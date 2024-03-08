# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger()


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_create_new_lot(self):
        self.ensure_one()
        action = {
            'name': _('Create Lot'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.lot',
            'view_id': self.env.ref('stock.view_production_lot_form').id,
            'target': 'new',
            'context': {
                **self.env.context,  # unnecessary?
                'move_id_to_link': self.id,
            }
        }
        return action
        # for move in self.move_ids:
        #     if move.lot_ids:
        #         continue
        #     if move.product_id:
        #         use_product = move.product_id
        #         return action
        # return
