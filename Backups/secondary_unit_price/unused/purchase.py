from odoo import models, fields, api, _


# from mrp_secondary_unit
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res.update({
            'secondary_uom_id': self.secondary_uom_id.id,
            'secondary_uom_qty': self.secondary_uom_qty,
        })
        return res
