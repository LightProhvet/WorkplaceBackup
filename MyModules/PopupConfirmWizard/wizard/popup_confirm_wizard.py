# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class PopupConfirmWizard(models.TransientModel):
    _name = "popup.confirm.wizard"
    _description = "Message wizard to trigger a specific action on confirm"

    @api.model
    def default_get(self, default_fields):
        vals = super(PackageReport, self).default_get(default_fields)
        if self.env.context.get("confirm_name", False):
            vals['name'] = self.env.context.get("confirm_name")
        if self.env.context.get("confirm_message", False):
            vals['message'] = self.env.context.get("confirm_message")
        if self.env.context.get("confirm_model_name", False):
            vals['model_name'] = self.env.context.get("confirm_model_name")
        if self.env.context.get("confirm_active_id", False):
            vals['active_id'] = self.env.context.get("confirm_active_id")
        if self.env.context.get("confirm_function", False):
            vals['function'] = self.env.context.get("confirm_function")
        _logger.info(f"\n\n\n I HAVE: {vals}\n\n\n")
        return vals

    name = fields.Text(string="Name", readonly=True)
    message = fields.Text(string="Message", readonly=True, default="Confirm ")
    model_name = fields.Char(string="Origin Model Name", readonly=True)
    active_id = fields.Integer(comodel_name='ir.model', string="Origin Model", readonly=True)
    function = fields.Char(string="Function to call", readonly=True)

    def wizard_confirm(self):
        _logger.info(F"\n\n i have vals in confirm: {[self.name, self.message, self.model_name, self.active_id, self.function]}")
        if not self.function:
            raise UserError(_(f"The method {action} doesn't exist on the provided model record {model}{record.id}"))
        if not self.model_name:
            raise UserError(_(f"The method {action} doesn't exist on the provided model record {model}{record.id}"))
        model = self.model_name
        record = self.env[model].browse(self.active_id)

        if hasattr(record, self.function):
            getattr(record, self.function)()
        else:
            raise UserError(_(f"The method {action} doesn't exist on the provided model record {model}{record.id}"))

    def get_confirm_action(self, record):
        return {
                'type': 'ir.actions.act_window',
                'name': _('Confirm'),
                'res_model': 'popup.confirm.wizard',
                'res_id': record.id,
                'view_mode': 'form',
                'view_id': self.env.ref('manufacturing_bonus_warmeston.popup_confirm_wizard').id,
                'target': 'new',
                'context': {
                    'default_message': "You have an existing bonus in this month. "
                                       "Do you wish to archive it and create a new bonus for the selected month?",
                    'default_name': "Confirm New Bonus",
                    'default_model_name': record._name,
                    'default_active_id': record.id,
                    'default_function': 'create_manufacturing_bonus',
                }
            }

