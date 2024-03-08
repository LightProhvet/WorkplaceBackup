# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class Picking(models.Model):
    _inherit = 'stock.picking'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object',
        # compute="_compute_partner_object_id",
        # readonly=False,
        # store=True
    )
    original_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Original Customer')

    # @api.depends('sale_id.partner_object_id')
    # def _compute_partner_object_id(self):
    #     for picking in self:
    #         sale_order = picking.sale_id
    #         for sale in sale_order:
    #             picking.partner_object_id = sale.partner_object_id
    #             break  # ensures we take the first, even when there is more and handles None as well.
