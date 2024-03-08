# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    purchase_delivery_carrier_id = fields.Many2one('delivery.carrier', company_dependent=True,
                                                   string="Purchase Delivery Method",
                                                   help="Default delivery method used in Purchase orders.")
                                                    # compute='_compute_delivery_carrier',
                                                    # related="parent_id.purchase_delivery_carrier_id",
                                                    # readonly=False,

    # parent_purchase_delivery_carrier_id = fields.Many2one('delivery.carrier', company_dependent=True,
    #                                                       string="Parent Delivery Method",
    #                                                       related="parent_id.purchase_delivery_carrier_id",
    #                                                       readonly=True,
    #                                                       invisible=True)

    # @api.depends('parent_purchase_delivery_carrier_id')
    # def _compute_delivery_carrier(self):
    #     _logger.info(f"\n\n\nSTARTING PARENT COMPUTE")
    #     for partner in self:
    #         if not partner.purchase_delivery_carrier_id:
    #             partner.purchase_delivery_carrier_id = partner.parent_purchase_delivery_carrier_id
    #
    # @api.onchange('parent_purchase_delivery_carrier_id')
    # def _onchange_parent_delivery_carrier(self):
    #     _logger.info(f"\n\n\nSTARTING ONCHANGE!!!")
    #     for partner in self:
    #         if not partner.purchase_delivery_carrier_id and partner.parent_purchase_delivery_carrier_id:
    #             partner.purchase_delivery_carrier_id = partner.parent_purchase_delivery_carrier_id

    @api.onchange('purchase_delivery_carrier_id')
    def _onchange_delivery_carrier(self):
        for partner in self:
            # child_ids_to_update = partner.child_ids.filtered(lambda c: (not c.purchase_delivery_carrier_id))
            # child_ids_to_update.write({
            #             "purchase_delivery_carrier_id": partner.purchase_delivery_carrier_id.id
            #         })

            for child in partner.child_ids:
                if not child.purchase_delivery_carrier_id and partner.purchase_delivery_carrier_id:
                    child_to_update = self.env['res.partner'].browse(child.id)
                    child_to_update.write({
                        "purchase_delivery_carrier_id": partner.purchase_delivery_carrier_id.id
                    })
                    _logger.info("\nCHANGE IS SUCCESSFULL!!!!")
                    # child.purchase_delivery_carrier_id = partner.purchase_delivery_carrier_id

