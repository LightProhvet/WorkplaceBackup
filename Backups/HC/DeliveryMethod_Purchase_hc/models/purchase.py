# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'purchase.order'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 compute='_compute_delivery_carrier',
                                 readonly=False,
                                 store=True,
                                 # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 )

    @api.depends('partner_id.purchase_delivery_carrier_id')
    def _compute_delivery_carrier(self):
        for order in self:
            if order.partner_id.purchase_delivery_carrier_id:
                order.carrier_id = order.partner_id.purchase_delivery_carrier_id

    # def set_delivery_line(self, carrier, amount):
    #     self._remove_delivery_line()
    #     for order in self:
    #         order.carrier_id = carrier.id
    #         order._create_delivery_line(carrier, amount)
    #     return True
