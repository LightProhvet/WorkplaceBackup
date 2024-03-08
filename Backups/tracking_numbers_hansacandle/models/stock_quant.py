# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero

import logging

_logger = logging.getLogger()


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None,
                                  strict=False):
        _logger.info(f"\n\n Seeing the world with: {self._context}")
        if self._context.get('use_full_pallets'):  # !!!
            self = self.sudo()
            rounding = product_id.uom_id.rounding
            quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                                  strict=strict)
            reserved_quants = []

            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                # if we want to reserve
                available_quantity = sum(
                    quants.filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=rounding) > 0).mapped(
                        'quantity')) - sum(quants.mapped('reserved_quantity'))
                if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                    raise UserError(_('It is not possible to reserve more products of %s than you have in stock.',
                                      product_id.display_name))
            elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
                # if we want to unreserve
                available_quantity = sum(quants.mapped('reserved_quantity'))
                if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                    raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.',
                                      product_id.display_name))
            else:
                return reserved_quants

            for quant in quants:
                if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                    max_quantity_on_quant = quant.quantity  # - quant.reserved_quantity -> I changed only this row!!!
                    if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                        continue
                    # max_quantity_on_quant = min(max_quantity_on_quant, quantity) #change this as well?
                    quant.reserved_quantity = max_quantity_on_quant
                    reserved_quants.append((quant, max_quantity_on_quant))
                    quantity -= max_quantity_on_quant
                    available_quantity -= max_quantity_on_quant
                else:
                    max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                    quant.reserved_quantity -= max_quantity_on_quant
                    reserved_quants.append((quant, -max_quantity_on_quant))
                    quantity += max_quantity_on_quant
                    available_quantity += max_quantity_on_quant

                if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity,
                                                                                         precision_rounding=rounding):
                    break
            return reserved_quants

        else:
            return super(StockQuant, self)._update_reserved_quantity(product_id, location_id, quantity, lot_id,
                                                                     package_id, owner_id, strict)

        # @api.model
        # def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None,
        #                             strict=False, allow_negative=False):
        #     self = self.sudo()
        #     quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        #     rounding = product_id.uom_id.rounding
        #     if product_id.tracking == 'none':
        #         super()._get_available_quantity(product_id, location_id, lot_id, package_id, owner_id, strict, allow_negative)
        #     else:
        #         availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped('lot_id'))) + ['untracked']}
        #         for quant in quants:
        #             if not quant.lot_id:
        #                 availaible_quantities['untracked'] += quant.quantity - quant.reserved_quantity
        #             else:
        #                 availaible_quantities[quant.lot_id] += quant.quantity - quant.reserved_quantity
        #         if allow_negative:
        #             return sum(availaible_quantities.values())
        #         else:
        #             return sum([available_quantity for available_quantity in availaible_quantities.values() if float_compare(available_quantity, 0, precision_rounding=rounding) > 0])

