# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    picking_quantity = fields.Selection(
        selection_add=[
            ('tray', 'By Label Count')
        ],
        ondelete={'tray': 'set default'},
        default='tray'
    )
    #this is originally in the model. I am overwriting it.
    print_format = fields.Selection(selection="_get_new_print_format_selection", string="Format", default='hansa', required=True)

    def _get_new_print_format_selection(self):
        return [('hansa', 'Hansacandle 1x1')]

    def _prepare_report_data(self):
        xml_id, data = super(ProductLabelLayout, self)._prepare_report_data()

        if self.print_format == 'hansa':
            xml_id = 'tracking_numbers_hansacandle.report_product_template_label_hansa'
        if self.picking_quantity == 'tray' and self.move_line_ids:
            qties = defaultdict(int)
            custom_barcodes = defaultdict(list)
            _logger.info(f'Looking at: {self.move_line_ids}')
            for line in self.move_line_ids:
                if line.lot_id or line.lot_name:
                    custom_barcodes[line.product_id.id].append((line.lot_id.name or line.lot_name, self.custom_quantity))
                    qties[line.product_id.id] = 1
            data['quantity_by_product'] = {}
            data['custom_barcodes'] = custom_barcodes
            _logger.info(f'I have data: {data}')

        return xml_id, data
