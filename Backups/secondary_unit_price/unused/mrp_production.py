from odoo import api, fields, models
from logging import getLogger

_logger = getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'product.secondary.unit.mixin']
    _name = 'mrp.production'
    _secondary_unit_fields = {
        'qty_field': 'product_qty',
        'uom_field': 'product_uom_id',
        "product_field": "product_id",
    }

    product_qty = fields.Float(
        string='Quantity To Produce',
        default=1.0,
        digits='Product Unit of Measure',
        readonly=True,
        required=True,
        tracking=True,
        store=True,
        copy=True,
        compute='_compute_product_qty',
        states={'draft': [('readonly', False)]})

    @api.depends('secondary_uom_qty', 'secondary_uom_id')
    def _compute_product_qty(self):
        self._compute_helper_target_field_qty()

    @api.onchange('product_uom_id')
    def onchange_product_uom_id_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange('secondary_uom_id')
    def onchange_product_secondary_uom(self):
        self.env.remove_to_compute(
            field=self._fields['product_qty'], records=self
        )
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id:
            self.secondary_uom_id = self.product_id.mrp_secondary_uom_id
            if self.secondary_uom_id:
                self.onchange_product_uom_id_for_secondary()
        return res
