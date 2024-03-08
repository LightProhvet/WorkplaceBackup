# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, Command, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    ###########################################
    # Service : Project and task generation
    def _timesheet_create_task(self, project):
        self.ensure_one()
        values = self._timesheet_create_task_prepare_values(project)
        # # from industry_fsm_sale module
        # template = self.product_id.worksheet_template_id
        # if template:
        #     self = self.with_context(default_worksheet_template_id=template.id) #bad practise, but not the first case of this.

        if self.product_id.task_template_id and self.product_id.service_tracking not in ['project_only', 'no']:
            values['name'] = "%s - %s" % (values['name'], self.product_id.task_template_id.name)
            task = self.product_id.task_template_id.with_context(no_create_folder=True).copy(values)
            #Child tasks seem to be generating appropriately as well.
            if task.child_ids:
                task.child_ids.write({
                    'sale_line_id': self.id,
                    'partner_id': self.order_id.partner_id.id,
                    'email_from': self.order_id.partner_id.email,
                })
                task.child_ids.filtered('parent_id').write({
                    'sale_line_id': self.id,
                    'sale_order_id': self.order_id.id,
                })
            # Avoid new tasks to go to 'Undefined Stage'
            # else:
            #     task.child_ids = self.env['project.task.type'].create({'name': _('New')})
        else:
            task = self.env['project.task'].sudo().create(values)


        # link project as generated by current so line
        self.write({'task_id': task.id})
        # post message on task
        task_msg = _("This task has been created from: %s (%s)", self.order_id._get_html_link(),
                     self.product_id.name)
        task.message_post(body=task_msg)
        return task