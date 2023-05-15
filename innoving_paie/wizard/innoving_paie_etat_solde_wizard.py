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

class InnovingHrPayslip(models.TransientModel):
    _name = 'innoving.hr.payslip'
    _description = "Innoving Hr payslip wizard"
    
    periode_id = fields.Many2one('periode', string='Période')
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    
    
    @api.onchange('periode_id')
    def onchange_periode_id(self):
        if self.periode_id:
            periode = self.env['periode'].search([('id','=',self.periode_id.id)])
            if periode.id:
                #self.ticket_html = self.req_ticket_html()
                self.date_from = periode.date_from
                self.date_to = periode.date_to
        return {}
    
    
    @api.onchange('date_from','date_to')
    def onchange_periode_date(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_('Attention, vérifier les dates !')) 
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
        if date_from:
            domain += [('date_from', '>=', date_from)]
        if date_to:
            domain += [('date_to', '<=', date_to)]
        if account_fonctionnel_code:
            domain += [('account_fonctionnel_code', '=', account_fonctionnel_code)]
            
        #payslips = self.env['hr.payslip'].search(domain)
        payslips = self.env['hr.payslip'].search_read(domain)
        payslips_list =  []
        for payslip in payslips:
            
            domain2 = [('slip_id', '=', payslip['id'])]
            payslips_line = self.env['hr.payslip.line'].search_read(domain2)

            if payslip['struct_id'][1] == "MAIRIE SPY":

                amount_lettre = amount_to_text_fr(payslips_line[24]['total'],'Francs CFA')

                vals = {
                    'employee_id': payslip['employee_id'][1],
                    'date_from': payslip['date_from'],
                    'date_to': payslip['date_to'],
                    'credit_ouvert': payslip['credit_ouvert'],
                    'structure_salariale': payslip['struct_id'][1],
                    'depense_anterieur': payslip['depense_anterieur'],
                    'credit_disponible': payslip['credit_disponible'],
                    'bank_id': payslip['bank_id'][1],
                    'hr_grade_id': payslip['hr_grade_id'][1],
                    'hr_echelon_id': payslip['hr_echelon_id'][1],
                    'job_id': payslip['job_id'][1],
                    'account_fonctionnel_id': payslip['account_fonctionnel_id'][1],
                    'account_fonctionnel_code': payslip['account_fonctionnel_code'],
                    'line_ids': payslip['line_ids'],
                    'line_code': payslips_line[0]['code'],
                    'line_amount': payslips_line[0]['total'],
                    'line_code1': payslips_line[1]['code'],
                    'line_amount1': payslips_line[1]['total'],
                    'line_code2': payslips_line[2]['code'],
                    'line_amount2': payslips_line[2]['total'],
                    'line_code3': payslips_line[3]['code'],
                    'line_amount3': payslips_line[3]['total'],
                    'line_code4': payslips_line[4]['code'],
                    'line_amount4': payslips_line[4]['total'],
                    'line_code5': payslips_line[5]['code'],
                    'line_amount5': payslips_line[5]['total'],
                    'line_code6': payslips_line[6]['code'],
                    'line_amount6': payslips_line[6]['total'],
                    'line_code7': payslips_line[7]['code'],
                    'line_amount7': payslips_line[7]['total'],
                    'line_code8': payslips_line[8]['code'],
                    'line_amount8': payslips_line[8]['total'],
                    'line_code9': payslips_line[9]['code'],
                    'line_amount9': payslips_line[9]['total'],
                    'line_code10': payslips_line[10]['code'],
                    'line_amount10': payslips_line[10]['total'],
                    'line_code11': payslips_line[11]['code'],
                    'line_amount11': payslips_line[11]['total'],
                    'line_code12': payslips_line[12]['code'],
                    'line_amount12': payslips_line[12]['total'],
                    'line_code13': payslips_line[13]['code'],
                    'line_amount13': payslips_line[13]['total'],
                    'line_code14': payslips_line[14]['code'],
                    'line_amount14': payslips_line[14]['total'],
                    'line_code15': payslips_line[15]['code'],
                    'line_amount15': payslips_line[15]['total'],
                    'line_code16': payslips_line[16]['code'],
                    'line_amount16': payslips_line[16]['total'],
                    'line_code17': payslips_line[17]['code'],
                    'line_amount17': payslips_line[17]['total'],
                    'line_code18': payslips_line[18]['code'],
                    'line_amount18': payslips_line[18]['total'],
                    'line_code19': payslips_line[19]['code'],
                    'line_amount19': payslips_line[19]['total'],
                    'line_code20': payslips_line[20]['code'],
                    'line_amount20': payslips_line[20]['total'],
                    'line_code21': payslips_line[21]['code'],
                    'line_amount21': payslips_line[21]['total'],
                    'line_code22': payslips_line[22]['code'],
                    'line_amount22': payslips_line[22]['total'],
                    'line_code23': payslips_line[23]['code'],
                    'line_amount23': payslips_line[23]['total'],
                    'line_code24': payslips_line[24]['code'],
                    'line_amount24': payslips_line[24]['total'],
                    'amount_lettre': amount_lettre,
                    'analytic_account_ref': payslip['analytic_account_ref'],
                    'compte': payslip['compte'],
                    'chapitre': payslip['chapitre'],
                    'numero_compte': payslip['numero_compte'],
                }
            
            if payslip['struct_id'][1] == "RESPONSABLE MAIRIE SPY":

                amount_lettre = amount_to_text_fr(payslips_line[2]['total'],'Francs CFA')

                vals = {
                    'employee_id': payslip['employee_id'][1],
                    'date_from': payslip['date_from'],
                    'date_to': payslip['date_to'],
                    'credit_ouvert': payslip['credit_ouvert'],
                    'structure_salariale': payslip['struct_id'][1],
                    'depense_anterieur': payslip['depense_anterieur'],
                    'credit_disponible': payslip['credit_disponible'],
                    'bank_id': payslip['bank_id'][1],
                    'hr_grade_id': payslip['hr_grade_id'][1],
                    'hr_echelon_id': payslip['hr_echelon_id'][1],
                    'job_id': payslip['job_id'][1],
                    'account_fonctionnel_id': payslip['account_fonctionnel_id'][1],
                    'account_fonctionnel_code': payslip['account_fonctionnel_code'],
                    'line_ids': payslip['line_ids'],
                    'line_code': payslips_line[0]['code'],
                    'line_amount': payslips_line[0]['total'],
                    'line_code1': payslips_line[1]['code'],
                    'line_amount1': payslips_line[1]['total'],
                    'line_code2': payslips_line[2]['code'],
                    'line_amount2': payslips_line[2]['total'],
                    'amount_lettre': amount_lettre,
                    'analytic_account_ref': payslip['analytic_account_ref'],
                    'compte': payslip['compte'],
                    'chapitre': payslip['chapitre'],
                    'numero_compte': payslip['numero_compte'],
                }

            payslips_list.append(vals)
            #raise UserError(_('%s') % (payslip['analytic_account_id']))
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }    
        return self.env.ref('innoving_paie.action_report_innoving_paie_report').report_action(self, data=data)