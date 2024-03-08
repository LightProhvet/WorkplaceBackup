import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.osv import expression
from odoo.tools import float_round
import ast
from collections import defaultdict
import json
import logging

_logger = logging.getLogger(__name__)

class ProductSecondaryUnit(models.Model):
    _inherit = "product.secondary.unit"

    def init(self):
        odoo.addons.product_secondary_unit_bundles_template._auto_init_secondary_units_bundles(self.env.cr, self.env.registry)
        return super().init()
