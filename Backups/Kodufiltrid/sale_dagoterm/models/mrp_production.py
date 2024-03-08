# -*- coding: utf-8 -*-

from odoo import api, fields, models
from logging import getLogger

_logger = getLogger(__name__)


class Production(models.Model):
    _inherit = 'mrp.production'

    sale_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Sale Partner')
    sale_partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Sale Partner Object')
    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        store=True,
        related='product_tmpl_id.categ_id')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            origin = vals.get('origin', False)
            if origin:
                dom = [('name', '=', origin)]
                order = self.env['sale.order'].search(dom, limit=1)
                if order:
                    partner_id = order.partner_id and order.partner_id.id
                    object_id = order.partner_object_id and order.partner_object_id.id
                    vals['sale_partner_id'] = partner_id
                    vals['sale_partner_object_id'] = object_id

        return super(Production, self).create(vals_list)
