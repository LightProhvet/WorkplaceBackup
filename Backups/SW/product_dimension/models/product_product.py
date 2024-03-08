# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

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

    lock_length = fields.Boolean(
        related='product_tmpl_id.lock_length')
    lock_height = fields.Boolean(
        related='product_tmpl_id.lock_height')
    lock_width = fields.Boolean(
        related='product_tmpl_id.lock_width')

    dimensional_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Dimensional UoM',
        related='product_tmpl_id.dimensional_uom_id',
        help='UoM for length, height, width')

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

    @api.model
    def _get_dimension_uom_domain(self):
        return [('category_id', '=', self.env.ref('uom.uom_categ_length').id)]

    @api.model
    def _calc_volume(self, product_length, product_height, product_width, uom_id):
        volume = 0
        if product_length and product_height and product_width and uom_id:
            length_m = self.convert_to_meters(product_length, uom_id)
            height_m = self.convert_to_meters(product_height, uom_id)
            width_m = self.convert_to_meters(product_width, uom_id)
            volume = length_m * height_m * width_m

        return volume

    @api.constrains('product_length', 'product_height', 'product_width', 'dimensional_uom_id')
    def constrains_calculate_volume(self):
        for record in self:
            record.volume = record._calc_volume(
                record.product_length,
                record.product_height,
                record.product_width,
                record.dimensional_uom_id,
            )

    def convert_to_meters(self, measure, dimensional_uom):
        if not measure or not dimensional_uom:
            return None
        uom_meters = self.env.ref('uom.product_uom_meter')

        return dimensional_uom._compute_quantity(qty=measure, to_unit=uom_meters, round=False)
