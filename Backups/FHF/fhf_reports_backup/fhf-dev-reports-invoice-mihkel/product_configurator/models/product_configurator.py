# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from logging import getLogger
import re
import ast
import operator as op
import json
from collections import Counter
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = getLogger(__name__)


class ProductConfigurator(models.Model):
    _name = "product.configurator"
    _description = "Product Configurator system"
    _order = "id desc"

    order_id = fields.Many2one('sale.order')
    template_name = fields.Many2one('product.configurator.templates', string=_('Choose a template'), domain=[('state', '=', 'confirmed')])
    name = fields.Char('Configurator Name')
    duplicate_configurator = fields.Many2one('product.configurator',
                                             domain="[('template_name', '=', template_name)]",
                                             string=_('Choose a configurator to duplicate'))
    configurator_product_description = fields.Char(string="Description")
    template_parameters = fields.One2many('product.configurator.list', 'parameter_line', copy=True)
    template_parameters_push = fields.One2many('product.configurator.list.push', 'parameter_line', compute="_compute_push")

    # template_parameters_push = fields.One2many('product.configurator.list.push', 'parameter_line')

    name_seq = fields.Char(string='Product Configurator', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    routing = fields.Char('Routing')
    default_code = fields.Char(string='Default Code')
    discount = fields.Float(string="Discount: ", default=0)
    quantity = fields.Integer(string="Quantity: ", default=1)

    configurator_file = fields.Many2many('ir.attachment', string='Attachments')

    calculate = fields.Boolean(default=False)
    calculate_price = fields.Float(string="Price: ")
    calculate_cost = fields.Float(string="Cost: ")
    calculate_margin = fields.Float(string="Margin: ")
    calculate_margin_multiplier = fields.Float(string="Margin multiplier: ")

    check = fields.Boolean(default=False)

    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
                 ast.USub: op.neg}

    # eval to calculate equations to numerical values
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

    # calculate string based field values to numerical values set in configurator via field_value fields
    def field_value_to_float(self, string):
        for record in self:
            for parameter in record.template_name.attribute_line_ids:
                height = str(parameter.field_value) + ".height"
                width = str(parameter.field_value) + ".width"
                depth = str(parameter.field_value) + ".depth"
                weight_per_area = str(parameter.field_value) + ".weight_per_area"
                product_quantity = str(parameter.field_value) + ".quantity"
                if isinstance(string, int):
                    return string
                # Add specific string values here to be calculated based on rules like $cost and $hourcost
                if "$hourcost" in string or "$Hourcost" in string:
                    cost = 0
                    for route in ast.literal_eval(record.routing).keys():
                        routing_workcenter = self.env['mrp.routing.workcenter'].search([('id', '=', route)])
                        cost += routing_workcenter.workcenter_id.costs_hour * int(ast.literal_eval(record.routing)[route]) / 60
                    string = string.replace("$hourcost", str(cost))
                    string = string.replace("$Hourcost", str(cost))

                if "$cost" in string or "$Cost" in string:
                    cost = 0
                    cost_quantity = 0
                    for field in record.template_parameters:
                        if field.products:
                            for parameter in record.template_name.attribute_line_ids:
                                if parameter.field_value == field.field_value:
                                    cost_quantity = record.field_value_to_float(parameter.quantity_formula)
                                    try:
                                        quantity = record.eval_expr(cost_quantity)
                                        product_uom_ratio = field.products.uom_id.factor_inv
                                        cost_quantity = quantity / product_uom_ratio * parameter.efficiency
                                    except:
                                        cost_quantity = 0
                            cost += field.products.standard_price * cost_quantity
                    string = string.replace("$cost", str(cost))
                    string = string.replace("$Cost", str(cost))
                if product_quantity in string:
                    string = string.replace(product_quantity, str(record.field_value_to_float(parameter.quantity_formula)))

                # if str(parameter.field_value) in string and (parameter.type_name.name in ['Product']):
                #     for conf in record.template_parameters:
                if str(parameter.field_value) in string and (parameter.type_name.state in ['template']):
                    for conf in record.template_parameters:
                        if conf.parameter_name.name == parameter.name and conf.template_check:
                            string = string.replace(str(parameter.field_value), "1")
                        if conf.parameter_name.name == parameter.name and not conf.template_check:
                            string = string.replace(str(parameter.field_value), "0")

                if str(parameter.field_value) in string and (parameter.type_name.name in ['Float', 'Height', 'Width', 'Depth']
                                                       or parameter.type_name.state in ["modifier", "push", "pull_modifier"]):
                    for conf in record.template_parameters:
                        if conf.parameter_name.name == parameter.name:
                            if conf.float_values:
                                string = string.replace(str(parameter.field_value), str(conf.float_values))
                            else:
                                string = string.replace(str(parameter.field_value), str(conf.type_list.modifier))

                elif str(parameter.field_value) in string and (parameter.type_name.name == "Product"):
                    for conf in record.template_parameters:
                        if conf.parameter_name.name == parameter.name:
                            if weight_per_area in string:
                                # h = self.env['product.template'].search([('name', '=', conf.products.name)]).height
                                string = string.replace(weight_per_area, str(conf.products.weight_per_square_meter))
                            # if height in string:
                            #     # h = self.env['product.template'].search([('name', '=', conf.products.name)]).height
                            #     string = string.replace(height, str(conf.products.dimension_height))
                            # if width in string:
                            #     # w = self.env['product.template'].search([('name', '=', conf.products.name)]).width
                            #     string = string.replace(width, str(conf.products.dimension_width))
                            # if depth in string:
                            #     # d = self.env['product.template'].search([('name', '=', conf.products.name)]).depth
                            #     string = string.replace(depth, str(conf.products.dimension_length))
                            if conf.parameter_name.name == parameter.name and not conf.products :
                                string = string.replace(str(parameter.field_value), "0")
                            elif conf.parameter_name.name == parameter.name and conf.products:
                                string = string.replace(str(parameter.field_value), "1")

        return string

    # compare if pull condition is true or false
    def comparer(self, compared_to, comparer_list):
        if "=" in compared_to:
            if ">" in compared_to:
                if comparer_list[0] >= comparer_list[1]:
                    return True
            if "<" in compared_to:
                if comparer_list[0] <= comparer_list[1]:
                    return True

            if comparer_list[0] == comparer_list[1]:
                return True

        elif ">" in compared_to:
            if comparer_list[0] > comparer_list[1]:
                return True

        elif "<" in compared_to:
            if comparer_list[0] < comparer_list[1]:
                return True
        return False

    # set new values for configurator based on pull domain
    def new_value(self, string):
        and_split = re.split(' AND | and ', string)
        change = False
        changed_parameters = []
        for slice in and_split:
            string = slice.split("=")
            for record in self:
                for parameter in record.template_name.attribute_line_ids:
                    if str(parameter.field_value) in string[0].strip():
                        for conf in record.template_parameters:
                            # Fix to copy value system for readonly fields
                            if conf.parameter_name.name == parameter.name:
                                changed_parameters.append(parameter)
                                if parameter.type_name.name in ['Float', 'Height', 'Width', 'Depth']:
                                    if conf.float_values != record.eval_expr(record.field_value_to_float(string[1].strip())):
                                        change = True
                                    conf.float_values = record.eval_expr(record.field_value_to_float(string[1].strip()))
                                elif parameter.type_name.state in ["template"]:
                                    if string[1].strip() == "1":
                                        conf.template_check = True
                                    elif string[1].strip() == "0":
                                        conf.template_check = False
                                elif parameter.type_name.name == "Text":
                                    if conf.text_value != string[1].strip():
                                        change = True
                                    conf.text_value = string[1].strip()
                                elif parameter.type_name.state in ['modifier']:
                                    for push_values in parameter.type_name.type_list:
                                        if push_values.modifier == record.eval_expr(record.field_value_to_float(string[1].strip())):
                                            if conf.type_list != push_values:
                                                change = True
                                            conf.type_list = push_values
                                # Push value separated from modifier for inner template products to have product values changed
                                elif parameter.type_name.state in ["push"]:
                                    for push_values in parameter.type_name.type_list:
                                        if push_values.modifier == record.eval_expr(record.field_value_to_float(string[1].strip())):
                                            if conf.type_list != push_values:
                                                change = True
                                                for product_parameter in record.template_parameters:
                                                    if product_parameter.field_value == parameter.type_name.target_parameter:
                                                        product_parameter.products = push_values.preview_product
                                            conf.type_list = push_values
                                elif ".quantity" in string[0].strip():
                                    if parameter.quantity_formula != record.eval_expr(record.field_value_to_float(string[1].strip())):
                                        change = True
                                    parameter.quantity_formula = record.eval_expr(record.field_value_to_float(string[1].strip()))

                                # Add options to call specific product fields through lines like these, may remove for different projects
                                # elif ".height" in string[0].strip():
                                #     if self.env['product.template'].search([('name', '=', conf.products.name)]).dimension_height != record.eval_expr(record.field_value_to_float(string[1].strip())):
                                #         change = True
                                #     self.env['product.template'].search([('name', '=', conf.products.name)]).dimension_height = record.eval_expr(record.field_value_to_float(string[1].strip()))
                                # elif ".width" in string[0].strip():
                                #     if self.env['product.template'].search([('name', '=', conf.products.name)]).dimension_width != record.eval_expr(record.field_value_to_float(string[1].strip())):
                                #         change = True
                                #     self.env['product.template'].search([('name', '=', conf.products.name)]).dimension_width = record.eval_expr(record.field_value_to_float(string[1].strip()))
                                # elif ".depth" in string[0].strip():
                                #     if self.env['product.template'].search([('name', '=', conf.products.name)]).depth != record.eval_expr(record.field_value_to_float(string[1].strip())):
                                #         change = True
                                #     self.env['product.template'].search([('name', '=', conf.products.name)]).depth = record.eval_expr(record.field_value_to_float(string[1].strip()))

                                else:
                                    if conf.products != self.env['product.product'].search([('name', '=', string[1].strip())]):
                                        change = True
                                    conf.products = self.env['product.product'].search([('name', '=', string[1].strip())])
        # Loop pull conditions if a pull parameter changed the value of another parameter
        if change:
            self.pull_condition(changed_attributes=changed_parameters)

    # Check pull conditions and assign domains based on first true condition
    def pull_condition(self, changed_attributes=False):
        for record in self:
            for parameter in record.template_name.attribute_line_ids:
                param = 0
                for type in parameter.type_name:
                    if type.state in ["pull", "pull_modifier"] and not changed_attributes or any(item in changed_attributes for item in type.depend_parameters) :
                        for pull in type.type_list:
                            # Skip pull conditions after first true condition is found
                            if param != 0:
                                continue
                            and_check = True
                            if " AND " or " and " in pull.condition:
                                and_split = re.split(' AND | and ', pull.condition)
                                for slice in and_split:
                                    comparer = []
                                    split = re.split('<=|>=|<|>|=', slice)
                                    for equation in split:
                                        new_equation = record.field_value_to_float(equation.strip())
                                        num_equation = record.eval_expr(new_equation)
                                        comparer.append(num_equation)
                                        if len(comparer) == 2:
                                            if not record.comparer(slice, comparer):
                                                and_check = False
                                if and_check and type.state == "pull":
                                    param = 1
                                    record.new_value(pull.domain)
                                    break

                                elif and_check and type.state == "pull_modifier":
                                    for conf in record.template_parameters:
                                        if conf.parameter_name.name == parameter.name and conf.type_name.id != pull.float_modifier_select.id:
                                            conf.type_name = pull.float_modifier_select.id
                                            type_var = self.env['template.type.list'].search(
                                                [('template_type_list', '=', pull.float_modifier_select.id)], limit=1)
                                            conf.type_list = type_var.id

                            else:
                                comparer = []
                                split = re.split('<=|>=|<|>|=', pull.condition)
                                for equation in split:

                                    new_equation = record.field_value_to_float(equation.strip())

                                    num_equation = record.eval_expr(new_equation)
                                    comparer.append(num_equation)
                                    if len(comparer) == 2:
                                        if record.comparer(slice, comparer) and type.state == "pull":
                                            record.new_value(pull.domain)
                                            param = 1
                                            break
                                        elif record.comparer(slice, comparer) and type.state == "pull_modifier" and conf.type_name.id != pull.float_modifier_select.id:
                                            for conf in record.template_parameters:
                                                if conf.parameter_name.name == parameter.name:
                                                    conf.type_name = pull.float_modifier_select.id
                                                    type_var = self.env['template.type.list'].search([('template_type_list', '=', pull.float_modifier_select.id)], limit=1)
                                                    conf.type_list = type_var.id

    # Get actual values for field_values in a string like name or description
    def name_generator(self, string):
        for record in self:
            if record.template_name and (
                    record.template_name.product_name_generator or record.template_name.product_description):
                name_gen = string
                for parameter in record.template_name.attribute_line_ids:
                    if name_gen and parameter.field_value and parameter.field_value in name_gen:
                        # Find any uses of display names and tag display names in the generator code
                        tag_display_name = str(parameter.field_value) + ".tag_display_name"
                        display_name = str(parameter.field_value) + ".display_name"
                        value = str(parameter.field_value) + ".value"
                        round_value = str(parameter.field_value) + ".round"
                        depth = str(parameter.field_value) + ".depth"
                        for temp_param in record.template_parameters:
                            if temp_param.parameter_name == parameter and temp_param.field_value == parameter.field_value:
                                # if parameter.accessibility != 2:
                                # Replace parameter names and display names with respective code names
                                if temp_param.products.configurator_tag_display_name and tag_display_name in name_gen:
                                    name_gen = name_gen.replace(tag_display_name, temp_param.products.configurator_tag_display_name)
                                if temp_param.products.configurator_display_name and display_name in name_gen:
                                    name_gen = name_gen.replace(display_name, temp_param.products.configurator_display_name)
                                if depth in name_gen:
                                    name_gen = name_gen.replace(depth, str(temp_param.products.depth))
                                if value in name_gen:
                                    name_gen = name_gen.replace(value, str(round(temp_param.float_values, 2)))
                                if round_value in name_gen:
                                    name_gen = name_gen.replace(round_value, str(round(temp_param.float_values)))

                                if parameter.type_name.name == "Product":
                                    name_gen = name_gen.replace(str(parameter.field_value), str(temp_param.products.name))
                                elif parameter.type_name.name in ["Float", "Height", "Width", "Depth"]:
                                    name_gen = name_gen.replace(str(parameter.field_value), str(temp_param.parameter_name.name))
                                elif parameter.type_name.name == "Text":
                                    name_gen = name_gen.replace(str(parameter.field_value), str(temp_param.text_value))
                                else:
                                    name_gen = name_gen.replace(str(parameter.field_value), str(temp_param.type_list.name))

                if "False" in name_gen:
                    name_gen = name_gen.replace("False", "")
                if ".tag_display_name" in name_gen:
                    name_gen = name_gen.replace(".tag_display_name", "")
                if ".display_name" in name_gen:
                    name_gen = name_gen.replace(".display_name", "")
                return name_gen

    # If duplicate configurator is added or changed, swap all values with the Duplicate's values.
    @api.onchange('duplicate_configurator')
    def _onchange_duplicate_configurator(self):
        for record in self:
            new_lines = [(5,)]
            for line in record.duplicate_configurator.template_parameters:
                vals = line.read()[0]
                new_lines.append((0, 0, vals))
            record.quantity = record.duplicate_configurator.quantity
            record.discount = record.duplicate_configurator.discount
            record.template_parameters = new_lines

    # If the template is added or changed, add the respective values to the configurator.
    @api.onchange('template_name')
    def _onchange_template(self):
        for record in self:
            record.duplicate_configurator = False
            order_lines = [(5,)]
            if record.template_name:
                # Take values given in the Configurator Templates' attribute lines
                for parameter in record.template_name.attribute_line_ids:
                    tags = parameter.tag_ids
                    readonly_status = False
                    hidden_status = False
                    default_float_value = 0
                    if parameter.accessibility == "2":
                        readonly_status = True
                    elif parameter.accessibility == "3":
                        hidden_status = True
                    if parameter.type_name.name == "Product":
                        line_config = "line_config_product"
                    elif parameter.type_name.name == "Text":
                        line_config = "line_config_text"
                    elif parameter.type_name.name in ["Float", "Height", "Width", "Depth"]:
                        line_config = "line_config_float"
                        default_float_value = parameter.default_float_value
                    elif parameter.type_name.state in ["push", "modifier", "pull_modifier"]:
                        line_config = "line_config_type"
                    elif parameter.type_name.state in ['template']:
                        line_config = "line_config_template"
                    else:
                        line_config = ""

                    products_union = self.env['product.product'].search([('tag_ids', 'in', tags.ids)])
                    intersection = []
                    number_of_tags = 0
                    for tag in tags:
                        number_of_tags += 1
                        for product_id in tag.products:
                            intersection.append(product_id.product_variant_id.id)
                    counted = Counter(intersection)
                    intersection_products = [el for el in intersection if counted[el] >= number_of_tags]
                    products_intersection = self.env['product.product'].search([('id', 'in', intersection_products)])

                    if parameter.intersection_check:
                        selectable_products = products_intersection
                    else:
                        selectable_products = products_union

                    if parameter.preview_product:
                        preview = parameter.preview_product.id
                    else:
                        preview = False

                    data = {
                        'line_config': line_config,
                        'parameter_name': parameter,
                        'type_name': parameter.type_name,
                        'quantity_formula_value': parameter.quantity_formula,
                        'readonly_status': readonly_status,
                        'hidden_status': hidden_status,
                        'efficiency': parameter.efficiency,
                        'tag_ids': tags,
                        'field_value': parameter.field_value,
                        'intersection_check': parameter.intersection_check,
                        'selectable_products': selectable_products,
                        'template_check': True,
                        'product_uom': parameter.product_uom,
                        'preview_product': preview,
                        'products': preview,
                        'float_values': default_float_value,
                    }

                    if parameter.type_name.name == "Product":
                        for att in record.template_name.attribute_line_ids:
                            if att.type_name.state == "push" and att.type_name.target_parameter == parameter.field_value:
                                for first_value in att.type_name.type_list:
                                    tags = self.env['product.configurator.tag'].search([('id', 'in', first_value.tags.ids)])

                                    products_union = self.env['product.product'].search([('tag_ids', 'in', tags.ids)])
                                    intersection = []
                                    number_of_tags = 0

                                    for tag in tags:
                                        number_of_tags += 1
                                        tag_products = self.env['product.product'].search([('tag_ids', 'in', tag.id)])
                                        # for product_template_id in tag.products:
                                        #     for product_id in product_template_id.product_variant_ids:
                                        for product_id in tag_products:
                                            intersection.append(product_id.id)
                                    # for tag in tags:
                                    #     number_of_tags += 1
                                    #     for product_id in tag.products:
                                    #         intersection.append(product_id.id)
                                    counted = Counter(intersection)

                                    intersection_products = [el for el in intersection if counted[el] >= number_of_tags]
                                    products_intersection = self.env['product.product'].search([('id', 'in', intersection_products)])

                                    if first_value.preview_product:
                                        preview = first_value.preview_product.id
                                    else:
                                        preview = False

                                    if first_value.intersection_check:
                                        data['selectable_products'] = products_intersection.ids
                                        data["products"] = preview
                                    else:
                                        data['selectable_products'] = products_union.ids
                                        data["products"] = preview

                                    data["intersection_check"] = first_value.intersection_check
                                    data["preview_product"] = preview

                                    data["tag_ids"] = first_value.tags.ids
                                    break
                    order_lines.append((0, 0, data))
            record.duplicate_configurator = False
            record.quantity = 1
            record.template_parameters = order_lines
            record.name = record.name_generator(record.template_name.configurator_name_generator)

