# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from logging import getLogger

_logger = getLogger(__name__)


class ProductConfiguratorTag(models.Model):
    _description = 'Product Tags'
    _name = "product.configurator.tag"
    _sql_constraints = [('tag_name_unique', 'unique(name)', 'Tag name already exists')]

    name = fields.Char('Tag Name', translate=True)
    active = fields.Boolean(help='The active field allows you to hide the tag without removing it.', default=True)
    products = fields.Many2many('product.template', string='Products')

    # @api.multi
    def name_get(self):
        res = {}
        for record in self:
            current = record
            name = current.name
            res[record.id] = name

        return [(record.id,  record.name) for record in self]

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     if name:
    #         name = name.split(' / ')[-1]
    #         args = [('name', operator, name)] + args
    #     tags = self.search(args, limit=limit)
    #     return tags.name_get()

    # @api.multi
    def write(self, vals):
        for record in self:
            for line in record.products:
                if not line.configurator_display_name:
                    line.configurator_display_name = line.name
        res = super(ProductConfiguratorTag, self).write(vals)
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # configurator_relation = fields.Many2one('product.configurator')
    # parent_configurator = fields.Many2one('product.configurator')
    # template_relation = fields.Many2one('product.configurator.templates')
    #
    # configurator_display_name = fields.Char('Display Name')
    # configurator_tag_display_name = fields.Char('Tag Display Name')

    # product_configurator_variant_id = fields.One2many('product.configurator.variant', 'product_template_id')

    # product_configurator_variant_target_parameter = fields.Many2many('product.template.attributes')
    # product_configurator_variant_target_parameter = fields.Char(string="Target Parameter")

    price_multiplier = fields.Float('Price Multiplier')
    tag_ids = fields.Many2many('product.configurator.tag', string='Tags')

    # inner_template = fields.Boolean(False)
    # separate_template = fields.Boolean(False)

    # standard_price_unit = fields.Many2one('uom.uom', string="Standard price unit", compute="_compute_price_per_unit")
    # standard_price_per_unit = fields.Monetary("Standard Price", compute="_compute_price_per_unit")

    configurator_check = fields.Boolean()

    # depth = fields.Float(string=_("Depth"))
    # width = fields.Float(string=_("Width"))
    # height = fields.Float(string=_("Height"))

    # Change Standard price per unit depending on products unit of measurement
    # @api.multi
    # @api.depends('uom_id', 'uom_po_id', 'list_price')
    # def _compute_price_per_unit(self):
    #     for record in self:
    #         if record.uom_id.uom_type == "reference":
    #             record.standard_price_unit = record.uom_id
    #             record.standard_price_per_unit = record.standard_price
    #         else:
    #             for uom in self.env['uom.uom'].search([('measure_type', '=', record.uom_id.measure_type)]):
    #                 if uom.uom_type == "reference":
    #                     record.standard_price_unit = uom
    #                 if record.uom_id.uom_type == "bigger":
    #                     record.standard_price_per_unit = record.standard_price / record.uom_id.factor_inv
    #                 elif record.uom_id.uom_type == "smaller":
    #                     record.standard_price_per_unit = record.standard_price * record.uom_id.factor


# class ProductConfiguratorVariants(models.Model):
#     _name = "product.configurator.variant"
#
#     product_template_id = fields.Many2one('product.template')
#     var_field_value = fields.Char(string="Field Value")
#     var_float_value = fields.Float(string="Float Value")
    # var_condition = fields.Char()
    # var_products = fields.Many2one('product.template')
    # var_tags = fields.Many2many('product.tag')
