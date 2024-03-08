# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def use_default_secondary_uom(self):
        for line in self:
            line.secondary_uom_id = line.product_id.secondary_uom_id
