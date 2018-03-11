from datetime import date
from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
# from odoo import http
from openerp.exceptions import UserError
# from openerp.tools.safe_eval import safe_eval as eval
# from openerp.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.model
    def invoice_line_move_line_get(self):
        product_obj = self.env['product.product']
        res = []
        total_last_value, value_to_inv = 0.0, 0.0
        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': line.purchase_line_id.last_received_value if line.purchase_line_id and line.purchase_line_id.last_received_value \
                    else line.price_subtotal,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
                'analytic_tag_ids': analytic_tag_ids
            }
            if line['account_analytic_id']:
                move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(move_line_dict)
            
            if line.purchase_line_id:
                total_last_value += line.purchase_line_id.last_received_value
                value_to_inv += line.price_subtotal if line.product_id.type == 'product' else 0
                line.purchase_line_id.last_received_value = 0
            
        # create write-off line
        diff = total_last_value - value_to_inv
        if diff:
            if not self.partner_id.diff_account_receivable or not self.partner_id.diff_account_payable:
                raise UserError(_('Please configure the default Difference Account on Partner.'))
            move_line_dict = {
                'type': 'src',
                'name': 'Price different',
                'price_unit': diff,
                'quantity': 1,
                'price': diff,
                'account_id': self.partner_id.diff_account_receivable.id if self.type in ('out_invoice', 'out_refund') \
                    else self.partner_id.diff_account_payable.id,
                'invoice_id': self.id,
                'analytic_tag_ids': analytic_tag_ids
            }
            res.append(move_line_dict)
        return res
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    diff_account_receivable = fields.Many2one('account.account', string='Difference Account Receivable')
    diff_account_payable = fields.Many2one('account.account', string='Difference Account Payable')
