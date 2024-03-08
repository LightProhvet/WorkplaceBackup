# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    original_partner_id = fields.Many2one(
        'res.partner', string='Original Customer', readonly=False,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute="_compute_original_partner_id",
        store=True
    )

    @api.depends('partner_id')
    def _compute_original_partner_id(self):
        for order in self:
            if order.original_partner_id:
                order.original_partner_id = order.original_partner_id
            else:
                order.original_partner_id = order.partner_id

