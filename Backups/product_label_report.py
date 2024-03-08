# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields
import pytz

import logging

_logger = logging.getLogger(__name__)


def to_integer(dt_time):  # incase this is preferable to int(datetime.utcnow().timestamp())
    return 10000000000 * dt_time.year + 100000000 * dt_time.month + 1000000 * dt_time.day + 10000 * dt_time.hour + 100 * dt_time.minute + dt_time.second


class ReportProductTemplateLabel(models.AbstractModel):
    _inherit = 'report.product.report_producttemplatelabel'

    def _get_report_values(self, docids, data):
        vals = super()._get_report_values(docids, data)
        return vals


class ReportProductTemplateLabelDymo(models.AbstractModel):
    _inherit = 'report.product.report_producttemplatelabel_dymo'

    def _get_report_values(self, docids, data):
        vals = super()._get_report_values(docids, data)
        return vals
