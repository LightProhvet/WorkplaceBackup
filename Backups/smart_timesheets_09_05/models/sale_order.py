# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_test_task(self):
        for order in self:
            for line in order.order_line:
                #line._timesheet_create_task(project=map_sol_project[so_line.id])
                line._timesheet_service_generation()
                return
        return
