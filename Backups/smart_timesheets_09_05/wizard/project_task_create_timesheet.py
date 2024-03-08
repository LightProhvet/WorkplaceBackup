# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class ProjectTaskCreateTimesheet(models.TransientModel):
    _inherit = 'project.task.create.timesheet'

    end_time = fields.Datetime(string='End Date')  # default=lambda self: self.env.context.get('default_start_time', 0)
    start_time = fields.Datetime(string='Start Date')  # readonly?
    task_name = fields.Char(string="Task name", compute='_compute_task_name')  #

    @api.depends('task_id.name', 'task_id.project_id.name')
    def _compute_task_name(self):
        for record in self:
            if record.task_id and record.task_id.project_id:
                task_name = f"{record.task_id.project_id.name} - {record.task_id.name}"
            elif record.task_id:
                task_name = record.task_id.name
            else:
                task_name = False  # should not happen
            record.task_name = task_name

    def save_timesheet(self):
        values = super(ProjectTaskCreateTimesheet, self).save_timesheet()
        for value in values:  # should be one
            value.end_time = self.end_time
            value.start_time = self.start_time  # value.task_id.timesheet_start
            value.unit_amount = self.time_spent  # this used to be just minutes now it is actually formated time.
        # start the timer for task that triggered the stop, using context
        starting_task_id = self.env.context.get('start_task', None)
        if starting_task_id:
            task = self.env['project.task'].search([('id', '=', starting_task_id)])
            task.action_timer_start()
        return values

    def save_timesheet_automatically(self, timer):
        values = {
            'task_id': self.task_id.id,
            'project_id': self.task_id.project_id.id,
            'date': fields.Date.context_today(self),
            'name': self.description,  # add some dynamic information as well?
            'user_id': timer.user_id.id,
            'unit_amount': self.task_id._get_rounded_hours((self.end_time - self.start_time).total_seconds() / 60),
            'end_time': self.end_time,
            'start_time': self.start_time
        }
        timer.unlink()
        return self.env['account.analytic.line'].create(values)

    @api.onchange('end_time')
    def onchange_end(self):
        for create in self:
            if create.end_time and create.start_time:
                if create.end_time > fields.Datetime.now() + timedelta(minutes=5):
                    raise UserError(_("Cannot confirm a task in the future. Please set an end time in the past."))
                create.time_spent = self.task_id._get_rounded_hours(
                    (create.end_time - create.start_time).total_seconds() / 60)

    @api.onchange('time_spent')
    def onchange_done(self):
        for create in self:
            # could start_time be None?
            create.end_time = create.start_time + timedelta(hours=create.time_spent)

    @api.constrains('time_spent')
    def _constrains_time_spent(self):
        for record in self:
            if record.time_spent > 12:
                raise ValidationError(_("Task timesheets are constrained to one day - you cannot/should not have done a task for over 12 h continously."))
