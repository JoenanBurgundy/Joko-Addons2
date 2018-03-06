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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.one
    @api.depends('currency_id')
    def _rate(self):
        for purchase in self:
            if purchase.state == 'draft':
                    purchase.rate = purchase.company_id.currency_id.rate / purchase.currency_id.rate if purchase.currency_id else 0
    
    rate = fields.Monetary(string='Rate', compute='_rate', store=True)

#     @api.multi
#     @api.onchange('currency_id')
#     def onchange_currency_id(self):
#         self.rate = self.company_id.currency_id.rate / self.currency_id.rate
#         return {}
