from odoo import api, models, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for line in self.order_line:
            if not line.secondary_uom_id:
                raise ValidationError(_(f"Product {line.product_id.name} doesn't have a secondary unit. You can not confirm a sale order without secondary units."))
        return super().action_confirm()
