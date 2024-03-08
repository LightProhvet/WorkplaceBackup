# -*- coding: utf-8 -*-

import base64
from odoo import fields, models, api, _
from logging import getLogger

_logger = getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    configurator_relation = fields.Many2one('product.configurator')
    parent_configurator = fields.Many2one('product.configurator')
    template_relation = fields.Many2one('product.configurator.templates')

    weight_per_square_meter = fields.Float(string="Weight per m²")
    configurator_file = fields.Many2many('ir.attachment', string='Configurator attachments')

    configurator_display_name = fields.Char('Display Name')
    configurator_tag_display_name = fields.Char('Tag Display Name')

    inner_template = fields.Boolean(False)
    separate_template = fields.Boolean(False)

    frame_image = fields.Binary('Frame Image', compute="_generate_report_file")

    def _generate_report_file(self):
        for record in self:
            if record.configurator_relation:
                height = 0
                width = 0
                for parameter in record.configurator_relation.template_parameters:
                    if parameter.type_name.name == "Height" and height == 0:
                        height = parameter.float_values
                    if parameter.type_name.name == "Width" and width == 0:
                        width = parameter.float_values


                report_name = "frame_image"
                datas = {
                    'ids': record.id,
                    'model': record._name,
                    'height': height,
                    'width': width,
                    'product': record.name,
                    'report_name': report_name,
                    # 'preview': True,
                }
                try:
                    pdf = self.env.ref('product_configurator.action_image_generator')._render_qweb_pdf(self, data=datas)[0]

                    pdf = base64.b64encode(pdf)

                    record.frame_image = pdf
                except:
                    record.frame_image = False

            else:
                record.frame_image = False


