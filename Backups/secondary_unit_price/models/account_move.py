from odoo import api, fields, models, _, Command
from odoo.tools.misc import formatLang
import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "product.secondary.unit.mixin"]
    _name = "account.move.line"
    _secondary_unit_fields = {
        "qty_field": "quantity",
        "uom_field": "product_uom_id",
        "product_field": "product_id",
        'price_field': "price_unit",
    }

    price_unit = fields.Float(
        compute='_compute_price_unit',
        store=True,
        readonly=False,
        precompute=True,
    )
    # full redeclaration to make it precomputed for 'quantity'
    secondary_uom_qty = fields.Float(
        precompute=True,
        string="Secondary Qty",
        digits="Product Unit of Measure",
        store=True,
        readonly=False,
        compute="_compute_secondary_uom_qty",
        default=1)

    @api.depends("secondary_uom_price", "secondary_uom_id")
    def _compute_price_unit(self):
        if hasattr(super(), "_compute_price_unit"):
            super()._compute_price_unit()
        self._compute_helper_target_field_price()
