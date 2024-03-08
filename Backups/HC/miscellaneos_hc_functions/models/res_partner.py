# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    purchase_delivery_carrier_id = fields.Many2one('delivery.carrier', company_dependent=True,
                                                   string="Purchase Delivery Method",
                                                   help="Default delivery method used in Purchase orders.")
