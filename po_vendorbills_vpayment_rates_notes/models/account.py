import datetime
from datetime import date
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
from openerp.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
# from openerp.tools.safe_eval import safe_eval as eval
# from openerp.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.one
    @api.depends('currency_id')
    def _rate(self):
        for inv in self:
            if inv.state == 'draft':
                    inv.rate = inv.company_id.currency_id.rate / inv.currency_id.rate if inv.currency_id else 0
    
    rate = fields.Monetary(string='Rate', compute='_rate', store=True)
    note = fields.Text(string='Notes')

#     @api.multi
#     @api.onchange('currency_id')
#     def onchange_currency_id(self):
#         self.rate = self.company_id.currency_id.rate / self.currency_id.rate
#         return {}
    
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    @api.one
    @api.depends('currency_id')
    def _rate(self):
        for payment in self:
            if payment.state == 'draft':
                    payment.rate = payment.company_id.currency_id.rate / payment.currency_id.rate if payment.currency_id else 0
    
    rate = fields.Monetary(string='Rate', compute='_rate', store=True)
    note = fields.Text(string='Notes')

#     @api.multi
#     @api.onchange('currency_id')
#     def onchange_currency_id(self):
#         self.rate = self.company_id.currency_id.rate / self.currency_id.rate
#         return {}
