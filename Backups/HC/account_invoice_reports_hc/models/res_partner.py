# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    fax = fields.Char(tracking=6)
