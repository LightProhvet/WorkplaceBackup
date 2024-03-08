# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_localhost_routing = fields.Boolean(
        string="Mock RabbitMQ",
        config_parameter='pika_rabbitMQ_linker.use_localhost_routing'
    )
