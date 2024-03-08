# -*- coding: utf-8 -*-

from odoo import models, api
from logging import getLogger
from ast import literal_eval

_logger = getLogger(__name__)


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.constrains('date_done')
    def _constrains_date_action_latest(self):
        self.mapped('sale_id')._compute_in_stock()
        self.mapped('sale_id')._compute_sent_to_partner()


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    def _get_action(self, action_xmlid):
        action = self.env['ir.actions.actions']._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name

        default_immediate_tranfer = True
        if self.env['ir.config_parameter'].sudo().get_param('stock.no_default_immediate_tranfer'):
            default_immediate_tranfer = False

        context = {
            'search_default_picking_type_id': [self.id],
            'default_picking_type_id': self.id,
            'default_immediate_transfer': default_immediate_tranfer,
            'default_company_id': self.company_id.id,
        }

        # Replace active_id with integer
        action_context = literal_eval(action['context'].replace('active_id', str(self.id)))
        context = {**action_context, **context}
        action['context'] = context

        return action