# update configurator values based on changes to parameters
    @api.onchange('template_parameters', 'discount', 'quantity')
    def _onchange_sizes(self):
        product_exists = self.env['product.product'].search([('configurator_relation.id', '=', self._origin.id)], limit=1)
        if not product_exists:
            for record in self:
                record.duplicate_configurator = False
                if record.template_name:
                    record.pull_condition()
                    cost = 0
                    price_formula = 0
                    routing = {}

                    # Calculate access formula
                    for parameter in record.template_parameters:
                        for attribute in record.template_name.attribute_line_ids:
                            if parameter.field_value == attribute.field_value:
                                if attribute.accessibility_condition:
                                    and_check = True
                                    and_split = re.split(' AND | and ', attribute.accessibility_condition)
                                    for slice in and_split:
                                        comparer = []
                                        split = re.split('<=|>=|<|>|=', slice)
                                        for equation in split:
                                            new_equation = record.field_value_to_float(equation.strip())
                                            num_equation = record.eval_expr(new_equation)
                                            comparer.append(num_equation)
                                            if len(comparer) == 2:
                                                if not record.comparer(slice, comparer):
                                                    and_check = False
                                    if and_check and attribute.accessibility in ['2', '3']:
                                        # if attribute.accessibility == '2':
                                            # parameter.ro_test = True
                                            # parameter.readonly_status = True
                                        if attribute.accessibility == '3':
                                            parameter.hidden_status = True
                                    else:
                                        # parameter.readonly_status = False
                                        parameter.hidden_status = False
                                    # access_condition = record.field_value_to_float(attribute.accessibility_condition)

                    # Calculate routing according to existing values
                    for condition in record.template_name.conditional_routing_formula:
                        and_check = True
                        or_check = False
                        or_split = re.split(' OR | or ', condition.control_formula)
                        for or_slice in or_split:
                            if or_check:
                                continue
                            and_split = re.split(' AND | and ', or_slice)
                            for slice in and_split:
                                comparer = []
                                split = re.split('<=|>=|<|>|=', slice)
                                for equation in split:
                                    new_equation = record.field_value_to_float(equation.strip())
                                    num_equation = record.eval_expr(new_equation)
                                    comparer.append(num_equation)
                                    if len(comparer) == 2:
                                        if not record.comparer(slice, comparer):
                                            and_check = False
                            if and_check:
                                or_check = True
                                duration = record.eval_expr(record.field_value_to_float(condition.duration))
                                routing[condition.routing.id] = duration + condition.routing.workcenter_id.time_start + condition.routing.workcenter_id.time_stop
                    if routing:
                        record.routing = routing
                    else:
                        record.routing = False

                    # Calculate price according to existing values
                    if record.template_name.conditional_price_check:
                        for condition in record.template_name.conditional_price_formula:
                            if price_formula != 0:
                                continue
                            and_check = True
                            and_split = re.split(' AND | and ', condition.control_formula)
                            for slice in and_split:
                                comparer = []
                                split = re.split('<=|>=|<|>|=', slice)
                                for equation in split:
                                    new_equation = record.field_value_to_float(equation.strip())
                                    num_equation = record.eval_expr(new_equation)
                                    comparer.append(num_equation)
                                    if len(comparer) == 2:
                                        if not record.comparer(slice, comparer):
                                            and_check = False
                            if and_check:
                                price_formula = condition.price_formula
                    else:
                        price_formula = record.template_name.price_formula
                    price_formula = record.field_value_to_float(price_formula)
                    price = 0
                    cost_quantity = 0
                    for field in record.template_parameters:
                        if field.products:
                            for parameter in record.template_name.attribute_line_ids:
                                if parameter.field_value == field.field_value:
                                    cost_quantity = record.field_value_to_float(parameter.quantity_formula)
                                    try:
                                        price = record.eval_expr(price_formula)
                                        quantity = record.eval_expr(cost_quantity)
                                        product_uom_ratio = field.products.uom_id.factor_inv
                                        cost_quantity = round(quantity, 2) / product_uom_ratio * parameter.efficiency
                                    except:
                                        price = 0
                                        cost_quantity = 0
                            cost += field.products.standard_price * cost_quantity
                    for route in ast.literal_eval(record.routing).keys():
                        routing_workcenter = self.env['mrp.routing.workcenter'].search([('id', '=', route)])
                        cost += routing_workcenter.workcenter_id.costs_hour * int(ast.literal_eval(record.routing)[route]) / 60

                    # Edit cost, price and margin values accordingly
                    record.calculate_cost = cost * record.quantity
                    record.calculate_price = price * (1 - record.discount/100) * record.quantity
                    record.calculate_margin = (price * (1 - record.discount/100) - cost) * record.quantity
                    if cost != 0:
                        record.calculate_margin_multiplier = price * (1 - record.discount/100) / cost
                    else:
                        record.calculate_margin_multiplier = 0
                if record.template_name.product_description:
                    record.configurator_product_description = record.name_generator(record.template_name.product_description)

                record.name = record.name_generator(record.template_name.configurator_name_generator)

    # Overwrite create to save configurator name
    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('product.configurator') or _('New')
        res = super(ProductConfigurator, self).create(vals)
        res.name = self.with_context(skip_write_configurator=True).name_generator(self.template_name.configurator_name_generator)

        return res

    # Overwrite write to save configurator name
    def write(self, vals):
        product_exists = self.env['product.product'].search([('configurator_relation.id', '=', self.id)], limit=1)

        if not self.env.context.get('skip_write_configurator', False):
            vals.update({
                'name': self.name_generator(self.template_name.configurator_name_generator) + " " + str(self.name_seq),
            })
        res = super(ProductConfigurator, self).write(vals)
        if product_exists:
            product_exists.write({
                'name': self.name_seq + " " + self.name_generator(self.template_name.product_name_generator),
                'description': self.name_generator(self.template_name.product_description)
            })
            sale_order_line = self.env['sale.order.line'].search([('product_id', '=', product_exists.id)])
            for line in sale_order_line:
                line.name = product_exists.description
            existing_lower_product = self.env['product.product'].search([('parent_configurator', '=', product_exists.configurator_relation.id)])
            for line in self.template_parameters:
                if line.type_name.state and line.type_name.state == "template":
                    target_template = line.type_name.target_template
                    for change_value in line.type_name.type_list:
                        # Edit mode allows only text field changes
                        if change_value.relation.type_name.name == "Text":
                            for parameter in self.template_parameters:
                                if parameter.field_value == change_value.name:
                                    value_change_to = parameter.text_value
                                    parameter_to_change = self.env['product.template.attributes'].search(
                                        [('id', '=', change_value.relation.id)])
                                    for lower_product in existing_lower_product:
                                        if lower_product.configurator_relation.template_name.id == target_template.id:
                                            for low_conf_value in lower_product.configurator_relation.template_parameters:
                                                if low_conf_value.parameter_name.id == parameter_to_change.id:
                                                    low_conf_value.text_value = value_change_to
            if existing_lower_product:
                for single in existing_lower_product:
                    single.write({
                        'name': single.configurator_relation.name_seq + " " + single.configurator_relation.name_generator(single.configurator_relation.template_name.product_name_generator),
                        'description': single.configurator_relation.name_generator(single.configurator_relation.template_name.product_description)
                    })
                lower_sale_order_line = self.env['sale.order.line'].search([('product_id', '=', single.id)])
                for line in lower_sale_order_line:
                    line.name = single.description
        return res

    # Return configurator product id for adding to sale order line
    @api.model
    def configurator_product_values(self):
        # conf = self.env['product.configurator'].search([], order="id desc", limit=1)
        configurator = self.env['product.configurator'].search([("check", "=", True)])
        product_ids = []

        for conf in configurator:
            conf.check = False
            product = self.env['product.product'].search([('configurator_relation', '=', conf.id)])
            for prod_id in product:
                if not prod_id.inner_template:
                    product_ids.insert(0, {
                            "product_id": prod_id.id,
                            "quantity": conf.quantity,
                            "discount": conf.discount,
                        })

        if not product_ids:
            product_ids.append({})
        return product_ids

    # create configurator product based on template
    def create_template_product(self, template, check, parent_configurator):
        for record in self:
            price_formula, height, width, depth = 0, 0, 0, 0
            # Run pull parameter check for inner template products
            record.pull_condition()
            if template.conditional_price_check:
                for condition in template.conditional_price_formula:
                    if price_formula != 0:
                        continue
                    and_check = True
                    and_split = re.split(' AND | and ', condition.control_formula)
                    for slice in and_split:
                        comparer = []
                        split = re.split('<=|>=|<|>|=', slice)
                        for equation in split:
                            new_equation = record.field_value_to_float(equation)
                            num_equation = record.eval_expr(new_equation.lstrip())
                            comparer.append(num_equation)
                            if len(comparer) == 2:
                                if not record.comparer(slice, comparer):
                                    and_check = False
                    if and_check:
                        price_formula = condition.price_formula
            else:
                price_formula = template.price_formula
            price_formula = record.field_value_to_float(price_formula)
            price = record.eval_expr(price_formula)

            # Add info regarding all the products within a Configurator to a list to append to BoM later
            configurator_products = []
            weight = 0

            template_relation = record.template_name.id
            cost = 0
            for bom_product in record.template_parameters:
                formula = bom_product.quantity_formula_value
                if bom_product.type_name.name == "Height":
                    height = bom_product.float_values
                elif bom_product.type_name.name == "Width":
                    width = bom_product.float_values
                elif bom_product.type_name.name == "Depth":
                    depth = bom_product.float_values

                if formula and bom_product.products:
                    formula = record.field_value_to_float(formula)

                    product_uom_ratio = bom_product.products.uom_id.factor_inv

                    # if product_uom_ratio < 0:
                    #     product_uom_ratio = 0
                    if bom_product.products.name not in ["None", "none"] and product_uom_ratio > 0:
                        formula_quantity = record.eval_expr(formula)
                        quantity = formula_quantity / product_uom_ratio
                        weight += bom_product.products.weight * quantity
                        bom_quantity = formula_quantity * bom_product.efficiency
                        if bom_quantity > 0:
                            cost += bom_quantity * bom_product.products.standard_price

                            # Append the BoM product values to the list for later usage
                            configurator_products.append((0, 0, {
                                'product_id': bom_product.products.id,
                                'product_qty': bom_quantity,
                                'product_uom_id': bom_product.product_uom.id,
                            }))

            description = ""
            configurator_relation = record.id

            if check or template.template_check:
                template_check = True
            else:
                template_check = False
            if template.product_description:
                description = record.name_generator(template.product_description)

            configurator_files = []
            for file in template.template_file:
                configurator_files.append(file.id)
            for file in record.configurator_file:
                configurator_files.append(file.id)

            replenish_on_order_route = self.env.ref('stock.route_warehouse0_mto')
            manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture')

            product_name = record.name_seq + " " + record.name_generator(template.product_name_generator)

        # If no example product was chosen in the template, create a new one with default values
            if not template.example_product:
                product = self.env['product.product'].create({
                    'name': product_name,
                    'type': 'product',
                    'description': description,
                    'list_price': price,
                    # 'weight': weight,
                    # 'height': height/100,
                    # 'width': width/100,
                    # 'depth': depth/100,
                    'inner_template': template_check,
                    'default_code': record.default_code,
                    'separate_template': check,
                    'configurator_relation': configurator_relation,
                    'template_relation': template_relation,
                    'parent_configurator': parent_configurator,
                    'configurator_file': [(6,0,configurator_files)],
                    'route_ids': [replenish_on_order_route.id, manufacture_route.id],
                    'produce_delay': template.produce_delay,
                    'categ_id': template.categ_id.id,
                    'purchase_ok': False,
                    # 'route_ids': template.route_ids.ids,
                })
            # If an example product was chosen in the template, create a new product with values from the example product
            else:
                product = template.example_product.copy({
                    'name': product_name,
                    'description': description,
                    'list_price': price,
                    # 'weight': weight,
                    # 'height': height/100,
                    # 'width': width/100,
                    # 'depth': depth/100,
                    'inner_template': template_check,
                    'default_code': record.default_code,
                    'separate_template': check,
                    'configurator_relation': configurator_relation,
                    'template_relation': template_relation,
                    'parent_configurator': parent_configurator,
                    'configurator_file': [(6,0,configurator_files)],
                    'route_ids': [replenish_on_order_route.id, manufacture_route.id],
                    'produce_delay': template.produce_delay,
                    'purchase_ok': False,
                })

            operation_ids = []
            if record.routing:
                for route in ast.literal_eval(record.routing).keys():
                    routing_workcenter = self.env['mrp.routing.workcenter'].search([('id', '=', route)])
                    operation_ids.append((0, 0, {
                        'name': routing_workcenter.name + " - " + product_name,
                        'workcenter_id': routing_workcenter.workcenter_id.id,
                        'auto_generate_check': True,
                        'time_cycle_manual': float(ast.literal_eval(record.routing)[route]),
                        # 'time_cycle': bom_product.product_uom.id,
                    }))


            bom = self.env['mrp.bom'].create({
                'product_id': product.id,
                'product_tmpl_id': product.product_tmpl_id.id,
                'bom_line_ids': configurator_products,
                'operation_ids': operation_ids,
                # 'routing_id': record.routing.id,
            })

            bom.message_post(attachment_ids=configurator_files)

            boms_to_recompute = self.env['mrp.bom'].search(
                ['|', ('product_id', 'in', product.ids), '&', ('product_id', '=', False),
                 ('product_tmpl_id', 'in', product.mapped('product_tmpl_id').ids)])

            self.env['product.product'].browse(product.id).write({
                'standard_price': product._compute_bom_price(bom, boms_to_recompute)
            })
            return product

    # Create configurator and ready it for adding to sale order line
    def action_save(self):
        product_exists = self.env['product.product'].search([('configurator_relation.id', '=', self.id)])
        low_product_list = []
        low_product_quantities = {}
        if not product_exists:
            conf = self.env['product.configurator'].search([('create_uid', '=', self._uid)], order="id desc", limit=1)
            conf.check = True
            if conf.template_name.template_check:
                conf.create_template_product(conf.template_name, True, False)
                return
            for parameter in conf.template_parameters:
                if parameter.type_name.state == "template" and parameter.template_check:
                    template = conf.env['product.configurator.templates'].search(
                        [('name', '=', parameter.type_name.target_template.name)])
                    list_ids = []
                    quantity_equation = self.field_value_to_float(parameter.quantity_formula_value)
                    quantity = self.eval_expr(quantity_equation)
                    for attribute in template.attribute_line_ids:
                        push_check = False
                        tags = attribute.tag_ids
                        data = {
                            'parameter_name': attribute.id,
                            'type_name': attribute.type_name.id,
                            'quantity_formula_value': attribute.quantity_formula,
                            'efficiency': attribute.efficiency,
                            'tag_ids': tags,
                            'field_value': attribute.field_value,
                            'template_check': True,
                            'product_uom': attribute.product_uom.id,
                            'preview_product': attribute.preview_product.id,
                        }
                        # Give product parameter value, overwrite based on existing related push parameters
                        if attribute.type_name.name == "Product":
                            data["products"] = attribute.preview_product.id
                            for att in template.attribute_line_ids:
                                if att.type_name.state == "push" and att.type_name.target_parameter == attribute.field_value:
                                    for first_value in att.type_name.type_list:
                                        data["products"] = first_value.preview_product.id
                                        break

                        # Check template parameter values for editing inner template parameter values accordingly
                        for relation in parameter.type_name.type_list:
                            if relation.relation == attribute:
                                for outer_parameter in conf.template_parameters:
                                    if outer_parameter.field_value == relation.name:
                                        if outer_parameter.type_name.name == "Product":
                                            data["products"] = outer_parameter.products.id
                                        elif outer_parameter.type_name.name == "Text":
                                            data['text_value'] = outer_parameter.text_value
                                        elif outer_parameter.type_name.name in ["Float", "Height", "Width", "Depth"]:
                                            data['float_values'] = outer_parameter.float_values
                                        elif outer_parameter.type_name.state in ["push", "modifier"]:
                                            data['type_list'] = outer_parameter.type_list.id
                        list_line = self.env['product.configurator.list'].create({})
                        list_line.write(data)
                        list_ids.append((4, list_line.id, 0))

                    low_product = self.env['product.configurator'].create({
                        'template_name': template.id,
                        'configurator_product_description': template.product_description,
                        'template_parameters': list_ids,
                        'discount': conf.discount,
                        'quantity': conf.quantity,
                        # 'routing': routing,
                        'check': True
                    })

                    # template_routing = False
                    routing = {}
                    # Calculate routing according to existing values
                    for condition in template.conditional_routing_formula:
                        # if routing != 0:
                        #     continue
                        and_check = True
                        and_split = re.split('AND|and', condition.control_formula)
                        for slice in and_split:
                            comparer = []
                            split = re.split('<=|>=|<|>|=', slice)
                            for equation in split:
                                new_equation = low_product.field_value_to_float(equation.strip())
                                num_equation = low_product.eval_expr(new_equation)
                                comparer.append(num_equation)
                                if len(comparer) == 2:
                                    if not low_product.comparer(slice, comparer):
                                        and_check = False
                        if and_check:
                            routing[
                                condition.routing.id] = condition.duration  # + condition.routing.workcenter_id.time_start + condition.routing.workcenter_id.time_stop
                    # if routing != 0:
                    #     template_routing = routing
                    #     routing[condition.routing.id] = duration + condition.routing.workcenter_id.time_start + condition.routing.workcenter_id.time_stop

                    low_product.write({
                        'routing': routing,
                    })

                    inner_product = low_product.create_template_product(low_product.template_name, False, conf.id)
                    low_product_quantities[inner_product.id] = quantity
                    low_product_list.append(inner_product)

            main_product = conf.create_template_product(conf.template_name, False, False)

            for single_low_product in low_product_list:
                bom = self.env['mrp.bom'].search([('product_id', '=', main_product.id)])
                bom_line = self.env['mrp.bom.line'].create({
                    'bom_id': bom.id,
                    'product_id': single_low_product.id,
                    'product_qty': low_product_quantities[single_low_product.id],
                    'product_uom_id': single_low_product.product_tmpl_id.uom_id.id,
                    # 'routing_id': record.routing.id,
                })

                boms_to_recompute = self.env['mrp.bom'].search(
                    ['|', ('product_id', 'in', main_product.ids), '&', ('product_id', '=', False),
                     ('product_tmpl_id', 'in', main_product.mapped('product_tmpl_id').ids)])

                self.env['product.product'].browse(main_product.id).write({
                    # 'standard_price': product._set_price_from_bom(boms_to_recompute)
                    'standard_price': main_product._compute_bom_price(bom, boms_to_recompute)
                })

            vals = {
                # 'sequence': 10000,
                'product_id': main_product.id,
                # 'product_uom': self.company_id.sales_discount_product.uom_id,
                'product_uom_qty': conf.quantity,
                # 'price_unit': self.amount_discount * -1,
                'name': self.name_generator(self.template_name.product_description),
                'discount': conf.discount,
                'order_id': conf.order_id.id,
                # 'tax_id': [(6, 0, self.company_id.sales_discount_product.taxes_id.ids)],
            }
            sol = self.env['sale.order.line'].sudo().create(vals)
            return

    # Used for changing product tags based on related push field
    @api.onchange('template_parameters_push')
    def _onchange_push_domain(self):
        for record in self:
            for inside in record.template_parameters_push:
                if inside.param:
                    all_param = inside.param.split()
                    for param in all_param:
                        inter = inside.intersection
                        domain = inside.push_domain
                        new_tags = json.loads(domain)
                        for other_line in record.template_parameters:
                            if other_line.parameter_name.field_value == str(param):
                                old_tags = []
                                for tag in other_line.tag_ids:
                                    old_tags.append(tag._origin.id)
                                tags = self.env['product.configurator.tag'].search([('id', 'in', new_tags)])
                                products_union = self.env['product.product'].search([('tag_ids', 'in', tags.ids)])
                                intersection = []
                                number_of_tags = 0
                                for tag in tags:
                                    number_of_tags += 1
                                    tag_products = self.env['product.product'].search([('tag_ids', 'in', tag.id)])
                                    for product_id in tag_products:
                                        intersection.append(product_id.id)
                                counted = Counter(intersection)
                                intersection_products = [el for el in intersection if counted[el] >= number_of_tags]
                                products_intersection = self.env['product.product'].search([('id', 'in', intersection_products)])
                                # Change product tags and preview value based on related push field actively
                                if old_tags != new_tags or other_line.preview_product != inside.preview_product:
                                    if inter:
                                        other_line.selectable_products = products_intersection
                                    else:
                                        other_line.selectable_products = products_union
                                    other_line.tag_ids = new_tags
                                    if inside.preview_product:
                                        other_line.products = inside.preview_product
                                    else:
                                        other_line.products = False
                                    other_line.preview_product = inside.preview_product
                                    if record.template_name.product_description:
                                        record.configurator_product_description = record.name_generator(
                                            record.template_name.product_description)
                                    # record.pull_condition()
                                    record._onchange_sizes()

    # used for changing product tags based on related push field
    @api.depends('template_parameters.type_list.name')
    def _compute_push(self):
        for record in self:
            push = [(5, 0, 0)]
            for line in record.template_parameters:
                if line.type_name.state == 'push' and line.type_list:
                    for type_list in line.type_name.type_list:
                        if type_list == line.type_list:
                            domain = []
                            tags = type_list.tags
                            for tag in tags:
                                domain.append(tag.id)
                            param = line.type_name.target_parameter
                            push.append((0, 0, {
                                'param': param,
                                'push_domain': domain,
                                'parameter_line': type_list.id,
                                'intersection': type_list.intersection_check,
                                'preview_product': type_list.preview_product,
                            }))
            if len(push) > 1:
                record.template_parameters_push = push
                record._onchange_push_domain()
            else:
                record.template_parameters_push = False


