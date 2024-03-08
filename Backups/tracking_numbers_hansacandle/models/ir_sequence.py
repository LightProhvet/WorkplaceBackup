# -*- coding: utf-8 -*-


from odoo import api, fields, models

import logging


def to_integer(dt_time):  # incase this is preferable to int(datetime.utcnow().timestamp())
    return 10 ** 10 * dt_time.year + 10 ** 8 * dt_time.month + 10 ** 6 * dt_time.day + 10 ** 4 * dt_time.hour + \
        100 * dt_time.minute + dt_time.second


_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.model
    def next_by_code(self, sequence_code, sequence_date=None):
        """You need to add context 'ref code' for this function to write to change the result
        """
        # TODO: set up the sequence with the date already, only add prod code here
        vals = super(IrSequence, self).next_by_code(sequence_code, sequence_date)

        return f"{self.env.context.get('ref_code', '')}{vals}"
