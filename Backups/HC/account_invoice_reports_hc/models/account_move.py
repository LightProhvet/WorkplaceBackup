# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    client_order_ref = fields.Char(string="Your Purchase order", copy=False)
