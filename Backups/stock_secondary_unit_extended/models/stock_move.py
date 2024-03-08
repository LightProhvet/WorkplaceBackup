from odoo import api, fields, models
from odoo.tools.float_utils import float_round
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = ["stock.move", "product.secondary.unit.mixin"]
    _name = "stock.move"
    _secondary_unit_fields = {
        "uom_field": "product_uom",
        "product_field": "product_id",
        "qty_field": "product_uom_qty",  # OCA defined. Shows RESERVED QUANTITY
        "qty_field_done": "quantity_done",  # compute causes problems on installation. Upgrade and usage works fine.
        # "qty_field_real": "product_qty", # odoo doesn't like this field. I got the error "use product_uom_qty instead"
    }  # TODO: Add: availabilty, product_virtual_available, reserved_availability, should_consume_qty

    product_uom_qty = fields.Float(
        store=True, readonly=False, compute="_compute_product_uom_qty", copy=True
    )
    quantity_done = fields.Float(
        store=True, readonly=False,
        compute="_compute_quantity_done",
        copy=True
    )
    # This should be in the secondary_unit_mixin
    secondary_uom_qty_done = fields.Float(
        string="Secondary Done Qty",
        digits="Product Unit of Measure",
        store=True,
        readonly=False,
        compute="_compute_secondary_uom_qty_done",
        default=1)

    # product_qty = fields.Float(
    #     store=True, readonly=False,
    #     compute="_compute_product_qty",
    #     copy=True
    # )
    #
    # secondary_uom_qty_real = fields.Float(
    #     string="Secondary Real Qty",
    #     digits="Product Unit of Measure",
    #     store=True,
    #     readonly=False,
    #     compute="_compute_secondary_uom_qty_real",
    #     default=1)

    # @api.onchange("secondary_uom_id")
    # def onchange_product_secondary_uom(self):
    #     self.env.remove_to_compute(
    #         field=self._fields["product_uom_qty"], records=self
    #     )
    #     self._onchange_helper_product_uom_for_secondary()

    def _merge_moves_fields(self):
        res = super()._merge_moves_fields()
        res["secondary_uom_qty_done"] = sum(self.mapped("secondary_uom_qty_done"))
        return res

    # TODO: _split for qty done?

    # This should be in the secondary_unit_mixin
    def _get_qty_done_line(self):
        _logger.info("_get_qty_done_line")
        return self[self._secondary_unit_fields["qty_field_done"]]

    # This should be in the secondary_unit_mixin
    def _compute_helper_target_field_qty_done(self):
        _logger.info("_compute_helper_target_field_qty_done")
        """Set the target quantity_done field defined in model"""
        for rec in self.filtered(lambda sm: sm.state != "cancel"):
            if not rec.secondary_uom_id:
                rec[rec._secondary_unit_fields["qty_field_done"]] = rec._origin[
                    rec._secondary_unit_fields["qty_field_done"]
                ]
                continue
            if rec.secondary_uom_id.dependency_type == "independent":
                if rec[rec._secondary_unit_fields["qty_field_done"]] == 0.0:
                    rec[rec._secondary_unit_fields["qty_field_done"]] = 1.0
                continue

            # To avoid recompute secondary_uom_qty field when
            # secondary_uom_id changes.
            if not rec.secondary_uom_qty_done:
                rec.env.remove_to_compute(
                    field=rec._fields["secondary_uom_qty_done"], records=rec
                )
            primary_uom = rec._get_uom_line()
            qty_primary_adjusted, qty_secondary_adjusted = rec.secondary_uom_id.convert_from_secondary_quantity(
                rec.secondary_uom_qty_done, primary_uom
            )

            rec.update({
                rec._secondary_unit_fields["qty_field_done"]: qty_primary_adjusted,
                'secondary_uom_qty_done': qty_secondary_adjusted
            })

    # This should be in the secondary_unit_mixin
    @api.model
    def _get_secondary_uom_qty_done_depends(self):
        _logger.info("_get_secondary_uom_qty_done_depends")
        if not self._secondary_unit_fields:
            return []
        return [self._secondary_unit_fields["qty_field_done"]]

    # This should be in the secondary_unit_mixin
    # Triggered when qty_done changed
    @api.depends(lambda x: x._get_secondary_uom_qty_done_depends())
    def _compute_secondary_uom_qty_done(self):
        _logger.info("\n\n\n_compute_secondary_uom_qty_done")
        self.env.remove_to_compute(
            field=self._fields["secondary_uom_qty_done"], records=self
        )
        for rec in self.filtered(lambda sm: sm.state != "cancel"):
            if not rec.secondary_uom_id:
                rec.secondary_uom_qty_done = 0.0
                continue
            elif rec.secondary_uom_id.dependency_type == "independent":
                continue

            # because the first remove just isn't enough.
            self.env.remove_to_compute(
                field=self._fields["secondary_uom_qty_done"], records=rec
            )

            qty_primary_unrounded = rec.quantity_done
            primary_uom = rec._get_uom_line()

            qty_primary_adjusted, qty_secondary_adjusted = rec.secondary_uom_id.convert_to_secondary_quantity(
                qty_primary_unrounded, primary_uom
            )
            rec.secondary_uom_qty_done = qty_secondary_adjusted
            rec.quantity_done = qty_primary_adjusted
            rec._secondary_unit_fields["qty_field_done"] = qty_primary_adjusted,

    # This should be in this model originally (according to OCA)
    @api.depends("secondary_uom_qty_done", "secondary_uom_id")
    def _compute_quantity_done(self):
        if hasattr(super(), "_compute_quantity_done"):
            super()._compute_quantity_done()
        self._compute_helper_target_field_qty_done()
