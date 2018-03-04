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


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    bank_proof = fields.Char(string='Proof of Bank')