class ProductConfiguratorListPush(models.Model):
    _name = "product.configurator.list.push"
    _description = "Product Configurator push fields system"

    # Additional model for relating push fields with their respective product fields
    param = fields.Char()
    push_domain = fields.Char()
    parameter_line = fields.Many2one('product.configurator')
    preview_product = fields.Many2one('product.product')
    intersection = fields.Boolean()


class ProductConfiguratorList(models.Model):
    _name = "product.configurator.list"
    _description = "Product Configurator parameter system"

    tag_ids = fields.Many2many('product.configurator.tag', string='Tags')

    selectable_products = fields.Many2many('product.product')
    readonly_status = fields.Boolean()
    hidden_status = fields.Boolean()

    group_type = fields.Selection(related='parameter_name.group_type')

    parameter_name = fields.Many2one('product.template.attributes')
    type_name = fields.Many2one("template.type")
    intersection_check = fields.Boolean(string="Intersection", default=False)
    parameter_line = fields.Many2one('product.configurator')
    products = fields.Many2one('product.product', domain="[('id', 'in', selectable_products)]")

    placeholder = fields.Many2one('product.product',
                               domain="[('tag_ids', 'in', tag_ids)]", context="{'configurator_display_name': 1}",
                               compute="_compute_default_product", store=True)

    # type_list = fields.Many2one("template.type.list", domain="['|', '&', ('template_type_list', '=', type_name), ('state', '!=', 'pull_modifier'), '&', ('template_type_list', '=', type_name), ('state', '=', 'pull_modifier')]")
    type_list = fields.Many2one("template.type.list", domain="[('template_type_list', '=', type_name)]")

    field_value = fields.Char()
    efficiency = fields.Float()

    text_value = fields.Text()

    quantity_formula_value = fields.Char()
    float_values = fields.Float()
    product_uom = fields.Many2one('uom.uom', domain="[('uom_type', '=', 'reference')]")

    preview_product = fields.Many2one('product.product')
    template_check = fields.Boolean(default=True)

    line_config = fields.Selection([
        ('line_config_text', 'Text'),
        ('line_config_product', 'Product'),
        ('line_config_float', 'Float'),
        ('line_config_type', 'Type'),
        ('line_config_template', 'Template')
    ])

    # Set default values for type_list and products
    @api.depends('line_config')
    def _compute_default_product(self):
        for record in self:
            if record.line_config == 'line_config_product':
                if record.products:
                    continue
                if record.preview_product:
                    record.products = record.preview_product
                # ONLY IF YOU DON'T WANT EMPTY LINES IN PRODUCTS
                # else:
                #     first = self.env['product.product'].search([('tag_ids', 'in', record.tag_ids.ids)], limit=1)
                #     record.products = first

            elif record.line_config == 'line_config_type':
                if record.type_list:
                    continue
                first = self.env['template.type.list'].search([('template_type_list', '=', record.type_name.id)], limit=1)
                record.type_list = first

    def create(self, vals):
        res = super(ProductConfiguratorList, self).create(vals)
        return res

    # Overwrite write to save configurator name
    def write(self, vals):
        res = super(ProductConfiguratorList, self).write(vals)
        return res

# iga rea juures lisaväli grupi tähisega näiteks : "1. mõõdud", "2. lukustus", "3. omadused", "4. ekstrad", "5. aknad"

class ProductNameChange(models.Model):
    _inherit = "product.product"

    # If product has a configurator display name show it instead under configurator list Products dropdown
    def name_get(self):
        result = []
        for record in self:
            if self.env.context.get('params', {}).get('model', False) == 'product.configurator' or \
                    self.env.context.get('open_template_configurator') or \
                    self.env.context.get('default_template_name') \
                    or self.env.context.get('configurator_display_name', False):
                if record.configurator_display_name:
                    result.append((record.id, record.configurator_display_name))
                else:
                    result.append((record.id, record.name))
            else:
                result.append((record.id, record.name))

        return result


class MrpRoutingWorkcenterAddition(models.Model):
    _inherit = 'mrp.routing.workcenter'

    auto_generate_check = fields.Boolean(default=False)
