# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from logging import getLogger
import ast
import operator as op

_logger = getLogger(__name__)


class ProductTemplatePrice(models.Model):
    _name = "product.configurator.template.price"
    _description = "Product Configurator Template price system"
    _order = "sequence asc"

    name = fields.Char()
    template_price = fields.Many2one('product.configurator.templates')
    sequence = fields.Integer(string="Sequence value", index=True)
    control_formula = fields.Char(string="Control Formula")
    price_formula = fields.Char("Price Formula")
    comments = fields.Char(string="Comments")


class ProductTemplateRouting(models.Model):
    _name = "product.configurator.template.routing"
    _description = "Product Configurator Template routing system"
    _order = "sequence asc"

    name = fields.Char()
    template_routing = fields.Many2one('product.configurator.templates')
    # test_routing = fields.Many2one('product.configurator.templates.test')
    sequence = fields.Integer(string="Sequence value", index=True)
    control_formula = fields.Char(string="Control Formula")
    routing = fields.Many2one('mrp.routing.workcenter', 'Default routing', required=True, domain=[('auto_generate_check', '=', False)])
    duration = fields.Char(string="Duration", help="Time in minutes")
    comments = fields.Char(string="Comments")


class ProductConfiguratorTemplates(models.Model):
    _name = "product.configurator.templates"
    _description = 'Product Configurator Templates'
    _order = "name asc"

    name = fields.Char('Template Name')

    state = fields.Selection([
        ('draft', _('Draft')),
        ('confirmed', _('Confirmed')),
    ], default='draft')

    def draft(self):
        for record in self:
            record.write({'state': 'draft'})

    def confirm(self):
        for record in self:
            record.write({'state': 'confirmed'})

    conditional_price_check = fields.Boolean()
    template_check = fields.Boolean()

    configurator_name_generator = fields.Text(help="Type in the code for generating configurators based on this template. "
                                              "Use the set values in the field 'Name for using in generator' to add the fields product value, float value "
                                              "or text value. Use '.display_name' and '.tag_display_name' to use a products display name or the tag display name")
    example_product = fields.Many2one('product.product')

    product_name_generator = fields.Text(string=_('Product Name Generator'),
                                         help="Type in the code for generating configurator products based on this configurator. "
                                              "Use the set values in the field 'Name for using in generator' to add the fields product value, float value "
                                              "or text value. Use '.display_name' and '.tag_display_name' to use a products display name or the tag display name")

    product_description = fields.Text(string=_('Product Description'),
                                      help="The description for products created with this configurator.")

    produce_delay = fields.Float(
        'Manufacturing Lead Time', default=0.0,
        help="Average lead time in days to manufacture this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added.")

    attribute_line_ids = fields.One2many('product.template.attributes', 'template_id', string=_('Template lines'))
    conditional_price_formula = fields.One2many('product.configurator.template.price', 'template_price', string=_('Conditional Template Price'))
    conditional_routing_formula = fields.One2many('product.configurator.template.routing', 'template_routing', string=_('Conditional Template Routing'))
    template_file = fields.Many2many('ir.attachment', string='Attachments')
    template_configurator_id = fields.Many2one('product.configurator')
    price_formula = fields.Char("Price Formula", help="Use 'product_multiplier' to use the price multiplier of the set product.")

    new_type_name = fields.Many2one('template.type', domain=[('state', 'in', ['pull', 'push', 'modifier', 'template'])] ,string="New type name")


    # route_ids = fields.Many2many('stock.route', string=_('Routes'))
    categ_id = fields.Many2one('product.category', 'Product Category')

    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
                 ast.USub: op.neg}

    def copy(self, default=None):
        ctx = dict(self.env.context)

        conditional_price = [(5,)]
        conditional_routes = [(5,)]
        parameter_attributes = [(5,)]
        for line in self.conditional_price_formula:
            data = {
                'name': line.name,
                'template_price': line.template_price.id,
                'sequence': line.sequence,
                'control_formula': line.control_formula,
                'price_formula': line.price_formula,
            }
            conditional_price.append((0, 0, data))
        for line in self.conditional_routing_formula:
            data = {
                'name': line.name,
                'template_routing': line.template_routing.id,
                'test_routing': line.test_routing.id,
                'sequence': line.sequence,
                'control_formula': line.control_formula,
                'routing': line.routing.id,
                'duration': line.duration,

            }
            conditional_routes.append((0, 0, data))
        for line in self.attribute_line_ids:
            data = {
                'name': line.name,
                'sequence': line.sequence,
                'intersection_check': line.intersection_check,
                'selectable_products': line.selectable_products.ids,
                'default_float_value': line.default_float_value,
                'tag_ids': line.tag_ids.ids,
                'preview_product': line.preview_product.id,
                'type_name': line.type_name.id,
                'type_state': line.type_state,
                'field_value': line.field_value,
                'quantity_formula': line.quantity_formula,
                'product_uom': line.product_uom.id,
                'efficiency': line.efficiency,
                'accessibility_condition': line.accessibility_condition,
                'accessibility': line.accessibility,
                'product': line.product,
            }
            parameter_attributes.append((0, 0, data))

        # ctx.pop('default_product_id', None)
        self = self.with_context(ctx)

        new_po = super(ProductConfiguratorTemplates, self).copy(default=default)
        new_po.conditional_price_formula = conditional_price
        new_po.conditional_routing_formula = conditional_routes
        new_po.attribute_line_ids = parameter_attributes
        # for line in new_po.attribute_line_ids:
            # if line.product_id:
            #     seller = line.product_id._select_seller(
            #         partner_id=line.partner_id, quantity=line.product_qty,
            #         date=line.order_id.date_order and line.order_id.date_order.date(), uom_id=line.product_uom)
            #     line.date_planned = line._get_date_planned(seller)
        return new_po

    def get_test_values_string(self, string):
        for record in self:
            name_gen = string
            for parameter in record.attribute_line_ids:
                if parameter.field_value and parameter.field_value in name_gen:
                    # Find any uses of display names and tag display names in the generator code
                    tag_display_name = str(parameter.field_value) + ".tag_display_name"
                    display_name = str(parameter.field_value) + ".display_name"
                    value = str(parameter.field_value) + ".value"
                    depth = str(parameter.field_value) + ".depth"

                    # Replace parameter names and display names with respective code names
                    if parameter.type_name.name == "Product" and tag_display_name in name_gen:
                        name_gen = name_gen.replace(tag_display_name, parameter.preview_product.configurator_tag_display_name)
                    if parameter.type_name.name == "Product" and display_name in name_gen:
                        name_gen = name_gen.replace(display_name, parameter.preview_product.configurator_display_name)
                    if depth in name_gen:
                        name_gen = name_gen.replace(depth, str(parameter.preview_product.depth))
                    if value in name_gen:
                        name_gen = name_gen.replace(value, str(round(parameter.default_float_value, 2)))
                    if parameter.type_name.name == "Product":
                        name_gen = name_gen.replace(str(parameter.field_value), str(parameter.preview_product.name))
                    elif parameter.type_name.name in ["Float", "Height", "Width", "Depth"]:
                        name_gen = name_gen.replace(str(parameter.field_value), str(parameter.name))
                    elif parameter.type_name.name == "Text":
                        name_gen = name_gen.replace(str(parameter.field_value), "(Text Here)")
                    else:
                        name_gen = name_gen.replace(str(parameter.field_value), str(parameter.name))

            if "False" in name_gen:
                name_gen = name_gen.replace("False", "")
            if ".tag_display_name" in name_gen:
                name_gen = name_gen.replace(".tag_display_name", "")
            if ".display_name" in name_gen:
                name_gen = name_gen.replace(".display_name", "")
            return name_gen

    def get_test_values_float(self, string):
        for record in self:
            cost = 0
            for parameter in record.attribute_line_ids:
                cost_quantity = 0
                height = str(parameter.field_value) + ".height"
                width = str(parameter.field_value) + ".width"
                depth = str(parameter.field_value) + ".depth"
                product_quantity = str(parameter.field_value) + ".quantity"

                if isinstance(string, int):
                    return string

                if "$hourcost" in string or "$Hourcost" in string:
                    hour_cost = 0
                    for route in record.conditional_routing_formula:
                        # routing_workcenter = self.env['mrp.routing.workcenter'].search([('id', '=', route)])
                        hour_cost += route.routing.workcenter_id.costs_hour * int(record.eval_expr(record.get_test_values_float(route.duration))) / 60
                    string = string.replace("$hourcost", str(hour_cost))
                    string = string.replace("$Hourcost", str(hour_cost))

                if "$cost" in string or "$Cost" in string and parameter.type_name.name == "Product":
                    cost_quantity = record.field_value_to_float(parameter.quantity_formula)
                    try:
                        quantity = record.eval_expr(cost_quantity)
                        product_uom_ratio = parameter.preview_product.products.uom_id.factor_inv
                        cost_quantity = quantity / product_uom_ratio * parameter.efficiency
                    except:
                        cost_quantity = 0

                    cost += parameter.preview_product.standard_price * cost_quantity

                if product_quantity in string:
                    string = string.replace(product_quantity, str(record.get_test_values_float(parameter.quantity_formula)))

                if str(parameter.field_value) in string and (parameter.type_name.name in ['Float', 'Height', 'Width', 'Depth']):
                    string = string.replace(str(parameter.field_value), str(parameter.default_float_value))

                elif str(parameter.field_value) in string and (parameter.type_name.name == "Product"):
                    string = string.replace(str(parameter.field_value), str(parameter.preview_product.name))
                    # if height in string:
                    #     string = string.replace(height, str(parameter.preview_product.height))
                    # if width in string:
                    #     string = string.replace(width, str(parameter.preview_product.width))
                    # if depth in string:
                    #     string = string.replace(depth, str(parameter.preview_product.depth))
            string = string.replace("$cost", str(cost))
            string = string.replace("$Cost", str(cost))

            return string

    def eval_(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self.eval_(node.left), self.eval_(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self.eval_(node.operand))
        else:
            raise TypeError(node)

    def eval_expr(self, expr):
        return self.eval_(ast.parse(expr, mode='eval').body)
