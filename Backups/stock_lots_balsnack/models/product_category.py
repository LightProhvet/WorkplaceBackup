# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "product.category"

    category_code = fields.Char(
        string='Category Code',
        compute="_compute_category_code")

    def _compute_category_code(self):
        for record in self:
            if record.parent_id:
                record.category_code = (record.parent_id.display_name[0] + "/" + record.name[0]).upper()
            else:
                record.category_code = record.display_name[0:2].upper()