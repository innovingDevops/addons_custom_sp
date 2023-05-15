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


class InnovingHrPayslipVirementRetenues(models.TransientModel):
    _name = 'innoving.hr.payslip.etat.virements'
    _description = "Innoving Hr payslip etat virement retenue wizard"
 
    name = fields.Selection(string="Titre", selection=[
        ('MAMA SP', 'MAMA SP'),
        ('SCA INTER A', 'SCA-INTER A'),])
    periode_id = fields.Many2one('periode', string='Période')
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')    
    somme_amount = fields.Float(string='Somme salaires')  
    amount_lettre = fields.Char(string='Montant en lettre')  
     
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

    
    @api.multi
    def print_report(self):
        domain = []
        date_from = self.date_from
        date_to = self.date_to
        name = self.name
        somme_salaire_net = 0.0
        somme_amount = 0.0
        index = 0
        net = 0.0
        net_respo = 0.0
             
        if date_from:
            domain += [('date_from', '>=', date_from)]
        if date_to:
            domain += [('date_to', '<=', date_to)]
             
        #payslips = self.env['hr.payslip'].search(domain)
        payslips = self.env['hr.payslip'].search_read(domain)
        #raise UserError(_('%s') % (payslips[0]['id']))
        payslips_list =  []
         
        for payslip in payslips:
            index +=1
            
            if payslip['struct_id'][1] == "MAIRIE SPY":
                if self.name == "MAMA SP":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'MUTUELLEMAMA')]
                elif self.name == "SCA INTER A":
                    domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'SCAINTERA')]
                payslips_line = self.env['hr.payslip.line'].search_read(domain1)

                somme_amount += payslips_line[0]['total']
                
                vals = {
                    'employee_id': payslip['employee_id'][1],
                    'date_from': payslip['date_from'],
                    'date_to': payslip['date_to'],
                    'structure': payslip['struct_id'][1],
                    'amount': payslips_line[0]['total'],
                    'index': index,
                }  

                payslips_list.append(vals)
        
        self.name = self.name
        self.somme_amount = somme_amount
        self.amount_lettre = amount_to_text_fr(somme_amount,'Francs CFA')
        #raise UserError(_('%s') % (somme_salaire))
        #print('Payslips',payslips)
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }  
        #raise UserError(_('%s') % (net))  
        return self.env.ref('innoving_paie.action_report_innoving_paie_etat_virement_retenue_report').report_action(self, data=data)
