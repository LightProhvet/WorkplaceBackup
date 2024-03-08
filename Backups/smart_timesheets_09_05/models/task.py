# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from pydoc import describe
from odoo import api, fields, models, _
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    planned_hours = fields.Float("Initially Planned Hours",
                                 tracking=True,
                                 compute="_compute_planned_hours",
                                 store=True,
                                 readonly=False)
    timesheet_start = fields.Datetime(string='Timer Start Date', copy=False)

    # self.user_timer_id - related timer
    @api.depends("subtask_planned_hours")
    def _compute_planned_hours(self):
        for task in self:
            old_plan = task.planned_hours
            task.planned_hours = old_plan + task.subtask_planned_hours
            # update the remaining hours as well
            task._compute_remaining_hours  # but for some reason this DOES NOT WORK!

    def _action_open_new_timesheet(self, time_spent):
        # self.ensure_one()
        res = super(ProjectTask, self)._action_open_new_timesheet(time_spent)
        res["context"]['default_start_time'] = self.timesheet_start
        res["context"]['default_end_time'] = fields.Datetime.now()
        res["context"]['start_task'] = self._context.get('start_task', None)
        return res

    def _action_interrupt_user_timers_with_stop(self):
        # Interruption is the action called when the timer is stoped by the start of another one
        return self.action_timer_stop()

    def custom_stop_timer_in_progress(self):
        """
        From timer_mixin model "_stop_timer_in_progress". Stop timers instead of pausing them. To avoid unfinished tasks.
        """
        timer = self._get_user_timers().filtered(lambda t: t.is_timer_running)
        if timer:
            model = self.env[timer.res_model].browse(timer.res_id)
            return model.with_context(start_task=self.id)._action_interrupt_user_timers_with_stop()  # changed this row from pause to stop

    def action_timer_start(self):
        self.ensure_one()
        self.timesheet_start = fields.Datetime.now()
        action = self.custom_stop_timer_in_progress()  # we stop the timers before the timer_mixin pauses them.
        if action:
            return action  # and can't start a new task before others are finished.
        super(ProjectTask, self).action_timer_start()

    def _smart_timesheets_close_all_timesheets(self):
        self = self.sudo()
        for timer in self.env['timer.timer'].search([('timer_start', '!=', False)]):
            rounded_hours = 12  # We will calculate it later, but presumably automatically finished task will have 12 h
            wizard = self.env['project.task.create.timesheet'].create({
                'time_spent': rounded_hours,
                'description': 'Automatically finished task. Please update the description.',
                'task_id': timer.res_id,
                'start_time': timer.timer_start,
                'end_time': fields.Datetime.now()
                    })
            user = timer.user_id.name
            _logger.info(f"wizard:{wizard}\n user:  {user}\ntime_spent: {wizard.time_spent}\ntask:{wizard.task_name}")
            if (wizard.end_time-wizard.start_time) > timedelta(hours=12):
                wizard.end_time = wizard.start_time+timedelta(hours=12)
            wizard.save_timesheet_automatically(timer)
