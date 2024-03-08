# -*- coding: utf-8 -*-

from odoo import fields, models
from logging import getLogger

_logger = getLogger(__name__)


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    standard_price = fields.Float(
        string='Cost',
        digits='Product Price')
    invoice_lines = fields.Many2many(
        'account.move.line',
        'sale_order_line_invoice_rel',
        'order_line_id',
        'invoice_line_id'
    )

    _depends = {
        'sale.order.line': ['id', 'product_uom_qty', 'purchase_price'],
    }

    def _select(self):
        return super()._select() + """
            , CASE
                WHEN line.product_id IS NOT NULL
                THEN COALESCE(SUM(sol.purchase_price * sol.product_uom_qty))
                ELSE 0
            END as standard_price
        """

    def _from(self):
        return super()._from() + """
            INNER JOIN sale_order_line_invoice_rel AS solir ON (solir.invoice_line_id = line.id)
            INNER JOIN sale_order_line AS sol ON (solir.order_line_id = sol.id)
        """

    def _group_by(self):
        return """
            GROUP BY
                line.id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.analytic_account_id,
                line.journal_id,
                line.company_id,
                line.currency_id,
                line.partner_id,
                move.name,
                move.state,
                move.move_type,
                move.amount_residual_signed,
                move.amount_total_signed,
                move.partner_id,
                move.invoice_user_id,
                move.fiscal_position_id,
                move.payment_state,
                move.invoice_date,
                move.invoice_date_due,
                move.invoice_payment_term_id,
                move.partner_bank_id,
                uom_template.id,
                uom_line.factor,
                template.categ_id,
                (COALESCE(partner.country_id, commercial_partner.country_id)),
                move.team_id,
                currency_table.rate,
                sol.purchase_price,
                sol.product_uom_qty
        """

    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())

    # _depends = {
    #     'ir.property': ['id', 'res_id', 'name', 'company_id'],
    #     'res.company': ['id'],
    # }

    # def _select(self):
    #     return super()._select() + """
    #         , CASE
    #             WHEN line.product_id IS NOT NULL
    #             THEN COALESCE(SUM(irp_standard_price.value_float * line.quantity))
    #             ELSE 0
    #         END as standard_price
    #     """

    # def _from(self):
    #     return super()._from() + """
    #         INNER JOIN res_company AS comp ON (comp.id = line.company_id or line.company_id is null)
    #         LEFT JOIN ir_property AS irp_standard_price ON (
    #             irp_standard_price.res_id = CONCAT('product.product,', product.id)
    #             AND irp_standard_price.name = 'standard_price'
    #             AND irp_standard_price.company_id = comp.id
    #         )
    #     """

    # def _group_by(self):
    #     return """
    #         GROUP BY
    #             line.id,
    #             line.move_id,
    #             line.product_id,
    #             line.account_id,
    #             line.analytic_account_id,
    #             line.journal_id,
    #             line.company_id,
    #             line.currency_id,
    #             line.partner_id,
    #             move.name,
    #             move.state,
    #             move.move_type,
    #             move.amount_residual_signed,
    #             move.amount_total_signed,
    #             move.partner_id,
    #             move.invoice_user_id,
    #             move.fiscal_position_id,
    #             move.payment_state,
    #             move.invoice_date,
    #             move.invoice_date_due,
    #             move.invoice_payment_term_id,
    #             move.partner_bank_id,
    #             uom_template.id,
    #             uom_line.factor,
    #             template.categ_id,
    #             (COALESCE(partner.country_id, commercial_partner.country_id)),
    #             move.team_id,
    #             irp_standard_price.value_float,
    #             line.quantity,
    #             currency_table.rate
    #     """

    # @property
    # def _table_query(self):
    #     return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())
