# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object',
        compute="_compute_partner_object_id",
    )

    @api.depends('sale_line_id.partner_object_id', 'purchase_line_id.partner_object_id', 'picking_id.partner_object_id')
    def _compute_partner_object_id(self):
        for move in self:
            if move.sale_line_id:
                _logger.info(f"\n\nsale line: {move.sale_line_id} Sale order: {move.picking_id.sale_id} Purchase order: {move.picking_id.purchase_id}")
                line = move.sale_line_id
                for sale in line:
                    move.partner_object_id = sale.partner_object_id
                    break  # ensures we take the first, even when there is more and handles None as well.

            elif move.purchase_line_id:  # how about created purchase line?
                _logger.info(f"\n\nPurchase line: {move.purchase_line_id} Purchase order: {move.picking_id.purchase_id}")
                line = move.purchase_line_id
                for purchase in line:
                    move.partner_object_id = purchase.partner_object_id
                    break  # ensures we take the first, even when there is more and handles None as well.
            elif move.production_id:
                _logger.info(f"\n\n HEY!!! we have Production order: {move.production_id} Sale order: {move.picking_id.purchase_id}")
                move.partner_object_id = False
            else:
                move.partner_object_id = False
