
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError

class Currency(models.Model):
    _inherit = "res.currency"

    @api.multi
    def _compute_current_rate(self):
        res = super(Currency, self)._compute_current_rate()
        if self._context.get('currency_id'):
            for currency in self.filtered(lambda r: r.id == self._context.get('currency_id')):
                currency.rate = self._context.get('rate')
        return res
    
    @api.model
    def _get_conversion_rate(self, from_currency, to_currency):
        from_currency = from_currency.with_env(self.env)
        to_currency = to_currency.with_env(self.env)
        if from_currency.rate == 0.0 or to_currency.rate == 0.0:
            raise UserError(_('Rate cannot be zero.'))
        res = super(Currency, self)._get_conversion_rate(from_currency, to_currency)
        return  from_currency.rate / to_currency.rate
    