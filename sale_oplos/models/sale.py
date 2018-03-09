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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    oplos = fields.Boolean(string='Oplos', readonly=True, states={'draft': [('readonly', False)]})
    
    @api.onchange('oplos')
    def _onchange_oplos(self):
        if self.oplos:
            if not self.product_id.oplos_code:
                raise UserError(_("This product doesn't has oplos product."))
            self.name = self.product_id.oplos_desc
            self.price_unit = self.product_id.oplos_sale_price
        return
    
    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_order_line_procurement(group_id)
        res['product_id'] = self.product_id.oplos_code.id if self.oplos and self.product_id.oplos_code \
            else self.product_id.id
        return res