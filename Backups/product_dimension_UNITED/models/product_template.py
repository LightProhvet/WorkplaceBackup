from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_length = fields.Float(
        string='Length')
    template_height = fields.Float(
        string='Thickness')
    template_width = fields.Float(
        string='Width')

    length = fields.Float(
        string='Length - DEPRECATED',
        compute='_compute_length',
        inverse='_set_length',
        store=True)
    width = fields.Float(
        string='Width - DEPRECATED',
        compute='_compute_width',
        inverse='_set_width',
        store=True)
    height = fields.Float(
        string='Height - DEPRECATED',
        compute='_compute_height',
        inverse='_set_height',
        store=True)
    diameter = fields.Float(
        string='Diameter - DEPRECATED')
    volume = fields.Float(
        string='Volume - DEPRECATED',
        compute='_compute_volume',
        store=False,
        readonly=True,
        digits='Volume')

    package_length = fields.Float(
        string='Package length',
        compute='_compute_package_length',
        inverse='_set_package_length',
        store=True)
    package_width = fields.Float(
        string='Package width',
        compute='_compute_package_width',
        inverse='_set_package_width',
        store=True)
    package_height = fields.Float(
        string='Package height',
        compute='_compute_package_height',
        inverse='_set_package_height',
        store=True)
    package_volume = fields.Float(
        string='Package volume',
        compute='_compute_package_volume',
        store=False,
        readonly=True,
        digits='Volume')
    package_weight = fields.Float(
        string='Package weight',
        compute='_compute_package_weight',
        digits='Stock Weight',
        inverse='_set_package_weight',
        store=True)

    bulk_box_length = fields.Float(
        string='Bulk box length',
        compute='_compute_bulk_box_length',
        inverse='_set_bulk_box_length',
        store=True)
    bulk_box_width = fields.Float(
        string='Bulk box width',
        compute='_compute_bulk_box_width',
        inverse='_set_bulk_box_width',
        store=True)
    bulk_box_height = fields.Float(
        string='Bulk box height',
        compute='_compute_bulk_box_height',
        inverse='_set_bulk_box_height',
        store=True)
    bulk_box_volume = fields.Float(
        string='Bulk box volume',
        compute='_compute_bulk_box_volume',
        store=True,
        readonly=True,
        digits='Volume')
    bulk_box_weight = fields.Float(
        string='Bulk box weight',
        compute='_compute_bulk_box_weight',
        digits='Stock Weight',
        inverse='_set_bulk_box_weight',
        store=True)

    # Use the same dimensional UoM on all product variants
    dimensional_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Dimensional UoM',
        domain=lambda self: self._get_dimension_uom_domain(),
        default=lambda self: self.env.ref('uom.product_uom_meter'),
        help='UoM for length, height, width')

    dimension_uom_name = fields.Char(
        string='Dimension unit name',
        related='dimensional_uom_id.name',
        readonly=True)

    dimension_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Dimension unit - DEPRECATED',
        domain=lambda self: self._get_dimension_uom_domain(),
        default=lambda self: self._get_dimension_uom_default().id, ondelete='restrict',
        help='Dimension unit for length, width, height')


    # Dimension lock fields
    lock_length = fields.Boolean(
        string='Lock Length?')
    lock_height = fields.Boolean(
        string='Lock Thickness?')
    lock_width = fields.Boolean(
        string='Lock Width?')

    # Product quantity inside the box
    quantity_in_bulk_box = fields.Float(
        string='Quantity in bulk box', default=1.0)

    def _compute_dimension(self, dimension_id):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template[dimension_id] = template.product_variant_ids[dimension_id]
        for template in (self - unique_variants):
            template[dimension_id] = 0.0

    def _set_dimension(self, dimension_id):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids[dimension_id] = template[dimension_id]

    def _convert_dimension(self, value, from_unit, to_unit):
        return from_unit._compute_quantity(qty=value, to_unit=to_unit, round=False)

    @api.depends("length", "width", "height", "dimension_uom_id")
    def calc_volume(self, length, width, height, dimension_uom_id):
        to_unit = self._get_dimension_uom_default()
        volume = 0
        if length and width and height:
            volume = self._convert_dimension(length, dimension_uom_id, to_unit) * \
                self._convert_dimension(width, dimension_uom_id, to_unit) * \
                self._convert_dimension(height, dimension_uom_id, to_unit)
        return volume

    @api.depends('product_variant_ids', 'product_variant_ids.length')
    def _compute_length(self):
        self._compute_dimension('length')

    def _set_length(self):
        self._set_dimension('length')

    @api.depends('product_variant_ids', 'product_variant_ids.width')
    def _compute_width(self):
        self._compute_dimension('width')

    def _set_width(self):
        self._set_dimension('width')

    @api.depends('product_variant_ids', 'product_variant_ids.height')
    def _compute_height(self):
        self._compute_dimension('height')

    def _set_height(self):
        self._set_dimension('height')

    @api.depends('length', 'width', 'height', 'dimension_uom_id')
    def _compute_volume(self):
        for product in self:
            product.volume = self.calc_volume(
                product.length, product.width, product.height, product.dimension_uom_id)

    @api.depends('product_variant_ids', 'product_variant_ids.package_length')
    def _compute_package_length(self):
        self._compute_dimension('package_length')

    def _set_package_length(self):
        self._set_dimension('package_length')

    @api.depends('product_variant_ids', 'product_variant_ids.package_width')
    def _compute_package_width(self):
        self._compute_dimension('package_width')

    def _set_package_width(self):
        self._set_dimension('package_width')

    @api.depends('product_variant_ids', 'product_variant_ids.package_height')
    def _compute_package_height(self):
        self._compute_dimension('package_height')

    def _set_package_height(self):
        self._set_dimension('package_height')

    @api.depends('package_length', 'package_width', 'package_height', 'dimension_uom_id')
    def _compute_package_volume(self):
        for product in self:
            product.package_volume = self.calc_volume(
                product.package_length, product.package_width,
                product.package_height, product.dimension_uom_id)

    @api.depends('product_variant_ids', 'product_variant_ids.package_weight')
    def _compute_package_weight(self):
        self._compute_dimension('package_weight')

    def _set_package_weight(self):
        self._set_dimension('package_weight')

    @api.depends('product_variant_ids', 'product_variant_ids.bulk_box_length')
    def _compute_bulk_box_length(self):
        self._compute_dimension('bulk_box_length')

    def _set_bulk_box_length(self):
        self._set_dimension('bulk_box_length')

    @api.depends('product_variant_ids', 'product_variant_ids.bulk_box_width')
    def _compute_bulk_box_width(self):
        self._compute_dimension('bulk_box_width')

    def _set_bulk_box_width(self):
        self._set_dimension('bulk_box_width')

    @api.depends('product_variant_ids', 'product_variant_ids.bulk_box_height')
    def _compute_bulk_box_height(self):
        self._compute_dimension('bulk_box_height')

    def _set_bulk_box_height(self):
        self._set_dimension('bulk_box_height')

    @api.depends('bulk_box_length', 'bulk_box_width', 'bulk_box_height', 'dimension_uom_id')
    def _compute_bulk_box_volume(self):
        for product in self:
            product.bulk_box_volume = self.calc_volume(
                product.bulk_box_length, product.bulk_box_width,
                product.bulk_box_height, product.dimension_uom_id)

    @api.depends('product_variant_ids', 'product_variant_ids.bulk_box_weight')
    def _compute_bulk_box_weight(self):
        self._compute_dimension('bulk_box_weight')

    def _set_bulk_box_weight(self):
        self._set_dimension('bulk_box_weight')

    def _get_dimension_uom_domain(self):
        return [
            ('category_id', '=', self.env.ref('uom.uom_categ_length').id)
        ]

    @api.model
    def _get_dimension_uom_default(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        if get_param('product.dimension_in_foot') == '1':
            return self.env.ref('uom.product_uom_foot')
        elif get_param('product.dimension_in_foot') == '2':
            return self.env.ref('uom.product_uom_cm')
        else:
            return self.env.ref('uom.product_uom_meter')

    @api.model_create_multi
    def create(self, values_list):
        templates = super(ProductTemplate, self).create(values_list)

        dimension_fields = [
            'length', 'width', 'height',
            'package_length', 'package_width', 'package_height', 'package_volume', 'package_weight',
            'bulk_box_length', 'bulk_box_width', 'bulk_box_height', 'bulk_box_volume',
            'bulk_box_weight']
        # This is needed to set given values to first variant after creation
        for template, values in zip(templates, values_list):
            related_values = {}

            for dimension_field in dimension_fields:
                if values.get(dimension_field):
                    related_values[dimension_field] = values[dimension_field]

            if related_values:
                template.write(related_values)

        return templates

    @api.model
    def _get_volume_uom_name_from_ir_config_parameter(self):
        """ Get the unit of measure to interpret the `volume` field. By default, we consider
        that volumes are expressed in cubic meters. Users can configure to express them in cubic feet
        by adding an ir.config_parameter record with "product.volume_in_cubic_feet" as key
        and "1" as value.
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        product_volume_in_cubic_feet_param = get_param(
            'product.dimension_in_foot')
        if product_volume_in_cubic_feet_param == '1':
            return "ft³"
        elif product_volume_in_cubic_feet_param == '2':
            return "cm³"
        else:
            return "m³"

    @api.model
    def _get_weight_uom_id_from_ir_config_parameter(self):
        """ Get the unit of measure to interpret the `weight` field. By default, we considerer
        that weights are expressed in kilograms. Users can configure to express them in pounds
        by adding an ir.config_parameter record with "product.product_weight_in_lbs" as key
        and "1" as value.
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        product_weight_in_lbs_param = get_param('product.weight_in_lbs')
        if product_weight_in_lbs_param == '1':
            return self.env.ref('uom.product_uom_lb')
        elif product_weight_in_lbs_param == '2':
            return self.env.ref('uom.product_uom_gram')
        else:
            return self.env.ref('uom.product_uom_kgm')

    def convert_to_meters(self, measure, dimensional_uom):
        uom_meters = self.env.ref('uom.product_uom_meter')

        return dimensional_uom._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )

    @api.constrains(
        'template_length', 'lock_length', 'template_height', 'lock_height', 'template_width',
        'lock_width')
    def _constrains_template_dimensions(self):
        for record in self:
            vals = {}
            if record.lock_length:
                vals['product_length'] = record.template_length
            if record.lock_height:
                vals['product_height'] = record.template_height
            if record.lock_width:
                vals['product_width'] = record.template_width
            if vals:
                record.product_variant_ids.update(vals)

    # @api.model
    # def _calc_volume(self, product_length, product_height, product_width, uom_id):
    #     volume = 0
    #     if product_length and product_height and product_width and uom_id:
    #         length_m = self.convert_to_meters(product_length, uom_id)
    #         height_m = self.convert_to_meters(product_height, uom_id)
    #         width_m = self.convert_to_meters(product_width, uom_id)
    #         volume = length_m * height_m * width_m
    #     return volume

    # @api.onchange('product_length', 'product_height', 'product_width', 'dimensional_uom_id')
    # def onchange_calculate_volume(self):
    #     self.volume = self._calc_volume(
    #         self.product_length,
    #         self.product_height,
    #         self.product_width,
    #         self.dimensional_uom_id)

    # def convert_to_meters(self, measure, dimensional_uom):
    #     uom_meters = self.env.ref('uom.product_uom_meter')
    #     return dimensional_uom._compute_quantity(qty=measure, to_unit=uom_meters, round=False)