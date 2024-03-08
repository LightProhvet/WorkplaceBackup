# -*- coding: utf-8 -*-

from odoo import models

import logging


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_generate_serial(self):
        self = self.with_context(ref_code=self.product_id.default_code, cat_code=self.product_id.categ_id.category_code)
        vals = super(MrpProduction, self).action_generate_serial()
        return vals
