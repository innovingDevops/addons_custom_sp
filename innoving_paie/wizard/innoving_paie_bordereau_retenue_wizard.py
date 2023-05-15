# -- coding: utf-8 --

import base64
import datetime
import hashlib
import pytz
import threading

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from email.utils import formataddr
from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.osv.orm import browse_record

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import html_translate

from odoo.tools.amount_to_text_frr import amount_to_text_fr


class InnovingHrPayslipBordereauRetenue(models.TransientModel):
    _name = 'innoving.hr.payslip.bordereau.retenue'
    _description = "Innoving Hr payslip bordereau retenue wizard"

    titre = fields.Selection(string="Titre", selection=[
        ('CNPS AGENT', 'CNPS AGENT'),
        ('CNPS PATRONALE', 'CNPS PATRONALE'),
        ('MUTUELLE', 'MAMA SP'),
        ('ASSURANCE', 'SCA-INTER A'),
        ('IS', 'IS'), ])
    date_from = fields.Date('Date début')
    date_to = fields.Date('date fin')
    account_fonctionnel_id = fields.Many2one('account.account', 'Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    periode_id = fields.Many2one('periode', string='Période')
    somme_salaire_base = fields.Float(string='Somme salaires')
    somme_retenue = fields.Float(string='Somme Retenues')
    amount_lettre = fields.Char(string='Montant en lettre')
    barre = fields.Selection(string="Barre", selection=[
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ])
    compte = fields.Char(string='Compte')
    chapitre = fields.Char(string='Chapitre')
    periode_retenue = fields.Char(string='Période retenue')

    @api.onchange('date_from', 'date_to')
    def onchange_periode_date(self):
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_('Attention, vérifier les dates !'))
        return {}

    @api.onchange('periode_id')
    def onchange_periode_id(self):
        if self.periode_id:
            periode = self.env['periode'].search([('id', '=', self.periode_id.id)])
            if periode.id:
                # self.ticket_html = self.req_ticket_html()
                self.date_from = periode.date_from
                self.date_to = periode.date_to
        return {}

    @api.onchange('account_fonctionnel_id')
    def _onchange_account_fonctionnel_id(self):
        if self.account_fonctionnel_id:
            self.account_fonctionnel_code = self.account_fonctionnel_id.code
            return {}



    @api.multi
    def calcul_compte(self, param):
        index = 0
        domain_line = []
        somme_retenue = 0.0
        payslip=0
        account_fonc=0
        
        for payslip in param:
            index += 1
            #raise UserError(_('%s') % (payslip['id']))
            if payslip['struct_id'][1] == "MAIRIE SPY":

                code1 = 'RETRAITECNPS'
                code2 = 'CNPSPATRONALE'
                code3 = 'MUTUELLEMAMA'
                code4 = 'SCAINTERA'
                code5 = 'c400'

                if self.titre == "CNPS AGENT":
                    domain_line = [('slip_id', '=', payslip['id']), ('code', '=', code1)]

                if self.titre == "CNPS PATRONALE":
                    domain_line = [('slip_id', '=', payslip['id']), ('code', '=', code2)]

                if self.titre == "MUTUELLE":
                    domain_line = [('slip_id', '=', payslip['id']), ('code', '=', code3)]

                if self.titre == "ASSURANCE":
                    domain_line = [('slip_id', '=', payslip['id']), ('code', '=', code4)]

                if self.titre == "IS":
                    domain_line = [('slip_id', '=', payslip['id']), ('code', '=', code5)]

                payslips_line = self.env['hr.payslip.line'].search_read(domain_line)

                somme_retenue += payslips_line[0]['total']
                account_fonc = payslip['account_fonctionnel_code']

        vals = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'index': index,
            'compte_fonctionnel': account_fonc,
            'somme_retenue': somme_retenue,
            'barre': self.barre,
            
        }

        return vals

    @api.multi
    def print_report(self):
        domain = []
        domain1 = []
        domain2 = []
        domain3 = []
        domain4 = []
        domain5 = []
        domain6 = []
        domain7 = []
        payslips_list = []

        date = []
        date_from = self.date_from
        date_to = self.date_to
        somme_amount = 0.0
        compte = '6000'
        compte1 = '60012'
        compte2 = '6002'
        compte3 = '6010'
        compte4 = '6030'
        compte5 = '6031'
        compte6 = '6100'
        compte7 = '6250'

        if date_from:
            date += [('date_from', '>=', date_from)]
        if date_to:
            date += [('date_to', '<=', date_to)]

        domain = date + [('account_fonctionnel_code', '=', compte)]
        domain1 = date + [('account_fonctionnel_code', '=', compte1)]
        domain2 = date + [('account_fonctionnel_code', '=', compte2)]
        domain3 = date + [('account_fonctionnel_code', '=', compte3)]
        domain4 = date + [('account_fonctionnel_code', '=', compte4)]
        domain5 = date + [('account_fonctionnel_code', '=', compte5)]
        domain6 = date + [('account_fonctionnel_code', '=', compte6)]
        domain7 = date + [('account_fonctionnel_code', '=', compte7)]
        
        # if barre:
        # domain += [('analytic_account_ref', '=', barre)]

        # payslips = self.env['hr.payslip'].search(domain)
        payslips = self.env['hr.payslip'].search_read(domain)
        payslips1 = self.env['hr.payslip'].search_read(domain1)
        payslips2 = self.env['hr.payslip'].search_read(domain2)
        payslips3 = self.env['hr.payslip'].search_read(domain3)
        payslips4 = self.env['hr.payslip'].search_read(domain4)
        payslips5 = self.env['hr.payslip'].search_read(domain5)
        payslips6 = self.env['hr.payslip'].search_read(domain6)
        payslips7 = self.env['hr.payslip'].search_read(domain7)
        

        payslips_list.append(self.calcul_compte(payslips))
        payslips_list.append(self.calcul_compte(payslips1))
        payslips_list.append(self.calcul_compte(payslips2))
        payslips_list.append(self.calcul_compte(payslips3))
        payslips_list.append(self.calcul_compte(payslips4))
        payslips_list.append(self.calcul_compte(payslips5))
        payslips_list.append(self.calcul_compte(payslips6))
        payslips_list.append(self.calcul_compte(payslips7))
        #raise UserError(_('%s') % (payslips_list))
        total_retenue = 0
        for ligne in payslips_list:
            total_retenue += int(ligne['somme_retenue'])

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.periode_retenue = _('%s de %s') % (self.titre, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))

        self.somme_salaire_base = total_retenue
        self.amount_lettre = amount_to_text_fr(total_retenue,'Francs CFA')
        data = {
            'form_data': self.read()[0],
            'payslips': payslips_list,
        }
        #raise UserError(_('%s') % (total_retenue))
        return self.env.ref('innoving_paie.action_report_innoving_paie_bordereau_retenue_report').report_action(self,data=data)