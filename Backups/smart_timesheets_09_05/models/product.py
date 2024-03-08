# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # service_tracking = fields.Selection(
    #     selection_add=[
    #         ("task_from_template", "Task from template")],)

    task_template_id = fields.Many2one(
        'project.task', 'Task Template', company_dependent=True, copy=True,
        domain="[('company_id', '=', current_company_id)]")

    # @api.constrains('project_id', 'project_template_id', 'task_template_id')
    # def _check_project_and_template(self):
    #     """ NOTE 'service_tracking' should be in decorator parameters but since ORM check constraints twice (one after setting
    #         stored fields, one after setting non stored field), the error is raised when company-dependent fields are not set.
    #         So, this constraints does cover all cases and inconsistent can still be recorded until the ORM change its behavior.
    #     """
    #     super(ProductTemplate, self)._check_project_and_template()

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        super()._onchange_service_tracking()
        if self.service_tracking == 'no':
            self.task_template_id = False
        elif self.service_tracking == 'project_only':
            self.task_template_id = False

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        super()._onchange_service_tracking()
        if self.service_tracking == 'no':
            self.task_template_id = False
        elif self.service_tracking == 'project_only':
            self.task_template_id = False

