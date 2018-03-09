from datetime import date
from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
# from odoo import http
from openerp.exceptions import UserError
import odoo.addons.decimal_precision as dp
# from openerp.tools.safe_eval import safe_eval as eval
# from openerp.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    oplos_code = fields.Many2one('product.product', string='Oplos Code')
    oplos_desc = fields.Char(string='Oplos Description')
    oplos_sale_price = fields.Float(string='Oplos Sale Price', digits=dp.get_precision('Product Price'))
