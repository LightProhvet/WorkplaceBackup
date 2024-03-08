# -*- coding: utf-8 -*-

from odoo import fields, models

import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_generate_serial(self):
        self = self.with_context(ref_code=self.product_id.code)
        vals = super(MrpProduction, self).action_generate_serial()
        return vals
