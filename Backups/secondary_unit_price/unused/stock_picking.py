
from odoo import models, fields


# This is "used" in standwood - stock_secondary_unit_extended. Would need to be implemented on all models, if desired.
class StockPicking(models.Model):
    _inherit = "stock.picking"

    show_sec_unit = fields.Selection(string="Show Secondary unit", selection=[
        ('no', "Don't show"),
        ('only', 'Instead of primary'),
        ('both', 'With primary')
        ])
