# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_time = fields.Datetime(string='Start Date', copy=False)
    end_time = fields.Datetime(string='Finish Date', copy=False)

    @api.onchange('end_time')
    def onchange_end(self):
        for line in self:
            if line.end_time and line.unit_amount:
                if line.end_time > fields.Datetime.now():
                    raise UserError(_("Cannot have finished a task in the future. Please set an end time in the past."))
                line.unit_amount = self.task_id._get_rounded_hours(
                    (line.end_time - line.start_time).total_seconds() / 60)

    @api.onchange('unit_amount')
    def onchange_done(self):
        for line in self:
            line.end_time = line.start_time + timedelta(hours=line.unit_amount)

    @api.onchange('start_time')
    def onchange_start(self):
        for line in self:
            if line.start_time and line.unit_amount:
                if line.start_time > fields.Datetime.now():
                    raise UserError(_("Cannot have started a task in the future. Please set a start time in the past."))
                line.end_time = line.start_time + timedelta(hours=line.unit_amount)

    @api.constrains('start_time, end_time')
    def _check_start_end_relation(self):
        for record in self:
            if not record.start_time:
                raise ValidationError(_("Cannot remove start date from timesheet. Every action had a beginning."))
            if not record.end_time:
                raise ValidationError(_("Cannot remove end date from timesheet. Every action had an end."))
            if record.end_time > fields.Datetime.now():
                raise ValidationError(_("Cannot have finished a task in the future. Please set an end time in the past."))
            if record.start_time > record.end_time:
                raise ValidationError(_("Cannot set start to be later than end. Every action began before it ended."))

    @api.constrains('unit_amount')
    def _constrains_time_spent(self):
        for record in self:
            if record.unit_amount > 12:
                raise ValidationError(_("Task timesheets are constrained to one day - you cannot/should not have done a task for over 12 h continously."))
