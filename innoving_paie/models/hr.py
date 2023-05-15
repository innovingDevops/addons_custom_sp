# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
import math

from odoo import api, fields, models, SUPERUSER_ID, _
#from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from mock.mock import self
from dateutil.relativedelta import relativedelta



class Employee(models.Model):

    _name = "hr.employee"
    _inherit = "hr.employee"
    
    echelon = fields.Char(string="Echelon")
    hr_grade_id = fields.Many2one('hr.grade',string='Grade')
    hr_echelon_id = fields.Many2one('hr.echelon',string='Echelon')
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')

    @api.onchange('account_fonctionnel_id')
    def _onchange_account_fonctionnel_id(self):
        if self.account_fonctionnel_id:
            self.account_fonctionnel_code=self.account_fonctionnel_id.code
            return {}