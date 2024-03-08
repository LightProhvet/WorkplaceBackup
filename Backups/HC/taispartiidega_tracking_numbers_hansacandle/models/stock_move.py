# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging

_logger = logging.getLogger()


class StockMove(models.Model):
    _inherit = "stock.move"

    print_tray_label_count = fields.Integer(  # this should also have a better name...
        string="Label count",
        compute="_compute_label_count",
        readonly=False,
        store=True)

    @api.depends("move_line_ids")
    def _compute_label_count(self):
        for record in self:
            lines = record.move_line_ids
            record.print_tray_label_count = len(lines)
            for line in lines:
                if not line.lot_name:
                    record.print_tray_label_count -= 1
