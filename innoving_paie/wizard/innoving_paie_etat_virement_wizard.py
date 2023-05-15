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


class InnovingHrPayslipVirementRetenue(models.TransientModel):
    _name = 'innoving.hr.payslip.etat.virement'
    _description = "Innoving Hr payslip etat virement wizard"
    
    banque_id = fields.Many2one('res.bank',straing='Banque')
    banque_name = fields.Char(straing='Banque')
    periode_id = fields.Many2one('periode', string='Période')
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')    
    somme_salaire_net = fields.Float(string='Somme salaires')  
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
        banque_id = self.banque_id.id
        somme_salaire_net = 0.0
        somme_amount = 0.0
        index = 0
        net = 0.0
        net_respo = 0.0
             
        if date_from:
            domain += [('date_from', '>=', date_from)]
        if date_to:
            domain += [('date_to', '<=', date_to)]
        if banque_id:
            domain += [('bank_id', '=', banque_id)]
             
        #payslips = self.env['hr.payslip'].search(domain)
        payslips = self.env['hr.payslip'].search_read(domain)
        #raise UserError(_('%s') % (payslips[0]['id']))
        payslips_list =  []
         
        for payslip in payslips:
            index +=1
            
            domain1 = [('slip_id', '=', payslip['id'])]
            payslips_line = self.env['hr.payslip.line'].search_read(domain1)

            if payslip['struct_id'][1] == "MAIRIE SPY":
                somme_salaire_net += payslips_line[24]['total']
                net = payslips_line[24]['total']

            if payslip['struct_id'][1] == "RESPONSABLE MAIRIE SPY":
                somme_salaire_net += payslips_line[2]['total']
                net_respo = payslips_line[2]['total']
                
            vals = {
                'employee_id': payslip['employee_id'][1],
                'numero_compte_id': payslip['numero_compte_id'][1],
                'date_from': payslip['date_from'],
                'date_to': payslip['date_to'],
                'structure': payslip['struct_id'][1],
                'line_amount_agent': net,
                'line_amount_respo': net_respo,
                'account_fonctionnel_code': payslip['account_fonctionnel_code'],
                'index': index,
            }  

            payslips_list.append(vals)
        
        self.banque_name = self.banque_id.name
        self.somme_salaire_net = somme_salaire_net
        self.amount_lettre = amount_to_text_fr(somme_salaire_net,'Francs CFA')
        #raise UserError(_('%s') % (somme_salaire))
        #print('Payslips',payslips)
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }  
        #raise UserError(_('%s') % (net))  
        return self.env.ref('innoving_paie.action_report_innoving_paie_etat_virement_report').report_action(self, data=data)
