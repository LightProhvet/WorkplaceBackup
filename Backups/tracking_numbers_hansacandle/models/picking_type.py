# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger()


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_full_pallets = fields.Boolean(string="Use full pallets")
    
