# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

from odoo.tools.amount_to_text_frr import amount_to_text_fr

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'
    
    account_fonctionnel_id = fields.Many2one('account.account',string='Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    numero_compte_id = fields.Many2one('res.partner.bank',string='Numéro de compte')
    numero_compte = fields.Char(string='Numéro de compte')
    hr_grade_id = fields.Many2one('hr.grade',string='Grade')
    hr_echelon_id = fields.Many2one('hr.echelon',string='Echelon')
    job_id = fields.Many2one('hr.job',string='Fonction')
    analytic_account_id = fields.Many2one('account.analytic.account',string='Compte analytique')
    analytic_account_ref = fields.Char(string='Ref')
    bank_id = fields.Many2one('res.bank',string='Compte bancaire')
    chapitre = fields.Char(string='Chapitre')
    compte = fields.Char(string='Compte')
    credit_ouvert = fields.Float(string='Credit ouvert')
    depense_anterieur = fields.Float(string='Dépense antérieur')
    depense_actuelle = fields.Float(string='Dépense actuelle')
    credit_disponible = fields.Float(string='Crédit disponible')
    objet = fields.Char(string='Objet')
    net = fields.Float(string='Net', compute='_compute_net',store=True)
    mise_a_pied = fields.Selection(string="Mise à pieds / Nbre Jours", selection=[
        ('0', '0 jour'),
        ('3', '3 jours'),
        ('8', '8 jours')
        ], track_visibility='always', default='0')
    amount_retenue = fields.Float(string='Mt Mise à pieds', compute='_compute_mis_a_pied',store=True)
    amount_retenue_transport = fields.Float(string='Mt MAP transport', compute='_compute_mis_a_pied',store=True)
    amount_rappel = fields.Float(string='Montant rappel')


    @api.multi
    def button_unlink(self):
        for payslip in self:
            payslip.env['hr.payslip'].browse(payslip.id).unlink()
                            
    
    #@api.onchange('employee_id','contract_id','numero_compte_id')
    #def _onchange_contract_id(self):
        #if  self.employee_id  and self.contract_id :
            #contract_id = self.env['hr.contract'].search([('id','=',self.contract_id.id)])
            #self.account_fonctionnel_id = contract_id.account_fonctionnel_id.id
            #self.account_fonctionnel_code = contract_id.account_fonctionnel_id.code
            #self.numero_compte_id = self.employee_id.bank_account_id.id
            ##self.numero_compte = self.employee_id.bank_account_id.acc_number
            ##self.numero_compte = self.numero_compte_id.acc_number
            #self.bank_id = self.employee_id.bank_account_id.bank_id.id
            #self.analytic_account_id = contract_id.analytic_account_id.id
            #self.analytic_account_ref = contract_id.analytic_account_id.code
            #self.compte = contract_id.compte
            #self.chapitre = contract_id.chapitre
            #return {}
        
        
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            #contract_id = self.env['hr.contract'].search([('id','=',self.contract_id.id)])
            employee_id = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
            self.numero_compte_id = self.employee_id.bank_account_id.id
            self.numero_compte = employee_id.bank_account_id.acc_number
            self.bank_id = self.employee_id.bank_account_id.bank_id.id
            self.hr_grade_id = self.employee_id.hr_grade_id.id
            self.hr_echelon_id = self.employee_id.hr_echelon_id.id
            self.job_id = self.employee_id.job_id.id
            self.account_fonctionnel_id = self.contract_id.account_fonctionnel_id.id
            self.account_fonctionnel_code = self.contract_id.account_fonctionnel_id.code
            self.analytic_account_id = self.contract_id.analytic_account_id.id
            self.analytic_account_ref = self.contract_id.analytic_account_id.code
            self.compte = self.contract_id.compte
            self.chapitre = self.contract_id.chapitre
            ttyme = datetime.combine(fields.Date.from_string(self.date_from), time.min)
            locale = self.env.context.get('lang') or 'en_US'
            self.objet = 'SALAIRE DU MOIS DE %s' % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
            return {}
        
        
    @api.onchange('account_fonctionnel_id')
    def _onchange_account_fonctionnel_id(self):
        if self.account_fonctionnel_id:
            self.account_fonctionnel_code=self.account_fonctionnel_id.code
            return {}

    def sum_text(self, value=0):
        if value >= 0.0:
            return amount_to_text_fr(value,'Francs CFA')

    @api.depends('line_ids')
    def _compute_net(self):
        net=0.0
        for order in self:
            for line in order.line_ids:
                if line.code in ['C900']:
                    net=line.total
            order.update({'net': net or 0.0})
            
    @api.depends('mise_a_pied')
    def _compute_mis_a_pied(self):
        amount=0.0
        amount_tp=0.0
        salaire=0.0
        base=30
        mise_a_pied=0
        transport=0.0
        for order in self:
            salaire = order.contract_id.wage
            transport = order.contract_id.transport_bonus
            if order.mise_a_pied == "0":
                mise_a_pied = 0
            elif order.mise_a_pied == "3":
                mise_a_pied = 3
            elif order.mise_a_pied == "8":
                mise_a_pied = 8
            amount = (mise_a_pied * salaire) / base
            amount_tp = (mise_a_pied * transport) / base
            order.update({'amount_retenue': amount or 0.0})
            order.update({'amount_retenue_transport': amount_tp or 0.0})

    @api.multi
    def action_payslip_done(self):
        payslips_line = []
        montant_alloue = 0
        depense_anterieur = 0
        montant_disponible = 0
        if not self.env.context.get('without_compute_sheet'):
            self.compute_sheet()
            for payslip in self:
                return self.write({'state': 'done', 'depense_actuelle': payslip.net})
                #for budget_line in payslip.analytic_account_id.crossovered_budget_line:
                    #raise UserError(_("ok"))
                    #domain1 = [('slip_id', '=', payslip['id']),('code', '=', 'C900')]
                    #payslips_line = self.env['hr.payslip.line'].search_read(domain1)
                    
                    #if len(budget_line) == 1:
                    
                    #mt_alloue = budget_line.planned_amount
                    #dp_anterieur = budget_line.practical_amount
                    #if mt_alloue < 0:
                        #montant_alloue = budget_line.planned_amount * (-1)
                    #else:
                        #montant_alloue = budget_line.planned_amount
                    #if dp_anterieur < 0:
                        #depense_anterieur = (budget_line.practical_amount * (-1)) - payslips_line[0]['total']
                    #else:
                        #depense_anterieur = budget_line.practical_amount
                    #md = montant_alloue - depense_anterieur
                    #montant_disponible = md - payslips_line[0]['total']
                    #budget_id = budget_line.crossovered_budget_id.id
                    #raise UserError(_("%s") % (payslips_line[0]['total']))
                #return self.write({'state': 'done', 'credit_ouvert': montant_alloue, 'depense_anterieur': depense_anterieur, 'depense_actuelle': payslips_line[0]['total'], 'credit_disponible': montant_disponible})