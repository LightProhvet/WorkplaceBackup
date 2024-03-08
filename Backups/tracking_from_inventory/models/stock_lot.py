# -*- coding: utf-8 -*-

from odoo import models, _, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

import logging

_logger = logging.getLogger()


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.model
    def create(self, vals_list):
        self._check_create()
        vals = super(StockLot, self).create(vals_list)
        move_id = self._context.get('move_id_to_link', False)
        if move_id:  # in this case we should only have on lot in vals!!!
            move = self.env['stock.move'].browse(move_id)
            for line in move.move_line_ids:
                if line.lot_id:
                    continue
                line.update({
                    'lot_id': vals
                })
                break
            _logger.info(f"move {move.move_line_ids} now has {move.lot_ids}") #BUT THIS IS OVERWRITTEN FOR SOME REASON!!!
        return vals
