# -*- coding: utf-8 -*-

from odoo import fields, models, api
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    object = fields.Boolean(
        string='Objekt')
    contract_ids = fields.One2many(
        comodel_name='res.partner.contract',
        inverse_name='partner_id',
        string='Contracts')
    sale_route_id = fields.Many2one(
        comodel_name='stock.location.route',
        domain=[('sale_selectable', '=', True)],
        string='Default Route')

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'street', 'street2', 'city')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    def _display_address(self, without_company=False):
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        }

        if self.env.user.company_id.partner_id.id == self.id:
            address_format = self._get_reg_number_address_format()
            args.update({'reg_number': self._get_reg_number()})
        else:
            address_format = self._get_default_address_format()

        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(city)s, %(state_name)s, %(zip)s\n%(country_name)s"

    @api.model
    def _get_reg_number_address_format(self):
        return "%(reg_number)s\n%(street)s\n%(street2)s\n%(city)s, %(state_name)s, %(zip)s\n%(country_name)s"

    @api.model
    def _get_reg_number(self):
        if self.reg_number:
            return u'Reg kood: {}'.format(self.reg_number)
        return ''

    def _get_name(self):
        partner = self
        name = partner.name or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)

        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)

        if self._context.get('show_address'):
            # name = name + "\n" + partner._display_address()
            # Added without company otherwise its doubled
            name = name + "\n" + partner._display_address(without_company=True)

        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')

        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')

        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)

        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')

        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)

        if self._context.get('display_website') and self.env.user.has_group('website.group_multi_website'):
            if self.website_id:
                name += ' [%s]' % self.website_id.name

        return name

    def name_get(self):
        res = super(ResPartner, self).name_get()

        for partner in self:
            if partner.object:
                display_name = ""

                if partner.name:
                    display_name += partner.name
                if partner.street:
                    display_name += ", " + partner.street
                if partner.street2:
                    display_name += ", " + partner.street2
                if partner.city:
                    display_name += ", " + partner.city

                res.append((partner.id, display_name))
            else:
                name = partner._get_name()
                res.append((partner.id, name))

        return res


class ResPartnerContract(models.Model):
    _name = 'res.partner.contract'
    _description = 'Partner Contracts'

    name = fields.Char(
        required=True,
        string='Name')
    active = fields.Boolean(
        string='Active',
        default=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string='Partner')
    date_from = fields.Date(
        string='From')
    date_to = fields.Date(
        string='To')
