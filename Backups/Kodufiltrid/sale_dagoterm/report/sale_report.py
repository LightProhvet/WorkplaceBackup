# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger

_logger = getLogger(__name__)


class SaleReport(models.Model):
    _inherit = 'sale.report'

    partner_object_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('object', '=', True)],
        string='Object')
    standard_price = fields.Float(
        string='Cost',
        digits='Product Price')

    def _group_by_sale(self, groupby=''):
        groupby_ = super()._group_by_sale(groupby)
        groupby_ += ''',
            l.purchase_price,
            l.product_uom_qty,
            u.factor,
            u2.factor
        '''
        return groupby_

    def _select_sale(self, fields={}):
        select_ = super()._select_sale(fields=fields)
        select_ += ''',
            CASE WHEN l.product_id IS NOT NULL THEN COALESCE(SUM(l.purchase_price * l.product_uom_qty / u.factor * u2.factor)) ELSE 0 END as standard_price'''
        return select_

    # def _from_sale(self, from_clause=''):
    #     from_ = super()._from_sale(from_clause)
    #     from_ += '''
    #         INNER JOIN res_company AS comp ON (comp.id = l.company_id or l.company_id is null)
    #         LEFT JOIN ir_property AS irp_standard_price ON (
    #             irp_standard_price.res_id = CONCAT('product.product,', p.id)
    #             AND irp_standard_price.name = 'standard_price'
    #             AND irp_standard_price.company_id = comp.id
    #         )'''
    #     return from_

    # def _group_by_sale(self, groupby=''):
    #     groupby_ = super()._group_by_sale(groupby)
    #     groupby_ += ''',
    #         irp_standard_price.value_float,
    #         l.product_uom_qty,
    #         u.factor,
    #         u2.factor
    #     '''
    #     return groupby_

    # def _select_sale(self, fields={}):
    #     select_ = super()._select_sale(fields=fields)
    #     select_ += ''',
    #         CASE WHEN l.product_id IS NOT NULL THEN COALESCE(SUM(irp_standard_price.value_float * l.product_uom_qty / u.factor * u2.factor)) ELSE 0 END as standard_price'''
    #     return select_
