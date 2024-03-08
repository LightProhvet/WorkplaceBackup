
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    show_sec_unit = fields.Selection(string="Show Secondary unit", selection=[
        ('no', "Don't show"),
        ('only', 'Instead of primary'),
        ('both', 'With primary')
        ])
