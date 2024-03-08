# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from logging import getLogger
from collections import Counter
import re

_logger = getLogger(__name__)


class ProductTemplateAttributes(models.Model):
    _name = "product.template.attributes"
    _description = "Product Configurator Template parameter system"
    _order = "sequence"

    _sql_constraints = [('field_value_unique', 'Check(1=1)', 'Type name already exists')]

    name = fields.Char('Name', translate=True)
    sequence = fields.Integer(string="Sequence value", index=True)
    template_id = fields.Many2one('product.configurator.templates')
    intersection_check = fields.Boolean(string=_('Tag intersection'), default=False)
    selectable_products = fields.Many2many('product.product', compute='_compute_selectable_products')

    default_float_value = fields.Float(string=_('Default Float'))
    tag_ids = fields.Many2many(string=_('Tag Filter'),
                               comodel_name='product.configurator.tag',
                               ondelete='cascade')
    preview_product = fields.Many2one('product.product', domain="[('id', 'in', selectable_products)]")
    type_name = fields.Many2one('template.type', string="Choose type")
    type_state = fields.Selection(related='type_name.state')
    field_value = fields.Char("Field value")
    quantity_formula = fields.Char("Quantity Formula")
    product_uom = fields.Many2one('uom.uom', domain="[('uom_type', '=', 'reference')]", string="Quantity Formula Unit of Measure")

    comments = fields.Char(string="Comments")

    efficiency = fields.Float(default=1.00)
    accessibility_condition = fields.Char(string="Accessibility condition")
    accessibility = fields.Selection(string="Accessibility", selection=[('1', 'Editable'), ('2', 'Read-only'), ('3', 'Hidden')])

    group_type = fields.Selection(string="Group", selection=[('dimensions', 'Dimensions'), ('locking', 'Locking'), ('properties', 'Properties'),
                                                             ('extras', 'Extras'), ('windows', 'Windows'), ('other', 'Other')])

    product = fields.Boolean(default=False)
    template_type_check = fields.Boolean(default=False)

    @api.depends('intersection_check', 'tag_ids')
    def _compute_selectable_products(self):
        for record in self:
            if not record.tag_ids:
                record.selectable_products = False
            # tags = self.env['product.tag'].search([('id', 'in', record.tag_ids)])
            products_union = self.env['product.product'].search([('tag_ids', 'in', record.tag_ids.ids)])
            intersection = []
            number_of_tags = 0
            for tag in record.tag_ids:
                number_of_tags += 1
                for product_id in tag.products:
                    intersection.append(product_id._origin.product_variant_id.id)
            counted = Counter(intersection)
            intersection_products = [el for el in intersection if counted[el] >= number_of_tags]
            if record.intersection_check and intersection_products:
                products_intersection = self.env['product.product'].search([('id', 'in', intersection_products)])
                record.selectable_products = products_intersection

            else:
                record.selectable_products = products_union

    @api.onchange('intersection_check')
    def _onchange_intersection_check(self):
        for record in self:
            record.preview_product = False

    @api.onchange('type_name')
    def _onchange_types(self):
        for record in self:
            if record.type_name.name == "Product":
                record.product = True
            else:
                record.product = False

            if record.type_name.state == "template":
                record.template_type_check = True
            else:
                record.template_type_check = False


