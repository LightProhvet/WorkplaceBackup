# -*- coding: utf-8 -*-


from odoo import models, fields


class Partner(models.Model):
    _inherit = "product.product"

    is_pallet = fields.Boolean()
