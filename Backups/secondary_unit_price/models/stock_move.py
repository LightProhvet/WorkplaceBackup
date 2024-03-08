# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockMove(models.Model):
    _inherit = ["stock.move", "product.secondary.unit.mixin"]
    _name = "stock.move"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
        "product_field": "product_id",
        "price_field": "price_unit"
    }

    price_unit = fields.Float(
        compute='_compute_price_unit',
        store=True,
        readonly=False)

    secondary_uom_price = fields.Float(precompute=False, compute='_compute_secondary_uom_price')

    @api.depends("secondary_uom_price", "secondary_uom_id")
    def _compute_price_unit(self):
        if hasattr(super(), "_compute_price_unit"):
            super()._compute_price_unit()
        self._compute_helper_target_field_price()


class StockMoveLine(models.Model):
    _inherit = ["stock.move.line", "product.secondary.unit.mixin"]
    _name = "stock.move.line"
    _secondary_unit_fields = {
        "qty_field": "qty_done",
        "uom_field": "product_uom_id",
        "product_field": "product_id",
        "price_field": "",  # there is no price on sml, so we remove price compute as well.
    }

    secondary_uom_price = fields.Float(
        string="Secondary Price - disabled",
        store=False,
        readonly=True,
        compute=False,
        default=None)
