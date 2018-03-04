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
    
    rate = fields.Float(string='Rate', states={'draft': [('readonly', False)]})
    note = fields.Text(string='Notes')

    @api.multi
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.rate = self.currency_id.rate
        return {}
    
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    rate = fields.Float(string='Rate', states={'draft': [('readonly', False)]})
    note = fields.Text(string='Notes')

    @api.multi
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.rate = self.currency_id.rate
        return {}
