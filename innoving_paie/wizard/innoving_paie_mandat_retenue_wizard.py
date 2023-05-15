# -*- coding: utf-8 -*-

import babel
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
from datetime import time

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import html_translate
from email.policy import default

from odoo.tools.amount_to_text_frr import amount_to_text_fr


class InnovingHrPayslipMandatRetenue(models.TransientModel):
    _name = 'innoving.hr.payslip.mandat.retenue'
    _description = "Innoving Hr payslip mandat retenue wizard"
    
    titre = fields.Selection(string="Titre", selection=[
        ('CNPS AGENT', 'CNPS AGENT'),
        ('CNPS PATRONALE', 'CNPS PATRONALE'),
        ('MUTUELLE', 'MAMA SP'),
        ('ASSURANCE', 'SCA-INTER A'),
        ('IS', 'IS'),])
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')
    periode_id = fields.Many2one('periode', string='Période')
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    somme_cnps_agent = fields.Float(string='Total CNPS')   
    beneficiaire = fields.Char(string='Bénéficiaire :')
    lieu = fields.Char(string='A :')
    compte_bancaire = fields.Char(string='Compte bancaire :')
    postal = fields.Char(string='Postal')
    banque = fields.Char(string='Banque')
    agence = fields.Char(string='Agence')
    amount_lettre = fields.Char(string='Montan en lettre')
    barre = fields.Selection(string="Barre", selection=[
        ('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),])  
    objet = fields.Char(string='Objet')
    
     
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
        domain1 = []
        date_from = self.date_from
        date_to = self.date_to
        account_fonctionnel_code = self.account_fonctionnel_code
        somme_salaire = 0.0
        somme_amount = 0.0
        somme_cnps_agent = 0.0

        if self.titre == 'CNPS AGENT' or self.titre == 'CNPS PATRONALE':
            self.beneficiaire = 'LA CNPS BP 368 SAN PEDRO'
            self.lieu = 'SAN PEDRO'
            self.compte_bancaire = 'CI150 07001 201090000738 03'
            self.postal = ''
            self.banque = 'UBA'
            self.agence = 'SAN PEDRO'
        elif self.titre == 'ASSURANCE':
            self.beneficiaire = 'SCA-INTER A'
            self.lieu = 'SAN PEDRO'
            self.compte_bancaire = 'CI1131 01001 011038400006 42'
            self.postal = ''
            self.banque = 'BRIDGE BANK GROUP-CI'
            self.agence = 'SAN PEDRO'
        elif self.titre == 'IS':
            self.beneficiaire = 'DGI'
            self.lieu = 'ABIDJAN'
            self.compte_bancaire = ''
            self.postal = ''
            self.banque = ''
            self.agence = ''
        elif self.titre == 'MUTUELLE':
            self.beneficiaire = 'MAMA-SP (Mutuelle des Agents de la Mairie de San Pedro)'
            self.lieu = 'SAN PEDRO'
            self.compte_bancaire = 'CI008 07271 027140303729 73'
            self.postal = ''
            self.banque = 'SOCIETE GENERALE CI'
            self.agence = 'SAN PEDRO'

        index = 0
        barre = self.barre

        ttyme = datetime.combine(fields.Date.from_string(self.date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'

        if self.titre != 'ASSURANCE':
            self.objet = 'RETENUE %s DU MOIS DE %s' % (self.titre, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        else:
            self.objet = 'RETENUE PART EMPLOYEE POUR L\'ASSURANCE MALADIE SCA-INTER A DU MOIS DE %s' % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
          
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
                if self.titre == "CNPS PATRONALE":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'CNPSPATRONALE')]
                elif self.titre == "MUTUELLE":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'MUTUELLEMAMA')]
                elif self.titre == "ASSURANCE":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'SCAINTERA')]
                elif self.titre == "IS":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'c400')]

                payslips_line = self.env['hr.payslip.line'].search_read(domain1)
                
                domain2 = [('slip_id', '=', payslip['id']),('code', '=', 'C100')]
                payslips_line1 = self.env['hr.payslip.line'].search_read(domain2)
                
                somme_cnps_agent += payslips_line[0]['total']
                
                vals = {
                    'employee_id': payslip['employee_id'][1],
                    'contract_id': payslip['contract_id'],
                    'account_fonctionnel_code': payslip['account_fonctionnel_code'],
                    'bank_id': payslip['bank_id'],
                    'date_from': payslip['date_from'],
                    'date_to': payslip['date_to'],
                    'number': payslip['number'],
                    'index': index,
                    'somme_cnps_agent': somme_cnps_agent,
                }
            payslips_list.append(vals)
        self.somme_cnps_agent = somme_cnps_agent
        self.amount_lettre = amount_to_text_fr(self.somme_cnps_agent,'Francs CFA')
        #raise UserError(_('%s') % (self.somme_cnps_agent))
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }  
        #raise UserError(_('%s') % (payslips['somme_cnps_agent']))  
        return self.env.ref('innoving_paie.action_report_innoving_paie_mandat_retenue_report').report_action(self, data=data)