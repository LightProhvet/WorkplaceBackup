# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object')
