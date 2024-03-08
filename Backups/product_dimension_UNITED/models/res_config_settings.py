# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_dimension_locks = fields.Boolean(
        string="Enable Dimension Locks",
        help='Set dimension locks to avoid unintended template and variant differences.',
        # config_parameter='l10n_ee.accunting_date_to_invoice_date'
    )

    use_package_dimension = fields.Boolean(
        string="Enable package dimensions",
        help="Puts dimensions in a separate sheet and new dimensions (volume, diameter) and dimension categories (package, BulkBox)",
        # config_parameter='l10n_ee.accunting_date_to_invoice_date'
    )

    product_dimension_in_foot = fields.Selection(
        selection=[
            ('0', 'Meter'),
            ('1', 'Foot'),
            ('2', 'Centimeter'),
        ],
        string='Dimension unit of measure',
        config_parameter='product.dimension_in_foot',
        default='2')

    product_volume_volume_in_cubic_feet = fields.Selection(selection_add=[('2', 'Cubic Centimeters')], default='2')
    product_weight_in_lbs = fields.Selection(selection_add=[('2', 'Gram')], default='2')
