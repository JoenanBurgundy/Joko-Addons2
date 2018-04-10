
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.depends('currency_id', 'company_currency_id')
    def _check_foreign_currency(self):
        self.foreign_currency = self.currency_id != self.company_currency_id
    
    rate_amount = fields.Monetary(string='Rate', readonly=True, states={'draft': [('readonly', False)]})
    foreign_currency = fields.Boolean(string='Foreign Currency', compute='_check_foreign_currency')
    
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        self.currency_id = self.purchase_id.currency_id
        return super(AccountInvoice, self).purchase_order_change()
        
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        return {}
            
    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        if self.foreign_currency and self.rate_amount:
            total = 0
            total_currency = 0
            for line in invoice_move_lines:
                if self.currency_id != company_currency:
                    currency = self.currency_id.with_context(date=self._get_currency_rate_date() or fields.Date.context_today(self),
                                                             rate=self.rate_amount,
                                                             currency_id=self.currency_id.id)
                    if not (line.get('currency_id') and line.get('amount_currency')):
                        line['currency_id'] = currency.id
                        line['amount_currency'] = currency.round(line['price'])
                        line['price'] = currency.compute(line['price'], company_currency)
                else:
                    line['currency_id'] = False
                    line['amount_currency'] = False
                    line['price'] = self.currency_id.round(line['price'])
                if self.type in ('out_invoice', 'in_refund'):
                    total += line['price']
                    total_currency += line['amount_currency'] or line['price']
                    line['price'] = - line['price']
                else:
                    total -= line['price']
                    total_currency -= line['amount_currency'] or line['price']
            return total, total_currency, invoice_move_lines
        else:
            return super(AccountInvoice, self).compute_invoice_totals(company_currency, invoice_move_lines)
    
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.rate_amount = self.currency_id.rate if self.currency_id else 0.0
        return {}
