# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_length = fields.Float(
        string='Length (mm)')
    template_height = fields.Float(
        string='Thickness (mm)')
    template_width = fields.Float(
        string='Width (mm)')

    lock_length = fields.Boolean(
        string='Lock Length?')
    lock_height = fields.Boolean(
        string='Lock Thickness?')
    lock_width = fields.Boolean(
        string='Lock Width?')

    # Use the same dimensional UoM on all product variants
    dimensional_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Dimensional UoM',
        domain=lambda self: self._get_dimension_uom_domain(),
        default=lambda self: self.env.ref('uom.product_uom_meter'),
        help='UoM for length, height, width')

    @api.model
    def _get_dimension_uom_domain(self):
        return [('category_id', '=', self.env.ref('uom.uom_categ_length').id)]

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
