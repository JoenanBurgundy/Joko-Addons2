from datetime import date
from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
# from odoo import http
# from openerp.exceptions import UserError
# from openerp.tools.safe_eval import safe_eval as eval
# from openerp.tools.translate import _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    last_received_value = fields.Float(string='Last Received Value', copy=False)
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        if self:
            for move in self.filtered(lambda r: r. product_id.type == 'product' and r. purchase_line_id):
                value = sum([quant.inventory_value for quant in move.quant_ids])
                move.purchase_line_id.last_received_value += value
        return res
        