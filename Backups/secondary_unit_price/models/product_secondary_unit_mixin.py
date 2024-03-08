# -*- coding: utf-8 -*-
from odoo import api, fields, models


# Core of the secondary unit prices.
class ProductSecondaryUnitMixin(models.AbstractModel):
    _inherit = "product.secondary.unit.mixin"

    # NB! WHEN ADDING MIXIN TO MODELS WITHOUT PRICE, YOU NEED TO REMOVE COMPUTE
    secondary_uom_price = fields.Float(
        string="Secondary Price",
        store=True,
        readonly=False,
        compute="_compute_secondary_uom_price",
        default=1,
        precompute=True)

    def _compute_helper_target_field_price(self):
        """Set the target price field defined in model"""
        for rec in self:
            if not self._secondary_unit_fields.get("price_field", False):
                continue
            if not rec.secondary_uom_id:
                rec[rec._secondary_unit_fields["price_field"]] = rec._origin[
                    rec._secondary_unit_fields["price_field"]
                ]
                continue
            if rec.secondary_uom_id.dependency_type == "independent":
                if rec[rec._secondary_unit_fields["price_field"]] == 0.0:
                    rec[rec._secondary_unit_fields["price_field"]] = 1.0
                continue

            # To avoid recompute secondary_uom_qty field when
            # secondary_uom_id changes.
            if not rec.secondary_uom_price:
                rec.env.remove_to_compute(
                    field=rec._fields["secondary_uom_price"], records=rec
                )
            primary_uom = rec._get_uom_line()
            # the math should be the same for the price, just the inverse (we swapped primary and secondary here)
            # But maybe we should make a separate function
            price_secondary_adjusted, price_primary_adjusted = rec.secondary_uom_id.convert_to_secondary_quantity(
                rec.secondary_uom_price, primary_uom
            )

            rec.update({
                rec._secondary_unit_fields["price_field"]: price_primary_adjusted,
                'secondary_uom_price': price_secondary_adjusted
            })

    def _get_price_from_line(self):
        if not self._secondary_unit_fields.get("price_field", False):
            return 0
        return self[self._secondary_unit_fields["price_field"]]

    @api.model
    def _get_secondary_uom_price_depends(self):
        if not self._secondary_unit_fields or not self._secondary_unit_fields.get("price_field", False):
            return []
        return [self._secondary_unit_fields["price_field"]]  # not factor?

    # Triggered when primary qty changed
    @api.depends(lambda x: x._get_secondary_uom_price_depends())
    def _compute_secondary_uom_price(self):
        if not self._secondary_unit_fields.get("price_field", False):
            return
        self.env.remove_to_compute(
            field=self._fields["secondary_uom_price"], records=self
        )
        for rec in self:
            if not rec.secondary_uom_id:
                rec.secondary_uom_price = 0.0
                continue
            elif rec.secondary_uom_id.dependency_type == "independent":
                continue

            qty_primary_unrounded = rec._get_quantity_from_line()
            primary_uom = rec._get_uom_line()  # defined in the original file

            price_primary_unrounded = rec._get_price_from_line()

            # the math should be the same for the price, just the inverse (we swapped primary and secondary here)
            # But maybe we should make a separate function
            price_secondary_adjusted, price_primary_adjusted = rec.secondary_uom_id.convert_from_secondary_quantity(
                price_primary_unrounded, primary_uom
        )
            rec.update({
                rec._secondary_unit_fields["price_field"]: price_primary_adjusted,
                'secondary_uom_price': price_secondary_adjusted
            })
