import time
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp
from lxml import etree

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    @api.depends('currency_id', 'company_id.currency_id')
    def _check_foreign_currency(self):
        self.foreign_currency = self.currency_id != self.company_id.currency_id
    
    rate_amount = fields.Monetary(string='Rate', readonly=True, states={'draft': [('readonly', False)]})
    foreign_currency = fields.Boolean(string='Foreign Currency', compute='_check_foreign_currency')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, related_sudo=False)

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        if self.foreign_currency and self.rate_amount:
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            invoice_currency = False
            if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
                # if all the invoices selected share the same currency, record the paiement in that currency too
                invoice_currency = self.invoice_ids[0].currency_id
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date,
                                                                               rate=self.rate_amount,
                                                                               currency_id=self.currency_id.id
                                                            ).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
    
            move = self.env['account.move'].create(self._get_move_vals())
    
            # Write line corresponding to invoice payment
            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
            counterpart_aml_dict.update({'currency_id': currency_id})
            counterpart_aml = aml_obj.create(counterpart_aml_dict)
    
            # Reconcile with the invoices
            if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
                # the writeoff debit and credit must be computed from the invoice residual in company currency
                # minus the payment amount in company currency, and not from the payment difference in the payment currency
                # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
                total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
                total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
                if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                    amount_wo = total_payment_company_signed - total_residual_company_signed
                else:
                    amount_wo = total_residual_company_signed - total_payment_company_signed
                # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
                # amount in the company currency
                if amount_wo > 0:
                    debit_wo = amount_wo
                    credit_wo = 0.0
                    amount_currency_wo = abs(amount_currency_wo)
                else:
                    debit_wo = 0.0
                    credit_wo = -amount_wo
                    amount_currency_wo = -abs(amount_currency_wo)
                writeoff_line['name'] = _('Counterpart')
                writeoff_line['account_id'] = self.writeoff_account_id.id
                writeoff_line['debit'] = debit_wo
                writeoff_line['credit'] = credit_wo
                writeoff_line['amount_currency'] = amount_currency_wo
                writeoff_line['currency_id'] = currency_id
                writeoff_line = aml_obj.create(writeoff_line)
                if counterpart_aml['debit']:
                    counterpart_aml['debit'] += credit_wo - debit_wo
                if counterpart_aml['credit']:
                    counterpart_aml['credit'] += debit_wo - credit_wo
                counterpart_aml['amount_currency'] -= amount_currency_wo
            self.invoice_ids.register_payment(counterpart_aml)
    
            # Write counterpart lines
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)
    
            move.post()
            return move
        else:
            return super(AccountPayment, self)._create_payment_entry(amount)
    
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.rate_amount = self.currency_id.rate_amount if self.currency_id else 0.0
        return {}
    
