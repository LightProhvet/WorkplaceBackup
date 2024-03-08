# -*- coding: utf-8 -*-


from odoo import fields, models, api, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare
from odoo.tools.safe_eval import safe_eval, wrap_module
import ast
import collections


from logging import getLogger

_logger = getLogger(__name__)


class ProductCustomConfiguratorInstance(models.Model):
    _inherit = "product.custom.configurator.instance"
    _secondary_unit_fields = {
        "price_field": "price_unit",
        "qty_field": "sol_uom_qty",
        "uom_field": "product_uom",
        "product_field": "product_id",
    }
    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_unit')

    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', default=_get_default_uom_id,)
    sol_uom_qty = fields.Float(compute='_compute_sol_uom_qty')
    # secondary unit essential fields
    secondary_uom_qty = fields.Float(compute='_compute_secondary_uom_qty', readonly=False, store=True)
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Second unit",
        compute="compute_secondary_uom_id",
    )
    secondary_uom_price = fields.Float(
        string="Secondary Price",
        store=True,
        readonly=False,
        compute="calculate_sec_unit_values",
        default=0,
        # precompute=True # We don't need precompute as were not using configurator price as dependency
    )
    # extra secondary unit fields
    primary_product_sec_uom_quantity = fields.Float(compute="calculate_sec_unit_values",
                                                    # store=True,
                                                    digits='Product Unit of Measure',
                                                    )
    total_cost_pp_sec_uom = fields.Float(string="Total Cost per Second.", compute="calculate_sec_unit_values")

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_sol_uom_qty(self):
        if hasattr(super(), "_compute_sol_uom_qty"):
            super()._compute_sol_uom_qty()
        self._compute_helper_target_field_qty()

    @api.depends('sale_order_lines_linked')
    def compute_secondary_uom_id(self):
        for record in self:
            if record.sale_order_lines_linked:
                if len(record.sale_order_lines_linked) == 1:
                    record.secondary_uom_id = record.sale_order_lines_linked.secondary_uom_id
                # # if we allow the following 'else', we need to add writing secondary_unit to sol.
                # else:
                #     # take first? - the secondary_uom_id is readonly anyway
                #     for line in record.sale_order_lines_linked:
                #         record.secondary_uom_id = line.secondary_uom_id
                #         break
            else:
                record.secondary_uom_id = None

    @api.depends('sol_uom_qty', 'secondary_uom_qty', 'quantity', 'total_cost_pp', 'price_unit',
                 'input_ids', 'input_ids.input_float', 'input_ids.input_integer')  # helpers instead of input maybe?
    def calculate_sec_unit_values(self):
        """
        DO separately:
        sol_uom_qty = secondary_uom_qty,
        price_unit - secondary_uom_price
        """
        _logger.info(f"\n\n\nComputing for: {self}\n\n")
        for record in self:
            volume = False
            _logger.info(f"\n\n ref gives me: {self.env.ref('uom.product_uom_cubic_meter')} while i have {record.secondary_uom_id}")
            # We prefer helper as this changes on input change.
            for helper in record.helper_ids:
                # TODO: add more volume code possibilities
                if helper.code in ["VOLUME"]:
                    volume = helper.value_float
            if not volume and record.secondary_uom_id:  # and record.secondary_uom_id == self.env.ref('uom.product_uom_cubic_meter')
                volume = record.secondary_uom_qty/record.sol_uom_qty  # this may actually not be volume, but it doesn't matter

            elif record.secondary_uom_id:  # and record.secondary_uom_id == self.env.ref('uom.product_uom_cubic_meter'):
                # We want to totally invalidate secondary_uom_qty on sol_
                self.env.remove_to_compute(
                    field=self._fields["secondary_uom_qty"], records=self
                )
                record.secondary_uom_qty = record.sol_uom_qty*volume
            _logger.info(f"\n\n i have volume: {volume}")
            # get the real configurator
            ident = record.sale_order_lines_linked.product_configurator_instance_id.id
            real_object = self.env['product.custom.configurator.instance'].browse(ident)
            if volume:
                real_object.write({
                    'primary_product_sec_uom_quantity': record.quantity / volume,
                    'total_cost_pp_sec_uom': record.total_cost_pp / volume,
                    'secondary_uom_price': record.price_unit / volume,
                })
                _logger.info(F"\n\n{real_object} has price: {real_object.secondary_uom_price} and sec_qty: {real_object.primary_product_sec_uom_quantity}")

                # But we need to set for the temporary objects as well otherwise compute fails.
                record.primary_product_sec_uom_quantity = record.quantity / volume
                record.total_cost_pp_sec_uom = record.total_cost_pp / volume

                record.secondary_uom_price = record.price_unit / volume
            else:
                # we don't need to write anything really
                record.primary_product_sec_uom_quantity = None
                record.total_cost_pp_sec_uom = None

                record.secondary_uom_price = None

    # these functions were effectively on product_secondary_unit module's 'product.secondary.unit.mixin',
    # but as we don't link configurator with secondary unit (as there may be no product, we modify these a little)
    @api.depends('sol_uom_qty')
    def _compute_secondary_uom_qty(self):
        self.env.remove_to_compute(
            field=self._fields["secondary_uom_qty"], records=self
        )
        for rec in self:
            if not rec.secondary_uom_id:
                rec.secondary_uom_qty = 0.0
                continue
            elif rec.secondary_uom_id.dependency_type == "independent":
                continue

            qty_primary_unrounded = rec.sol_uom_qty
            primary_uom = rec.product_uom_id

            qty_primary_adjusted, qty_secondary_adjusted = rec.secondary_uom_id.convert_to_secondary_quantity(
                qty_primary_unrounded, primary_uom
            )
            _logger.info(f"\n\n DATA: {qty_primary_adjusted}, and {qty_secondary_adjusted}")
            rec.write({"sol_uom_qty": qty_primary_adjusted, "secondary_uom_qty": qty_secondary_adjusted})
            # normal set causes errors on " __set__ --> convert_to_write --> convert_to_cache --> v
            # value = float(value or 0.0) -- 'value' is tuple for some reason
            # rec.sol_uom_qty = qty_primary_adjusted,
            # rec.secondary_uom_qty = qty_secondary_adjusted

    def _compute_helper_target_field_qty(self):
        _logger.info("configurator compute_helper_target_field_qty")
        """Set the target qty field defined in model"""
        for rec in self:
            if not rec.secondary_uom_id:
                rec.secondary_uom_qty = rec.secondary_uom_qty
                continue
            if rec.secondary_uom_id.dependency_type == "independent":
                if rec.secondary_uom_qty == 0.0:
                    rec.secondary_uom_qty = 1.0
                continue

            # To avoid recompute secondary_uom_qty field when
            # secondary_uom_id changes.
            if not rec.secondary_uom_qty:
                rec.env.remove_to_compute(
                    field=rec._fields["secondary_uom_qty"], records=rec
                )

            primary_uom = rec.product_uom_id
            qty_primary_adjusted, qty_secondary_adjusted = rec.secondary_uom_id.convert_from_secondary_quantity(
                rec.secondary_uom_qty, primary_uom
            )

            rec.write({"sol_uom_qty": qty_primary_adjusted, "secondary_uom_qty": qty_secondary_adjusted})
