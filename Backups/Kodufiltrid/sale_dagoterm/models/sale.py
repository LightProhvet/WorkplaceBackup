# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object')
    contract_id = fields.Many2one(
        comodel_name='res.partner.contract',
        domain="[('partner_id', '=', partner_id)]",
        string='Contract')
    in_production = fields.Date(
        string='In production',
        compute='_compute_in_production',
        store=True,
        copy=False)
    in_stock = fields.Date(
        string='In stock',
        compute='_compute_in_stock',
        store=True,
        copy=False)
    sent_to_partner = fields.Date(
        string='Sent to partner',
        compute='_compute_sent_to_partner',
        store=True,
        copy=False)
    date_action_latest = fields.Char(
        string='Latest Action',
        compute='_find_latest_action',
        store=True,
        readonly=True)
    partner_route_id = fields.Many2one(
        comodel_name='stock.location.route',
        string='Partner Route')

    @api.depends('picking_ids.date_done')
    def _compute_sent_to_partner(self):
        for record in self:
            sent_to_partner = False
            dates = record.picking_ids.filtered(
                lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done'
            ).sorted(lambda m: m.date_done).mapped('date_done')
            if dates:
                sent_to_partner = dates[0]
            record.sent_to_partner = sent_to_partner

    @api.depends('picking_ids.date_done')
    def _compute_in_stock(self):
        for record in self:
            in_stock = False
            dates = record.picking_ids.filtered(
                lambda p: p.picking_type_id.code == 'internal' and p.state == 'done'
            ).sorted(lambda m: m.date_done).mapped('date_done')
            if dates:
                in_stock = dates[0]
            record.in_stock = in_stock

    def _compute_in_production(self):
        # OVERRIDE in dagoterm_bom
        for record in self:
            record.in_production = False

    @api.depends('in_production', 'in_stock', 'sent_to_partner')
    def _find_latest_action(self):
        field_names = self.fields_get(allfields=['in_production', 'in_stock', 'sent_to_partner'])
        for record in self:
            if record.sent_to_partner:
                record.date_action_latest = field_names['sent_to_partner']['string']
            elif record.in_stock:
                record.date_action_latest = field_names['in_stock']['string']
            elif record.in_production:
                record.date_action_latest = field_names['in_production']['string']
            else:
                record.date_action_latest = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if self.partner_id and self.partner_id.sale_route_id:
            self.partner_route_id = self.partner_id.sale_route_id.id
        else:
            self.partner_route_id = False

    def recompute_lines(self):
        tax_obj = self.env['account.tax']
        for line in self.order_line:
            prod = line.product_id
            if prod:
                display_price = line._get_display_price(prod)
                prod_tax = prod.taxes_id
                order_tax = line.tax_id
                company = line.company_id

                line.price_unit = tax_obj._fix_tax_included_price_company(
                    display_price, prod_tax, order_tax, company)
                line.name = prod.get_product_multiline_description_sale()

    def print_quotation_html(self):
        return self.env.ref('sale_dagoterm.action_report_saleorder_html') \
            .with_context({'discard_logo_check': True}).report_action(self)

    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(SaleOrder, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        return res

    def action_confirm(self):
        for prod in self.order_line.product_id:
            if prod.bom_ids or prod.purchase_ok or prod.type == 'service':
                continue
            raise UserError('Product {} has no bill of materials.'.format(prod.name))
        return super(SaleOrder, self).action_confirm()
