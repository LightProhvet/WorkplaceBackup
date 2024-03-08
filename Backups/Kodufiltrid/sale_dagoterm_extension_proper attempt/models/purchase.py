# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object',
        # compute="_compute_partner_object_id",
        # readonly=False,
        # store=True
    )

    original_partner_id = fields.Many2one(
        'res.partner', string='Original Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    # @api.depends('order_line.sale_order_id')
    # def _compute_partner_object_id(self):
    #     for order in self:
    #         sale_order = order._get_sale_orders()
    #         # _logger.info(f"\n\nAuto order: {order.auto_sale_order_id} Sale order: {order.order_line.sale_order_id} Or what im using: {sale_order}")
    #         for sale in sale_order:
    #             order.partner_object_id = sale.partner_object_id
    #             break  # ensures we take the first, even when there is more and handles None as well.

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        vals = super(PurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        vals['partner_object_id'] = self.partner_object_id.id
        vals['original_partner_id'] = self.original_partner_id.id
        return vals

    @api.model
    def _prepare_sale_order_line_data(self, line, company):
        values = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company)
        values.update({
            'partner_object_id': line.partner_object_id.id,
        })
        return values

    def _prepare_picking(self):
        values = super(PurchaseOrder, self)._prepare_picking()
        values.update({
            'partner_object_id': self.partner_object_id.id,
            'original_partner_id': self.original_partner_id.id,
        })
        return values


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object',
        # compute="_compute_partner_object_id",
        # readonly=False,
        # store=True
    )

    # @api.depends('sale_line_id.partner_object_id')
    # def _compute_partner_object_id(self):
    #     # _logger.info(f"\n\n\nCOMPUTING")
    #     for line in self:
    #         done = False
    #         sale_order = line.order_id._get_sale_orders()
    #         for sale in sale_order:
    #             for sale_line in sale.order_line:
    #                 if sale_line.product_id == line.product_id:
    #                     line.partner_object_id = sale_line.partner_object_id
    #                     done = True
    #                     break
    #             if done:
    #                 break
            #
            # _logger.info(f"\n\nSale line: {line.sale_order_id.order_line} Sale order: {line.sale_order_id}")
            #
            # for sale in line.sale_line_id:
            #     _logger.info(f"\n And we have succesfulyl set: {sale.partner_object_id}")
            #
            #     line.partner_object_id = sale.partner_object_id
            #     break  # ensures we take the first, even when there's more (there shouldn't be), handles None as well.

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for re in res:
            re['partner_object_id'] = self.partner_object_id.id
        return res
