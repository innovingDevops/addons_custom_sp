# -*- coding: utf-8 -*-

import base64
import datetime
import hashlib
import pytz
import threading

from email.utils import formataddr
from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.osv.orm import browse_record
from datetime import datetime
from datetime import date

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import html_translate
from email.policy import default

from odoo.tools.amount_to_text_frr import amount_to_text_fr


class InnovingHrPayslipMandatSalaire(models.TransientModel):
    _name = 'innoving.hr.payslip.mandat.salaire'
    _description = "Innoving Hr payslip mandat salaire wizard"
    
    
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')
    periode_id = fields.Many2one('periode', string='Période')
    amount_lettre = fields.Char(string='Montan en lettre')
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
   
    
    
     
    @api.onchange('date_from','date_to')
    def onchange_periode_date(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_('Attention, vérifier les dates !')) 
        return {}
    
    @api.onchange('periode_id')
    def onchange_periode_id(self):
        if self.periode_id:
            periode = self.env['periode'].search([('id','=',self.periode_id.id)])
            if periode.id:
                #self.ticket_html = self.req_ticket_html()
                self.date_from = periode.date_from
                self.date_to = periode.date_to
        return {}

    @api.onchange('account_fonctionnel_id')
    def _onchange_account_fonctionnel_id(self):
        if self.account_fonctionnel_id:
            self.account_fonctionnel_code=self.account_fonctionnel_id.code
            return {}
    
    @api.multi
    def print_report(self):
        domain = []
        date_from = self.date_from
        date_to = self.date_to
        index = 0
        account_fonctionnel_code = self.account_fonctionnel_code
            
        if date_from:
            domain += [('date_from', '>=', date_from)]
        if date_to:
            domain += [('date_to', '<=', date_to)]
        if account_fonctionnel_code:
            domain += [('account_fonctionnel_code', '=', account_fonctionnel_code)]
  
        #payslips = self.env['hr.payslip'].search(domain)
        payslips = self.env['hr.payslip'].search_read(domain)
        #raise UserError(_('%s') % (payslips[0]['id']))
        payslips_list =  []
        
        for payslip in payslips:
            index +=1
            
            domain2 = [('slip_id', '=', payslip['id'])]
            payslips_line = self.env['hr.payslip.line'].search_read(domain2)
           
            if payslip['struct_id'][1] == "MAIRIE SPY":
                amount_lettre = amount_to_text_fr(payslips_line[24]['total'],'Francs CFA')
                salaire = payslips_line[24]['total']

            if payslip['struct_id'][1] == "RESPONSABLE MAIRIE SPY":
                amount_lettre = amount_to_text_fr(payslips_line[2]['total'],'Francs CFA')
                salaire = payslips_line[2]['total']
            
            vals = {
                'employee_id': payslip['employee_id'][1],
                'contract_id': payslip['contract_id'],
                'account_fonctionnel_code': payslip['account_fonctionnel_code'],
                'bank_id': payslip['bank_id'][1],
                'job_id': payslip['job_id'][1],
                'objet': payslip['objet'],
                'numero_compte': payslip['numero_compte'],
                'analytic_account_ref': payslip['analytic_account_ref'],
                'date_from': payslip['date_from'],
                'date_to': payslip['date_to'],
                'number': payslip['number'],
                'index': index,
                'amount_lettre': amount_lettre,
                'line_amount': salaire,
            }
            #raise UserError(_('%s') % (payslip['numero_compte']))
            payslips_list.append(vals)

            #raise UserError(_('%s') % (payslip['numero_compte_id'][1]))
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }  
        #raise UserError(_('%s') % (payslips['somme_cnps_agent']))  
        return self.env.ref('innoving_paie.action_report_innoving_paie_mandat_salaire_report').report_action(self, data=data)