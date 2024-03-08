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
    _inherit = ["product.custom.configurator.instance", "product.secondary.unit.mixin"]
    _name = "product.custom.configurator.instance"
    _secondary_unit_fields = {
        "price_field": "price_unit",
        "qty_field": "sol_uom_qty",
        "uom_field": "product_uom",
        "product_field": "product_id",
    }

    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_unit')

    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', default=_get_default_uom_id,)
    # secondary unit essential fields
    secondary_uom_qty = fields.Float()
    sol_uom_qty = fields.Float(compute='_compute_sol_uom_qty')
    price_unit = fields.Float(compute='_compute_price_unit')
    # extra secondary unit fields
    primary_product_sec_uom_quantity = fields.Float()
    total_cost_pp_sec_uom = fields.Float(string="Total Cost per Product", compute="calculate_costs_sec_unit")

    # sol_uom_qty = fields.Float(
    #     store=True, readonly=False, compute="_compute_sol_uom_qty", copy=True, precompute=True
    # )

    # price_unit = fields.Float(
    #     compute='_compute_price_unit',
    #     store=True,
    #     readonly=False)

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_sol_uom_qty(self):
        if hasattr(super(), "_compute_sol_uom_qty"):
            super()._compute_sol_uom_qty()
        self._compute_helper_target_field_qty()

    @api.onchange("product_uom_id")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("secondary_uom_id")
    def onchange_product_secondary_uom(self):
        self.env.remove_to_compute(
            field=self._fields["sol_uom_qty"], records=self
        )
        self._onchange_helper_product_uom_for_secondary()

    # IMPACTIC
    @api.depends("secondary_uom_price", "secondary_uom_id")
    def _compute_price_unit(self):
        if hasattr(super(), "_compute_price_unit"):
            super()._compute_price_unit()
        self._compute_helper_target_field_price()

    # TODO: alot
    def calculate_costs_sec_unit(self):
        pass


