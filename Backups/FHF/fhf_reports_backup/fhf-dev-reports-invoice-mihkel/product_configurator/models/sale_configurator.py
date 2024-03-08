# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from logging import getLogger
from datetime import datetime
import ast
import operator as op
import re

_logger = getLogger(__name__)


class SaleOrderLineConfigurator(models.Model):
    _inherit = "sale.order.line"

    def get_sale_order_line_multiline_description_sale(self, product):
        if self.product_id.description:
            return self.product_id.description
        else:
            return self.product_id.name

    # Make note of configurator products removed from SOL
    # @api.multi
    def unlink(self):
        product = self.env['product.product'].browse(self.product_id.id)
        product.write({
            'configurator_check': False
        })

        for temp_product in self.env['product.template'].search([('name', '=', product.name)]):
            temp_product.write({
                'configurator_check': False
            })
        return super(SaleOrderLineConfigurator, self).unlink()

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        """overriding the original function to remove the low stock warning"""
        return {}

    def button_open_configurator(self):
        self.ensure_one()
        if self.product_id.configurator_relation:
            view = self.env.ref('product_configurator.product_configurator_text_edit_view')
            return {
                'name': 'Product Configurator',
                'res_model': 'product.configurator',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.product_id.configurator_relation.id,
                'view_id': self.env.ref('product_configurator.product_configurator_text_edit_view').id,
                'target': 'new'
            }


class SaleOrderConfigurator(models.Model):
    _inherit = "sale.order"

    amount_margin_multiplier = fields.Float(string="Margin multiplier", store=True, readonly=True, compute='_amount_all')

    last_added_template_line = fields.Many2one('sale.order.line', string="Last added template line")

    def add_configurator(self):
        return {
            'name': 'Product Configurator',
            'res_model': 'product.configurator',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            # 'res_id': self.product_id.configurator_relation.id,
            'view_id': self.env.ref('product_configurator.product_configurator_view').id,
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_margin_multiplier, amount_cost, amount_untaxed, amount_tax = 0.0, 0.0, 0.0, 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_cost += line.product_id.standard_price * line.product_uom_qty
            if amount_cost != 0:
                amount_margin_multiplier = amount_untaxed / amount_cost
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
               # 'amount_margin': amount_untaxed - amount_cost,
                'amount_margin_multiplier': amount_margin_multiplier,
            })

    # Make note of configurator products saved to SO
    # @api.multi
    def write(self, vals):
        for record in self:
            for line in record.order_line:
                temp_name = self.env['product.product'].browse(line.product_id.id).name
                for temp_prod in self.env['product.template'].search([('name', '=', temp_name)]):
                    temp_prod.write({
                        'configurator_check': True
                    })
                self.env['product.product'].browse(line.product_id.id).write({
                    'configurator_check': True
                })
        res = super(SaleOrderConfigurator, self).write(vals)
        return res
