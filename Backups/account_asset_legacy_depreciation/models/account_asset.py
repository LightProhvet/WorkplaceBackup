import pdb
import datetime
from _decimal import Decimal
from unicodedata import decimal

from dateutil.relativedelta import relativedelta

from odoo import models, fields, _, api
from odoo.exceptions import UserError
from logging import getLogger

from odoo.tools import float_is_zero

_logger = getLogger(__name__)


class AccountAssetInherit(models.Model):
    _inherit = 'account.asset'

    use_original_date = fields.Boolean(string="Acquisition Date for Depreciation")