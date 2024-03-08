# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re
import ast
import operator as op
from logging import getLogger
from collections import Counter

_logger = getLogger(__name__)


class ProductConfiguratorTemplateTest(models.Model):
    _name = "product.configurator.template.test"

    test_environment_values = fields.One2many('test.environment', 'template_test_id')
    template_type_id = fields.Many2one('template.type')
    template_id = fields.Many2one('product.configurator.templates')
    # test_template_product_name = fields.Char()
    # test_template_product_description = fields.Char()
    value = fields.Float(compute="_compute_value_float")
    value_string = fields.Char(compute="_compute_value_string")
    # test_routes = fields.One2many(comodel_name='product.configurator.template.routing', inverse_name='test_routing', string=_('Conditional Template Routing'))

    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
                 ast.USub: op.neg}

    # eval to calculate string based equations to numerical values
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

    def value_from_test_environment(self, string):
        for record in self:
            for environment_line in record.test_environment_values:
                string = string.replace(environment_line.name, str(environment_line.value))
            return str(string)

    @api.depends('test_environment_values')
    def _compute_value_string(self):
        for record in self:
            for type_line in record.template_type_id.type_list:
                and_check = True
                and_split = re.split(' AND | and ', type_line.condition)
                for slice in and_split:
                    comparer = []
                    split = re.split('<=|>=|<|>|=', slice)
                    for equation in split:
                        new_equation = record.value_from_test_environment(equation.strip(' '))
                        num_equation = record.eval_expr(new_equation)
                        comparer.append(num_equation)
                        if len(comparer) == 2:
                            if not record.comparer(slice, comparer):
                                and_check = False
                if and_check:
                    record.value_string = type_line.domain
                    return
            record.value_string = "None"
            return

    @api.onchange('template_id')
    def _onchange_template_id(self):
        for record in self:
            for test_line in record.test_environment_values:
                test_line.value = 0
                for parameter in record.template_id.attribute_line_ids:
                    if parameter.field_value == test_line.name:
                        if parameter.type_name.name in ['Float', 'Height', 'Width', 'Depth']:
                            test_line.value = parameter.default_float_value
                            record._compute_value_string()
                            break
                        elif parameter.type_state in ['modifier', 'push']:
                            line_value = 0
                            for line in parameter.type_name.type_list:
                                line_value = line.modifier
                                break
                            test_line.value = line_value
                            record._compute_value_string()
                            break

    @api.depends('template_id', 'value_string')
    def _compute_value_float(self):
        if self.value_string and self.template_id and self.value_string != "None":
            try:
                value_string_equals = self.value_string.split('=')[1].strip()
                for parameter in self.template_id.attribute_line_ids:
                    if parameter.type_name.name in ['Float', 'Height', 'Width', 'Depth']:
                        value_string_equals = value_string_equals.replace(parameter.field_value, str(parameter.default_float_value))
                    elif parameter.type_state in ['modifier', 'push']:
                        line_value = 0
                        for line in parameter.type_name.type_list:
                            line_value = line.modifier
                            break
                        value_string_equals = value_string_equals.replace(parameter.field_value, str(line_value))
                self.value = self.eval_expr(value_string_equals)
            except SyntaxError:
                raise Warning('No such field value found on template!')
        else:
            self.value = 0


class TemplateTypeTestEnvironment(models.Model):
    _name = 'test.environment'

    template_test_id = fields.Many2one('product.configurator.template.test')
    name = fields.Char()
    value = fields.Float()