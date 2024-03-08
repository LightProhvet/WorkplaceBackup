# -*- coding: utf-8 -*-

from odoo import api, fields, models
from logging import getLogger

_logger = getLogger(__name__)


class Production(models.Model):
    _inherit = 'mrp.production'

    original_partner_id = fields.Many2one(  # or sale_original_partner_id. Name kept like this for consistency.
        comodel_name='res.partner',
        string='Original Customer')

    # sale_partner_object_id = fields.Many2one(
    #     comodel_name='res.partner',
    #     domain=[('object', '=', True)],
    #     string='Sale Partner Object')

