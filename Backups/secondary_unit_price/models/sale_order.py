# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "price_field": "price_unit",  # We add price in secondary unit as well
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
        "product_field": "product_id",
    }

    # full redefinition. This field is from mixin, but needs to be precomputed now.
    secondary_uom_qty = fields.Float(
        string="Secondary Qty",
        digits="Product Unit of Measure",
        store=True,
        readonly=False,
        compute="_compute_secondary_uom_qty",
        precompute=True,
        default=1)

    product_uom_qty = fields.Float(
        store=True, readonly=False, compute="_compute_product_uom_qty", copy=True, precompute=True
    )

    price_unit = fields.Float(
        compute='_compute_price_unit',
        store=True,
        readonly=False)

    @api.depends("secondary_uom_price", "secondary_uom_id")
    def _compute_price_unit(self):
        if hasattr(super(), "_compute_price_unit"):
            super()._compute_price_unit()
        self._compute_helper_target_field_price()


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        invoices = super()._create_invoices(sale_orders)
        for invoice in invoices:
            invoice.invoice_line_ids._compute_secondary_uom_price()
        return invoices