class ProductConfiguratorTemplateType(models.Model):
    _name = "template.type"
    _description = "Product Configurator Template parameter type system"
    _sql_constraints = [('template_type_name_unique', 'unique(name)', 'Type name already exists')]

    name = fields.Char("Type Name", required='1')
    # state = fields.Selection([('modifier', 'Float Modifier'), ('pull', 'Pull'), ('push', 'Push'), ('template', 'Template')], string="Type")
    state = fields.Selection([('modifier', 'Float Modifier'), ('pull', 'Pull'), ('push', 'Push'), ('template', 'Template'), ('pull_modifier', 'Pull Modifier')], string="Type")
    target_parameter = fields.Char(readonly=True, states={'push': [('readonly', False)]}, placeholder="Target Parameter")
    target_template = fields.Many2one('product.configurator.templates', domain=[('template_check', '=', True)], readonly=True, states={'template': [('readonly', False)]})
    type_list = fields.One2many("template.type.list", "template_type_list")

    product_template_attributes_ids = fields.One2many('product.template.attributes', 'type_name')
    related_template_ids = fields.Many2many('product.configurator.templates', compute='_compute_templates')

    depend_parameters = fields.Many2many("product.template.attributes", compute='_compute_depend_parameters')

    # Change state and target template values inside type_list when changed within template type view.
    @api.onchange('target_template')
    def _onchange_template(self):
        for record in self:
            for type in record.type_list:
                type.template = self.target_template

    @api.onchange('state', 'type_list')
    def _onchange_states(self):
        for record in self:
            for type in record.type_list:
                type.state = record.state
            if record.target_template:
                for type in record.type_list:
                    type.template = record.target_template

    @api.depends('type_list')
    def _compute_depend_parameters(self):
        for record in self:
            if record.state not in ['pull', 'pull_modifier']:
                record.depend_parameters = False
                return
            elif record.related_template_ids:
                list_of_field_values = set([])
                list_of_attributes = []
                for line in record.type_list:
                    and_split = re.split(' AND | and ', line.condition)
                    for slice in and_split:
                        comparer = []
                        split = re.split('<=|>=|<|>|=', slice)
                        for equation in split:
                            if isinstance(equation, str):
                                list_of_field_values.add(equation.strip())

                for template in record.related_template_ids:
                    for parameter in template.attribute_line_ids:
                        if parameter.field_value in list_of_field_values:
                            list_of_attributes.append(parameter.id)
                record.depend_parameters = list_of_attributes
            else:
                record.depend_parameters = False

    @api.depends('product_template_attributes_ids')
    def _compute_templates(self):
        for record in self:
            # record.related_template_ids = [(6, 0, record.product_template_attributes_ids.ids)]
            templates = []
            for parameter in record.product_template_attributes_ids:
                templates.append(parameter.template_id.id)
            record.related_template_ids = [(6, 0, templates)]

    def show_test_wizard(self):
        self.ensure_one()
        environment_lines = [(5,)]
        duplicate_check = []
        for type_line in self.type_list:
            if type_line.condition:
                split = re.split('[+-/*=><,]| and | AND ', type_line.condition)
                new_list = []
                for string in split:
                    string = string.strip()
                    if string:
                        try:
                            int(string)
                        except ValueError:
                            if string not in duplicate_check:
                                duplicate_check.append(string)
                                data = {
                                    'name': string,
                                    'value': 0,
                                }
                                environment_lines.append((0, 0, data))
        template_test = self.name + " - Test Environment"
        # try:
        #     return {
        #         'name': template_test,
        #         'domain': [],
        #         'res_model': 'product.configurator.template.test',
        #         'type': 'ir.actions.act_window',
        #         'view_mode': 'form',
        #         'view_type': 'form',
        #         'target': 'new',
        #         'nodestroy': True,
        #         'view_id': self.env.ref("product_configurator.configurator_template_test_view").id,
        #         'context': {
        #             'default_template_type_id': self.id,
        #             'default_test_environment_values': environment_lines,
        #             # 'default_test_template_product_description': self.get_test_values_string(self.product_description),
        #             # 'default_test_price': int(self.eval_expr(self.get_test_values_float(self.price_formula))),
        #         },
        #     }
        # except:
        raise Warning('Incorrect info')


class TemplateTypeList(models.Model):
    _name = "template.type.list"
    _description = "Product Configurator parameter type rules system"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence value", index=True)
    new_type_name = fields.Char(readonly=True)
    name = fields.Char()
    state = fields.Selection([('modifier', 'Float Modifier'), ('pull', 'Pull'), ('push', 'Push'), ('template', 'Template'), ('pull_modifier', 'Pull Modifier')], string="Type")
    selectable_products = fields.Many2many('product.product', compute='_compute_selectable_products')

    condition = fields.Char()
    domain = fields.Char()
    tags = fields.Many2many(string=_('Tags'),
                               comodel_name='product.configurator.tag')
    preview_product = fields.Many2one('product.product', domain="[('id', 'in', selectable_products)]")
                               # domain="[('tag_ids', 'in', tags)]")
    modifier = fields.Float()
    intersection_check = fields.Boolean(string="Intersection")

    template = fields.Many2one('product.configurator.templates', readonly=True)
    relation = fields.Many2one('product.template.attributes', domain="[('template_id.id', '=', template)]")
    template_type_list = fields.Many2one("template.type", string=" ", readonly=True)
    float_modifier_select = fields.Many2one('template.type', string=" Float Mod.")
    comments = fields.Char(string=_("Comments"))

    @api.onchange('intersection_check')
    def _onchange_intersection_check(self):
        for record in self:
            record.preview_product = False

    @api.depends('intersection_check', 'tags')
    def _compute_selectable_products(self):
        for record in self:
            if not record.tags:
                record.selectable_products = False
            # tags = self.env['product.tag'].search([('id', 'in', record.tags)])
            products_union = self.env['product.product'].search([('tag_ids', 'in', record.tags.ids)])
            intersection = []
            number_of_tags = 0
            for tag in record.tags:
                number_of_tags += 1
                for product_id in tag.products:
                    intersection.append(product_id._origin.product_variant_id.id)
            counted = Counter(intersection)
            intersection_products = [el for el in intersection if counted[el] >= number_of_tags]
            if record.intersection_check and intersection_products:
                products_intersection = self.env['product.product'].search([('id', 'in', intersection_products)])
                record.selectable_products = products_intersection

            else:
                record.selectable_products = products_union
