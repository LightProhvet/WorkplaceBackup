from odoo import models, fields, api, _
from logging import getLogger

_logger = getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # product dimension
    product_length = fields.Float(
        string='Length (mm)')
    product_height = fields.Float(
        string='Thickness (mm)',
        related='product_tmpl_id.template_height',
        store=True,
        readonly=True)
    product_width = fields.Float(
        string='Width (mm)',
        related='product_tmpl_id.template_width',
        store=True,
        readonly=True)

    length = fields.Float(
        string='Length - DEPRECATED')
    width = fields.Float(
        string='Width - DEPRECATED')
    height = fields.Float(
        string='Height - DEPRECATED')
    diameter = fields.Float(
        string='Diameter - DEPRECATED')
    volume = fields.Float(
        string='Volume',
        compute='_compute_volume',
        store=True,
        readonly=True)

    # package dimension
    package_length = fields.Float(
        string='Package length')
    package_width = fields.Float(
        string='Package width')
    package_height = fields.Float(
        string='Package height')
    package_volume = fields.Float(
        string='Package volume',
        compute='_compute_package_volume',
        store=True,
        readonly=True)
    package_weight = fields.Float(
        string='Package weight',
        digits='Stock Weight')

    # bulk box dimension
    bulk_box_length = fields.Float(
        string='Bulk box length')
    bulk_box_width = fields.Float(
        string='Bulk box width')
    bulk_box_height = fields.Float(
        string='Bulk box height')
    bulk_box_volume = fields.Float(
        string='Bulk box volume',
        compute='_compute_bulk_box_volume',
        store=True,
        readonly=True)
    bulk_box_weight = fields.Float(
        string='Bulk box weight',
        digits='Stock Weight')

    # dimension lock options
    lock_length = fields.Boolean(
        related='product_tmpl_id.lock_length')
    lock_height = fields.Boolean(
        related='product_tmpl_id.lock_height')
    lock_width = fields.Boolean(
        related='product_tmpl_id.lock_width')

    dimensional_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Dimensional UoM',
        readonly=False,
        related='product_tmpl_id.dimensional_uom_id',
        help='UoM for length, height, width')

    dimension_uom_name = fields.Char(
        string='Dimension unit name',
        related='dimensional_uom_id.name',
        readonly=True)

    dimension_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Dimension unit - DEPRECATED',
        readonly=False,
        related='product_tmpl_id.dimension_uom_id',
        help='Dimension unit for length, width, height')

    # Product quantity inside the box
    quantity_in_bulk_box = fields.Float(
        string='Quantity in bulk box',
        default=1.0)

    # HUUM version of volume computation
    @api.depends('length', 'width', 'height', 'dimension_uom_id')
    def _compute_volume(self):
        for product in self:
            product.volume = self.env['product.template'].calc_volume(
                product.length, product.width, product.height, product.dimension_uom_id)

    # SW version of the same functionality
    @api.model
    def _calc_volume(self, product_length, product_height, product_width, uom_id):
        volume = 0
        if product_length and product_height and product_width and uom_id:
            length_m = self.convert_to_meters(product_length, uom_id)
            height_m = self.convert_to_meters(product_height, uom_id)
            width_m = self.convert_to_meters(product_width, uom_id)
            volume = length_m * height_m * width_m

        return volume

    @api.depends('package_length', 'package_width', 'package_height')
    def _compute_package_volume(self):
        for product in self:
            product.package_volume = self.env['product.template'].calc_volume(
                product.package_length, product.package_width,
                product.package_height, product.dimension_uom_id)

    @api.depends('bulk_box_length', 'bulk_box_width', 'bulk_box_height')
    def _compute_bulk_box_volume(self):
        for product in self:
            product.bulk_box_volume = self.env['product.template'].calc_volume(
                product.bulk_box_length, product.bulk_box_width,
                product.bulk_box_height, product.dimension_uom_id)

    @api.onchange('dimension_uom_id')
    def onchange_dimension_uom_id(self):
        product = self.env['product.template'].browse(
            self._context.get('active_id'))
        if self.is_product_variant:
            if self.dimension_uom_id != product.dimension_uom_id:
                return {
                    'warning': {
                        'title': _('Warning'),
                        'message': _(
                            'Upon saving this variant, uom (%s) will be set in all the variants of product (%s) and their volumes recalculated.'
                        ) % (self.dimension_uom_id.name, self.name)
                    }
                }

    # constrains functions
    @api.constrains('product_tmpl_id')
    def _constrains_product_tmpl_id(self):
        for record in self:
            template = record.product_tmpl_id
            vals = {}
            if template.lock_length:
                vals['product_length'] = template.template_length
            if template.lock_height:
                vals['product_height'] = template.template_height
            if template.lock_width:
                vals['product_width'] = template.template_width
            if vals:
                record.update(vals)

    @api.constrains('product_length', 'product_height', 'product_width', 'dimensional_uom_id')
    def constrains_calculate_volume(self):
        for record in self:
            record.volume = record._calc_volume(
                record.product_length,
                record.product_height,
                record.product_width,
                record.dimensional_uom_id,
            )

    @api.model
    def _get_dimension_uom_domain(self):
        return [('category_id', '=', self.env.ref('uom.uom_categ_length').id)]

    def convert_to_meters(self, measure, dimensional_uom):
        if not measure or not dimensional_uom:
            return None
        uom_meters = self.env.ref('uom.product_uom_meter')

        return dimensional_uom._compute_quantity(qty=measure, to_unit=uom_meters, round=False)
