from odoo import models, fields, api, _


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    @api.model
    def _default_footer_address(self):
        company = self.env.company
        address = company.footer_address or company.partner_id._display_address(without_company=True).replace('\n', ', ')
        return address

    company_registry = fields.Char(related='company_id.company_registry', readonly=True)
    footer_address = fields.Char(related='company_id.footer_address', readonly=False, default=_default_footer_address)

