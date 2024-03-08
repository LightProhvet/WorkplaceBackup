# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from random import randint


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    done_qty = fields.Float("Assumed Quantity", digits='Product Unit of Measure', related="move_id.quantity_done")
    quantity = fields.Float(default=lambda self: self.done_qty)
