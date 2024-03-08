# -*- coding: utf-8 -*-


from odoo import api, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.model
    def next_by_code(self, sequence_code, sequence_date=None):
        """You need to add context 'ref code' and 'cat_code' for this function to write to change the result
        """
        vals = super(IrSequence, self).next_by_code(sequence_code, sequence_date)

        return f"{self.env.context.get('cat_code', '')}/{self.env.context.get('ref_code', '')}/{vals}"
