# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line", "product.secondary.unit.mixin"]
    _name = "purchase.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_qty",
        "uom_field": "product_uom",
        "product_field": "product_id",
        "price_field": "price_unit",
    }

    price_unit = fields.Float(
        compute='_compute_price_unit',
        store=True,
        readonly=False)

    secondary_uom_price = fields.Float(precompute=False, compute="_compute_secondary_uom_price")


    @api.depends("secondary_uom_price", "secondary_uom_id")
    def _compute_price_unit(self):
        if hasattr(super(), "_compute_price_unit"):
            super()._compute_price_unit()
        self._compute_helper_target_field_price()
