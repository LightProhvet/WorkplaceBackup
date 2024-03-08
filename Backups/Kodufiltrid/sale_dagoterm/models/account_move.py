# -*- coding: utf-8 -*-

from odoo import api, fields, models
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Sale Partner Object')
    object_name = fields.Char(
        related='object_id.name',
        string='Object Name')
    contract_id = fields.Many2one(
        comodel_name='res.partner.contract',
        domain="[('partner_id', '=', partner_id)]",
        string='Contract')
    contract_name = fields.Char(
        related='contract_id.name',
        string='Contract Name')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('invoice_origin', False):
                dom = [('name', '=', vals['invoice_origin'])]
                order = self.env['sale.order'].search(dom, limit=1)
                if order:
                    if order.partner_object_id:
                        vals['object_id'] = order.partner_object_id.id
                    if order.contract_id:
                        vals['contract_id'] = order.contract_id.id
        return super(AccountMove, self).create(vals_list)

    def print_invoice_html(self):
        view_id = 'sale_dagoterm.action_report_invoice_html'
        return self.env.ref(view_id).report_action(self)

    def action_recompute_tax_grid(self):
        active_ids = self.env.context.get('active_ids', [])
        for move in self.browse(active_ids):
            move.button_cancel()
            move.button_draft()
            move.with_context(check_move_validity=False)._recompute_tax_lines()
            move.action_post()

    def action_post(self):
        res = super(AccountMove, self).action_post()

        if self.move_type in ['out_invoice', 'out_refund']:
            subscribe_partner_ids = self.partner_id.message_partner_ids.ids

            unsubscribe_partners = list()
            for current_follower_id in self.message_partner_ids.ids:
                if current_follower_id != self.partner_id.id \
                        and current_follower_id != self.create_uid.partner_id.id \
                        and current_follower_id not in subscribe_partner_ids:
                    unsubscribe_partners.append(current_follower_id)

            if unsubscribe_partners:
                self.message_unsubscribe(unsubscribe_partners)

            self.message_subscribe([
                p_id for p_id in subscribe_partner_ids
                if p_id not in self.sudo().message_partner_ids.ids
            ])

        return res

    # def action_fix_display_type(self):
    #     active_ids = self.env.context.get('active_ids', [])
    #     for move in self.browse(active_ids):
    #         move.button_cancel()
    #         move.button_draft()
    #         tax_ids = False
    #         account_id = 113
    #         if move.invoice_line_ids and move.invoice_line_ids.tax_ids:
    #             tax_ids = [move.invoice_line_ids.tax_ids.ids[0]]
    #         for line in move.invoice_line_ids:
    #             if line.display_type and line.product_id:
    #                 if not tax_ids:
    #                     taxes_id = line.product_id.taxes_id
    #                     if taxes_id:
    #                         tax_ids = taxes_id.ids

    #                 line.with_context(check_move_validity=False).write({
    #                     'display_type': False,
    #                     'account_id': account_id,
    #                 })
    #                 line.with_context(check_move_validity=False).write({
    #                     'tax_ids': [(6, 0, tax_ids)],
    #                 })
    #         move.with_context(check_move_validity=False)._move_autocomplete_invoice_lines_values()
    #         move.action_post()
