# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object')

    def _prepare_procurement_values(self, group_id=False):
        _logger.info(f"\n\n Creating picking or smth?")
        # I am assuming this is used to create the actual mrp_order/picking not only line/move
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({
            'partner_object_id': self.order_id.partner_object_id.id,
            'original_partner_id': self.order_id.original_partner_id.id,
        })
        _logger.info(f"\nAnd Right now i am getting object : {values['partner_object_id']}")
        return values

    def _purchase_service_prepare_order_values(self, supplierinfo):
        _logger.info(f"\n\n \n\n \n\n Super works")
        values = super(SaleOrderLine, self)._purchase_service_prepare_order_values(supplierinfo)
        self.ensure_one()
        values.update({
            'partner_object_id': self.order_id.partner_object_id.id,
            'original_partner_id': self.order_id.original_partner_id.id,
        })
        _logger.info(f"\nAnd we are writing values: {values}")
        return values

    def _purchase_service_generation(self):
        _logger.info(f"\n\n\n Well, atleast this triggers...")
        return super(SaleOrderLine, self)._purchase_service_generation()

    def _purchase_service_create(self, quantity=False):
        _logger.info(f"\n\n I AM CREATING FROM HERE")
        return super(SaleOrderLine, self)._purchase_service_create(quantity)

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        _logger.info(f"\n\n And when creating lines")
        values = super(SaleOrderLine, self)._purchase_service_prepare_line_values(purchase_order, quantity)
        self.ensure_one()
        values.update({
            'partner_object_id': self.partner_object_id.id,
        })
        _logger.info(f"\n We give object : {values['partner_object_id']}")

        return values
