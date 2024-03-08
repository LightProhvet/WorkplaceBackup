from odoo import api, fields, models
from logging import getLogger

_logger = getLogger(__name__)


class MrpBom(models.Model):
    _inherit = ['mrp.bom', 'product.secondary.unit.mixin']
    _name = 'mrp.bom'
    _secondary_unit_fields = {
        'qty_field': 'product_qty',
        'uom_field': 'product_uom_id',
        "product_field": "product_id",
    }

    product_qty = fields.Float(
        compute='_compute_product_qty',
        copy=True,
        default=1.0,
        digits='Product Unit of Measure',
        readonly=False,
        required=True,
        store=True,
        string='Quantity',
        help='This should be the smallest quantity that this product can be produced in. If the BOM contains operations, make sure the work center capacity is accurate.')

    @api.depends('secondary_uom_qty', 'secondary_uom_id')
    def _compute_product_qty(self):
        if hasattr(super(), '_compute_product_qty'):
            super()._compute_product_qty()
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

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id:
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.secondary_uom_id:
                self.onchange_product_uom_id_for_secondary()
        return res


class MrpBomLine(models.Model):
    _inherit = ['mrp.bom.line', 'product.secondary.unit.mixin']
    _name = 'mrp.bom.line'
    _secondary_unit_fields = {
        'qty_field': 'product_qty',
        'uom_field': 'product_uom_id',
        "product_field": "product_id",
    }

    product_qty = fields.Float(
        compute='_compute_product_qty',
        copy=True,
        default=1.0,
        digits='Product Unit of Measure',
        readonly=False,
        required=True,
        store=True,
        string='Quantity',
        help='This should be the smallest quantity that this product can be produced in. If the BOM contains operations, make sure the work center capacity is accurate.')

    @api.depends('secondary_uom_qty', 'secondary_uom_id')
    def _compute_product_qty(self):
        if hasattr(super(), '_compute_product_qty'):
            super()._compute_product_qty()
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

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super().onchange_product_id()
        if self.product_id:
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.secondary_uom_id:
                self.onchange_product_uom_id_for_secondary()
                # self.secondary_uom_qty = 1.0
                # self.onchange_secondary_uom()
        return res


class MrpByProduct(models.Model):
    _inherit = ['mrp.bom.byproduct', 'product.secondary.unit.mixin']
    _name = 'mrp.bom.byproduct'
    _secondary_unit_fields = {
        'qty_field': 'product_qty',
        'uom_field': 'product_uom_id',
        "product_field": "product_id",
    }

    product_qty = fields.Float(
        compute='_compute_product_qty',
        copy=True,
        default=1.0,
        digits='Product Unit of Measure',
        readonly=False,
        required=True,
        store=True,
        string='Quantity',
        help='This should be the smallest quantity that this product can be produced in. If the BOM contains operations, make sure the work center capacity is accurate.')

    @api.depends('secondary_uom_qty', 'secondary_uom_id')
    def _compute_product_qty(self):
        _logger.warning(f'[MRP BYPROD] _compute_product_qty')
        if hasattr(super(), '_compute_product_qty'):
            super()._compute_product_qty()
        self._compute_helper_target_field_qty()

    @api.onchange('product_uom_id')
    def onchange_product_uom_id_for_secondary(self):
        _logger.warning(f'[MRP BYPROD] onchange_product_uom_id_for_secondary')
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange('secondary_uom_id')
    def onchange_product_secondary_uom(self):
        _logger.warning(f'[MRP BYPROD] onchange_product_secondary_uom')
        self.env.remove_to_compute(
            field=self._fields['product_qty'], records=self
        )
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        _logger.warning(f'[MRP BYPROD] _onchange_product_id')
        # res = super()._onchange_product_id()
        if self.product_id:
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.secondary_uom_id:
                self.onchange_product_uom_id_for_secondary()
        # return res
