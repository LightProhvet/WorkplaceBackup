# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    first_delivery_date = fields.Date(string="Delivery Date", compute="_compute_first_delivery_date")
    VAT_directive = fields.Text(compute="_compute_directive")

    @api.depends('invoice_line_ids')
    def _compute_first_delivery_date(self):
        for record in self:
            record.first_delivery_date = False
            if record.invoice_line_ids and record.invoice_line_ids[0].sale_line_ids:
                sale_order = record.invoice_line_ids[0].sale_line_ids[0].order_id
            else:
                continue
            for picking in sale_order.picking_ids.filtered(lambda pick: pick.state == "done"):
                if not record.first_delivery_date:
                    record.first_delivery_date = picking.date_deadline
                elif record.first_delivery_date > picking.date_deadline:
                    record.first_delivery_date = picking.date_deadline

    @api.depends('invoice_line_ids', 'fiscal_position_id', 'partner_id')
    def _compute_directive(self):
        options = ["",
                   "Intra-community 0% supply. Art 28C clause A. 6. Directive - recipient is liable for VAT Article 21.\n",
                   "VAT Directive: 0% supply of services. Reverse charge. Art 196. Directive 2006/112\n",
                   "Intra-community 0% supply. Art 28C clause A. 6. Directive - recipient is liable for VAT Article 21. \nVAT Directive: 0% supply of services. Reverse charge. Art 196. Directive 2006/112"]
        value = 0  # 0 - none, 1 - sellable product/option1, 2 - service/option2, 3- both.
        for record in self:
            if (record.fiscal_position_id.name != "EU Sisene"):
                record.VAT_directive = ''
                continue
            value = 0
            for line in record.invoice_line_ids:
                if value == 3:
                    break
                if line.product_id.type == 'product' or line.product_id.type == 'consu':
                    if value == 2:
                        value = 3
                    else:
                        value = 1
                elif line.product_id.type == 'service':
                    if value == 1:
                        value = 3
                    else:
                        value = 2
            record.VAT_directive = options[value]
