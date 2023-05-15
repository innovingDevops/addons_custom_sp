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

    _name = "hr.contract"
    _inherit = "hr.contract"
    
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    account_analytic_id = fields.Many2one('account.analytic.account','Compte Analytique')
    budget_id = fields.Many2one('crossovered.budget','Budget')
    chapitre = fields.Char(string='Chapitre')
    compte = fields.Char(string='Compte')  
    #copy_compte_ok = fields.Boolean(string="Copy Compte OK")
    #copy_ok = fields.Boolean(string="Copy Compte OK") 
    copy_cpt_ok = fields.Boolean(string="Copy Compte OK") 
    
    @api.onchange('account_fonctionnel_id')
    def _onchange_account_fonctionnel_id(self):
        if self.account_fonctionnel_id:
            self.account_fonctionnel_code=self.account_fonctionnel_id.code
            return {}


    @api.multi
    def gen_compte(self, force=False):
        for contract in self.env['hr.contract'].search([('copy_cpt_ok','=',False)],limit=400):
            employee_id = self.env['hr.employee'].browse([contract.employee_id.id]).write({
                'account_fonctionnel_id':contract.account_fonctionnel_id.id,
                'account_fonctionnel_code':contract.account_fonctionnel_id.code,
            })
            self.env['hr.employee'].browse([contract.employee_id.id]).write({'copy_cpt_ok':True,})

    