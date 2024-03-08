# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    footer_address = fields.Char(translate=True)
    late_fee = fields.Float(string="Fine for delay", default=0.05)