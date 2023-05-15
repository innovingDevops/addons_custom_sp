# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2014 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_payroll_ci
# ##############################################################################  -->


import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import netsvc
from odoo import fields, osv, api,models
from odoo import tools
from odoo.tools.translate import _
from odoo.exceptions import Warning

from odoo.tools.safe_eval import safe_eval as eval
from decimal import Decimal
from collections import namedtuple
from math import fabs, ceil

import odoo.addons.decimal_precision as dp



class hr_payslip(models.Model):
    _inherit="hr.payslip"
       
    def get_days_periode(self,start, end):
        r = (end + timedelta(days=1) - start).days
        return [start+timedelta(days=i) for i in range(r)]
      
    def get_test(self,cr, uid,ids,employee_id, context=None):
        res = {}
        obj_payslip = self.pool.get('hr.payslip')
        for emp in self.browse(cr, uid, ids, context=context):
            contract_ids = obj_payslip.search(cr, uid, [('employee_id','=',emp.id),], context=context)
            if contract_ids:
                raise osv.except_osv(_("test"),_("test"))     
        
    def get_emprunt_montant_monthly(self,cr,uid,ids,employee_id,date_from, date_to,context=None):
        cp=cr
        cp.execute("SELECT * FROM hr_emprunt as emp, hr_echeance as ech WHERE emp.employee_id=%s and\
        ech.date_remboursement_echeance<=%s or ech.date_remboursement_echeance>=%s\
        and ech.emprunt_id=emp.id",(employee_id,date_from,date_to))
        test=cp.fetchall()
        raise osv.except_osv(_('Test'),test)

    # @api.model
    # def get_worked_day_lines(self, contract_ids, date_from, date_to):
        # """
        # @param contract_ids: list of contract id
        # @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        # """

        # def was_on_leave(employee_id, datetime_day):
            # day = fields.Date.to_string(datetime_day)
            # return self.env['hr.holidays'].search([
                # ('state', '=', 'validate'),
                # ('employee_id', '=', employee_id),
                # ('type', '=', 'remove'),
                # ('date_from', '<=', day),
                # ('date_to', '>=', day)
            # ], limit=1).holiday_status_id.name

        # res = []
        # --fill only if the contract as a working schedule linked
        # for contract in self.env['hr.contract'].browse(
                # contract_ids):  # .filtered(lambda contract: contract.working_hours):
            # attendances = {
                # 'name': _("Temps de travail contractuel"),
                # --'name': _("Normal Working Days paid at 100%"),
                # 'sequence': 1,
                # 'code': 'WORK100',
                # 'number_of_days': 0.0,
                # 'number_of_hours': 0.0,
                # 'contract_id': contract.id,
            # }
            # leaves = {}
            # day_from = fields.Datetime.from_string(date_from)
            # day_to = fields.Datetime.from_string(date_to)
            # nb_of_days = (day_to - day_from).days + 1
            # for day in range(0, nb_of_days):
                # working_hours_on_day = contract.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                # if working_hours_on_day:
                    # --the employee had to work
                    # leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day))
                    # if leave_type:
                        # --if he was on leave, fill the leaves dict
                        # if leave_type in leaves:
                            # leaves[leave_type]['number_of_days'] += 1.0
                            # leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        # else:
                            # leaves[leave_type] = {
                                # 'name': leave_type,
                                # 'sequence': 5,
                                # 'code': leave_type,
                                # 'number_of_days': 1.0,
                                # 'number_of_hours': working_hours_on_day,
                                # 'contract_id': contract.id,
                            # }
                    # else:
                        # --add the input vals to tmp (increment if existing)
                        # attendances['number_of_days'] += 1.0
                        # --attendances['number_of_hours'] += working_hours_on_day  # B replaced by the next 4 lines
                        # if contract.time_mod == 'fixed':
                            # attendances['number_of_hours'] = contract.time_fixed
                        # else:
                            # attendances['number_of_hours'] += working_hours_on_day

            # if attendances['number_of_hours'] == 0.0:
                # attendances['number_of_hours'] = contract.time_fixed

            # leaves = [value for key, value in leaves.items()]

            # --B          add a placeholder for actually worked days/hours (to be entered by user if needed)
            # actually_worked = {
                # 'name': _("Temps de travail effectif"),
                # 'sequence': 2,
                # 'code': 'WORKED',
                # 'number_of_days': attendances['number_of_days'],
                # 'number_of_hours': contract.time_fixed,
                # 'contract_id': contract.id,
            # }

            # res += [attendances] + [actually_worked] + leaves
        # return res


             
    def calcul_anciennete_actuel(self,cr,uid,ids,context=None):
        payslips=self.browse(cr, uid, ids, context=context)
        anciennete={}
        for payslip in payslips:
            date_debut=datetime.strptime(payslip.contract_id.date_start,'%Y-%m-%d')
            date_fin = datetime.strptime(payslip.date_to,'%Y-%m-%d')
            result=date_fin - date_debut
            nombre_day=result.days
            nbre_year=int(nombre_day/360)
            nbre_year=payslip.contract_id.an_report+nbre_year
            jour_restant=result.days%360
            nbre_mois=jour_restant/30
            nbre_mois=nbre_mois+payslip.contract_id.mois_report
            if nbre_mois >= 12:
                nbre_year=nbre_year+int(nbre_mois/12)
                nbre_mois=nbre_mois%12
            anciennete={
                        'year_old':nbre_year,
                        'month_old':nbre_mois,
                        }
        return anciennete
    
    def get_anciennete(self,cr,uid,ids,date_start,context=None):
        res = {'value':{
                      'anne_anc':0,
                      }
            }
        payslips=self.browse(cr, uid, ids, context=context)
        for payslip in payslips:
            date_debut=datetime.strptime(payslip.contract_id.date_start,'%Y-%m-%d')
            today = datetime.strptime(payslip.date_to,'%Y-%m-%d')
            result=today-date_debut
            nombre_day=result.days
            nbre_year=int(nombre_day/360)
            nbre_year=payslip.contract_id.an_report+nbre_year
            jour_restant=result.days%360
            nbre_mois=jour_restant/30
            nbre_mois=nbre_mois+payslip.contract_id.mois_report
            if nbre_mois >= 12:
                nbre_year=nbre_year+int(nbre_mois/12)
                nbre_mois=nbre_mois%12
            res['value'].update({
                             'payslip_an_anciennete':nbre_year,
                             'payslip_mois_anciennete':nbre_mois,
                             })
        return res
    
    def _get_annee_actuel(self,cr,uid,ids,field,arg,context=None):
        res={}
        payslips=self.browse(cr,uid,ids,context)
        anciennete=self.calcul_anciennete_actuel(cr, uid,ids, context=context)
        for payslip in payslips :
                res[payslip.id] = anciennete['year_old']
        return res
    
    def _get_mois_actuel(self,cr,uid,ids,field,arg,context=None):
        res={}
        payslips=self.browse(cr,uid,ids,context)
        anciennete=self.calcul_anciennete_actuel(cr, uid,ids, context=context)
        for payslip in payslips :
                res[payslip.id] = anciennete['month_old']
        return res
    
    def _get_last_payslip(self,cr,uid,ids,field,arg,context=None):
        dic={}
        res=[]
        payslips=self.browse(cr, uid, ids, context=context)
        for payslip in payslips:
            slips = payslip.employee_id.slip_ids
            if (len(slips)==1 ) :
                dic[payslip.id] = False
            else :
                for slip in slips:
                    if (slip.id < payslip.id) :
                        res.append(slip)
                        if len(res)>= 1 :
                            dernier=res[len(res)-1]
                            payslip_obj=self.pool.get('hr.payslip').search(cr, uid, [('id','=',dernier.id)], context=context)
                            dic[payslip.id]=payslip_obj      
        return dic

    def _get_total_gain(self):
        res= 0
        line_obj=self.env["hr.payslip.line"]
        for id in range(len(line_obj)):
            line_ids = line_obj[id].lines_ids
            for line in line_ids :
                print (line.code)
                if line.code=='BRUT':
                    res=line.total
        print (res)
        return res


    def get_amount_rubrique(self,lines_ids,rubrique):

        payslip_line = self.env['hr.payslip.line']
        res = []
        ids = []
        print (payslip_line)

        for idx in range(len(lines_ids)):
           # if (lines_ids[idx].appears_on_payslip is True):
                ids.append(lines_ids[idx].id)
        if ids:
            res = payslip_line.browse(ids)


        #print obj.id
        total = 0
        #for id in range(len(obj)):
            #line_ids=obj[id]
        for line in res :
                print (line.total)
                if line.code == rubrique and line.total != 0:
                    #if line.code == rubrique :
                       total = line.total

        return total


    def _get_retenues(self,obj):
        res=0
        #line_obj=self.pool.get('hr.payslip.line')
        for id in range(len(obj)):
            line_ids = obj[id]
            for line in line_ids :
                if line.code=='RET':
                    res =line.total
        return res
    
    def _get_net_paye(self,cr,uid,ids,fields_name, arg, context=None):
        res={}
        #line_obj=self.pool.get("hr.payslip.line")
        for i in self.browse(cr, uid, ids, context=context):
            for line in i.line_ids :
                if line.code=="NET" :
                    res[i.id]=line.total
        return res


    def _get_net(self,obj):
        res=0
        for id in range(len(obj)):
            line_ids = obj[id].lines_ids
            for line in line_ids :
                if line.amount != 0:
                    if  line.code=='NET':
                        res+=line.total

        return res
    
    def _get_last_arrondi(self,cr,uid,ids,field,arg,context=None):
        res = {}
        montant=0
        for payslip in self.browse(cr, uid, ids, context=context): 
            liste_line=payslip.last_payslip.line_ids
            if (liste_line) :
                for line in liste_line:
                    if line.salary_rule_id.code == 'AEP':
                        montant=line.amount
                        res[payslip.id]=montant
            else : 
                res[payslip.id] = 0
        return res
    
    def _get_actuel_id(self,cr,uid,ids,field,arg,context=None):
        res={}
        for payslip in self.browse(cr, uid, ids, context=context):
            res[payslip.id]=1
        return res
    

    option_salaire= fields.Selection([('mois','Mensuel'),('jour','Journalier'),('heure','horaire')],
                         'Option salaire', select=True, readonly=False)
    reference_reglement= fields.Char('Reférence',size=60,required=False)
    # payslip_an_anciennete= fields.Integer("Nombre d'année",compute=_get_annee_actuel,store=True)
    # payslip_mois_anciennete= fields.Integer(compute=_get_mois_actuel,store=True,string="Nombre de mois")
    payment_method= fields.Selection([('espece','Espèces'),('virement','Virement bancaire'),('cheque','Chèques')],
                      string='Moyens de paiement',required=True,default='virement')
    # last_payslip= fields.Many2one("hr.payslip",compute=_get_last_payslip,store=True,string="Dernier bulletin")
    # total_gain= fields.Integer(compute=_get_total_gain,store=True)
    # total_retenues= fields.Integer(compute=_get_retenues,store=True)
    # net_paie= fields.Integer(compute=_get_net_paye,store=True)


    
    def get_list_employee(self,cr,uid,ids,date_to,context=None): 
        list_employees=[]
        hc_obj=self.pool.get('hr.contract')
        hcontract_ids=hc_obj.search(cr,uid,[('state','=','in_progress')])
        cr.execute("SELECT employee_id FROM hr_contract WHERE id=ANY(%s)", (hcontract_ids,))
        results=cr.fetchall()
        if results :
             list_employees=[res[0] for res in results]
             return {'domain':{'employee_id':[('id','in',list_employees)]}}
        
                    
#modification pour le calcul du total            

class hr_payslip_line(models.Model):
    '''
    Payslip Line
    '''

    _name = 'hr.payslip.line'
    _inherit = 'hr.payslip.line'


    @api.depends('quantity', 'amount', 'rate')
    def _calculate_total(self):
        # if not self: return {}
        # res = {}
        for line in self:
            line.total = round(float(line.quantity) * line.amount * line.rate / 100)

    amount= fields.Float('Amount', digits_compute=dp.get_precision('Payroll SN'))
    quantity= fields.Float('Quantity', digits_compute=dp.get_precision('Payroll'))
    total= fields.Float('Total',compute=_calculate_total,  digits_compute=dp.get_precision('Payroll SN'),store=True )
    




        
    