#
# # everything needed for product_qty secondary unit (secondary_qty_real)
#     # This should be in the secondary_unit_mixin
#     def _get_qty_real_line(self):
#         return self[self._secondary_unit_fields["qty_field_real"]]
#
#     # This should be in the secondary_unit_mixin
#     def _compute_helper_target_field_qty_real(self):
#         """Set the target product_qty field defined in model"""
#         for rec in self.filtered(lambda sm: sm.state != "cancel"):
#             if not rec.secondary_uom_id:
#                 rec[rec._secondary_unit_fields["qty_field_real"]] = rec._origin[
#                     rec._secondary_unit_fields["qty_field_real"]
#                 ]
#                 continue
#             if rec.secondary_uom_id.dependency_type == "independent":
#                 if rec[rec._secondary_unit_fields["qty_field_real"]] == 0.0:
#                     rec[rec._secondary_unit_fields["qty_field_real"]] = 1.0
#                 continue
#
#             # To avoid recompute secondary_uom_qty field when
#             # secondary_uom_id changes.
#             if not rec.secondary_uom_qty_real:
#                 rec.env.remove_to_compute(
#                     field=rec._fields["secondary_uom_qty_real"], records=rec
#                 )
#             primary_uom = rec._get_uom_line()
#             qty_primary_adjusted, qty_secondary_adjusted = rec.secondary_uom_id.convert_from_secondary_quantity(
#                 rec.secondary_uom_qty_real, primary_uom
#             )
#
#             rec.update({
#                 rec._secondary_unit_fields["qty_field_real"]: qty_primary_adjusted,
#                 'secondary_uom_qty_real': qty_secondary_adjusted
#             })
#
#     # This should be in the secondary_unit_mixin
#     @api.model
#     def _get_secondary_uom_qty_real_depends(self):
#         if not self._secondary_unit_fields:
#             return []
#         return [self._secondary_unit_fields["qty_field_real"]]
#
#     # This should be in the secondary_unit_mixin
#     # Triggered when qty_done changed
#     @api.depends(lambda x: x._get_secondary_uom_qty_real_depends())
#     def _compute_secondary_uom_qty_real(self):
#         self.env.remove_to_compute(
#             field=self._fields["secondary_uom_qty_real"], records=self
#         )
#         for rec in self.filtered(lambda sm: sm.state != "cancel"):
#             if not rec.secondary_uom_id:
#                 rec.secondary_uom_qty_real = 0.0
#                 continue
#             elif rec.secondary_uom_id.dependency_type == "independent":
#                 continue
#
#             qty_primary_unrounded = rec._get_qty_real_line()
#             primary_uom = rec._get_uom_line()
#
#             qty_primary_adjusted, qty_secondary_adjusted = rec.secondary_uom_id.convert_to_secondary_quantity(
#                 qty_primary_unrounded, primary_uom
#             )
#
#             rec.update({
#                 rec._secondary_unit_fields["qty_field_real"]: qty_primary_adjusted,
#                 'secondary_uom_qty_real': qty_secondary_adjusted
#             })
#
#     # This should be in this model originally (according to OCA)
#     @api.depends("secondary_uom_qty_real", "secondary_uom_id")
#     def _compute_product_qty(self):
#         if hasattr(super(), "_compute_product_qty"):
#             super()._compute_product_qty()
#         self._compute_helper_target_field_qty_real()

