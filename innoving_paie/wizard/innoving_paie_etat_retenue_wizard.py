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

from odoo.tools.amount_to_text_frr import amount_to_text_fr


class InnovingHrPayslipEtatRetenue(models.TransientModel):
    _name = 'innoving.hr.payslip.etat.retenue'
    _description = "Innoving Hr payslip etat retenue wizard"
    
    titre = fields.Selection(string="Titre", selection=[
        ('CNPS AGENT', 'CNPS AGENT'),
        ('CNPS PATRONALE', 'CNPS PATRONALE'),
        ('MUTUELLE', 'MAMA SP'),
        ('ASSURANCE', 'SCA-INTER A'),
        ('IS', 'IS'),])
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    periode_id = fields.Many2one('periode', string='Période')
    somme_salaire_base = fields.Float(string='Somme salaires')  
    somme_retenue = fields.Float(string='Somme Retenues')  
    amount_lettre = fields.Char(string='Montant en lettre') 
    barre = fields.Selection(string="Barre", selection=[
        ('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),])  
    compte = fields.Char(string='Compte') 
    chapitre = fields.Char(string='Chapitre') 
    
     
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
        account_fonctionnel_code = self.account_fonctionnel_code
        barre = self.barre
        somme_salaire = 0.0
        somme_amount = 0.0
        index = 0
            
        if date_from:
            domain += [('date_from', '>=', date_from)]
        if date_to:
            domain += [('date_to', '<=', date_to)]
        if account_fonctionnel_code:
            domain += [('account_fonctionnel_code', '=', account_fonctionnel_code)]
        #if barre:
            #domain += [('analytic_account_ref', '=', barre)]
            
        #payslips = self.env['hr.payslip'].search(domain)
        payslips = self.env['hr.payslip'].search_read(domain)
        #raise UserError(_('%s') % (payslips[0]['id']))
        payslips_list =  []
        
        for payslip in payslips:
            index +=1
            if payslip['struct_id'][1] == "MAIRIE SPY":
                if self.titre == "CNPS AGENT":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'RETRAITECNPS')]
                elif self.titre == "MUTUELLE":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'MUTUELLEMAMA')]
                elif self.titre == "ASSURANCE":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'SCAINTERA')]
                elif self.titre == "IS":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'c400')]
                elif self.titre == "CNPS PATRONALE":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'CNPSPATRONALE')]
                payslips_line = self.env['hr.payslip.line'].search_read(domain1)
                
                #domain2 = [('slip_id', '=', payslip['id']),('code', '=', 'C100')]
                domain2 = [('slip_id', '=', payslip['id']),('code', '=', 'C300')]
                payslips_line1 = self.env['hr.payslip.line'].search_read(domain2)
                
                #raise UserError(_('%s') % (payslips_line1[0]['total']))

                somme_salaire += payslips_line1[0]['total']
                somme_amount += payslips_line[0]['total']
                
                #amount_lettre = amount_to_text_fr(payslips_line[20]['total'],'Francs CFA')
                compte = payslip['compte'],
                chapitre = payslip['chapitre'],

                vals = {
                    'employee_id': payslip['employee_id'][1],
                    'contract_id': payslip['contract_id'],
                    'date_from': payslip['date_from'],
                    'date_to': payslip['date_to'],
                    'number': payslip['number'],
                    'salaire': payslips_line1[0]['total'],
                    'amount': payslips_line[0]['total'],
                    'index': index,
                    'compte': payslip['compte'],
                    'compte_fonctionnel': payslip['account_fonctionnel_id'],
                    'chapitre': payslip['chapitre'],
                }
                payslips_list.append(vals)
        self.compte = compte[0]
        self.chapitre = chapitre[0]
        self.somme_salaire_base = somme_salaire
        self.somme_retenue = somme_amount
        self.amount_lettre = amount_to_text_fr(somme_amount,'Francs CFA')
        #raise UserError(_('%s') % (somme_salaire))
        #print('Payslips',payslips)
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }  
        #raise UserError(_('%s') % (somme_salaire['somme_salaire']))  
        return self.env.ref('innoving_paie.action_report_innoving_paie_etat_retenue_report').report_action(self, data=data)