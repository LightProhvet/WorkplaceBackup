# At sale order
def _prepare_procurement_group_vals(self):
    return {
        'name': self.order_id.name,
        'move_type': self.order_id.picking_policy,
        'sale_id': self.order_id.id,
        'partner_id': self.order_id.partner_shipping_id.id, # add original partner here?
    }
def _get_procurement_group(self):
    return self.order_id.procurement_group_id

def _prepare_procurement_values(self, group_id=False):
    """ Prepare specific key for moves or other components that will be created from a stock rule
    comming from a sale order line. This method could be override in order to add other custom key that could
    be used in move/po creation.
    """
    values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
    self.ensure_one()
    # Use the delivery date if there is else use date_order and lead time
    date_deadline = self.order_id.commitment_date or (self.order_id.date_order + timedelta(days=self.customer_lead or 0.0))
    date_planned = date_deadline - timedelta(days=self.order_id.company_id.security_lead)
    values.update({
        'group_id': group_id,
        'sale_line_id': self.id,
        'date_planned': date_planned,
        'date_deadline': date_deadline,
        'route_ids': self.route_id,
        'warehouse_id': self.order_id.warehouse_id or False,
        'partner_id': self.order_id.partner_shipping_id.id,
        'product_description_variants': self.with_context(lang=self.order_id.partner_id.lang)._get_sale_order_line_multiline_description_variants(),
        'company_id': self.order_id.company_id,
        'sequence': self.sequence,
    })
    return values