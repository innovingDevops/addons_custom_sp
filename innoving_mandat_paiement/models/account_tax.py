# -*- coding: utf-8 -*-

import time
import math
import re

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = "account.tax"
    _description = 'Tax'

    tax_source = fields.Boolean(string='Prelevement à la source')