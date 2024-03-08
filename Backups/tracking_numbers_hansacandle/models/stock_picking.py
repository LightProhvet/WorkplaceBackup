# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger()


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def compute_lot_id(self, index):
        # TODO: Server timezone
        lot_name = str(
            self.env['ir.sequence'].next_by_code('stock.lot.serial'))  # + str(index) #[:-2] - to remove seconds
        # _logger.info(f'Lot name is: {lot_name} and index {index}')
        return lot_name
    def action_open_label_layout(self):
        vals = super(StockPicking, self).action_open_label_layout()
        vals['context']['default_picking_quantity'] = 'tray'
        return vals

    def action_assign(self):
        new_self = self.with_context(use_full_pallets=self.picking_type_id.use_full_pallets)
        super(StockPicking, new_self).action_assign()
    def action_click_create_move_lines(self):
        self.ensure_one()
        if not self.picking_type_id.use_create_lots:
            raise UserError(
                f"Current Operation Type ({self.picking_type_id.display_name}) does not support generating new lines.")
        counts = {move: move.print_tray_label_count for move in self.move_ids}
        self.do_unreserve()
        for move in self.move_ids:
            move_lines = move.move_line_ids.filtered(lambda r: r.reserved_qty == 0 or r.qty_done != 0)
            qty_line = 0
            qty_counted = 0
            if move.product_uom_qty and counts[move]:
                qty_line = int(move.product_uom_qty/counts[move])
                qty_counted = move.product_uom_qty
            if move_lines:
                continue
            ctx_self = self.with_context(ref_code=move.product_id.code)
            for line_index in range(counts[move]):
                # TODO CHECK FOR TRACKING
                lot_name = ctx_self.with_context(ref_code=move.product_id.code).compute_lot_id(line_index)
                qty_counted -= qty_line
                if qty_counted < qty_line: #if last line, we add the missing done qty to the last line
                    qty_line += qty_counted
                new_line = self.env['stock.move.line'].create(
                    dict(move._prepare_move_line_vals(),
                         lot_name=lot_name,
                         reserved_uom_qty=qty_line))
        if self.state not in ["draft", "waiting", "confirmed", "cancel"]:
            self.action_assign()
        # TODO if not available, create non reserved lines?
