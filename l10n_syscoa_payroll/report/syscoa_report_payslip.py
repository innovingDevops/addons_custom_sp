#-*- coding:utf-8 -*-

##############################################################################
#
#    ErgoBIT Payroll Senegal
#    Copyright (C) 2013-TODAY ErgoBIT Consulting (<http://ergobit.org>).
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from dateutil import parser
from dateutil import relativedelta
from odoo import models
from odoo.report import report_sxw
from datetime import date
from amount_to_text import amount_to_text 
from amount_to_text_fr import amount_to_text_fr
import odoo

import locale





class ErgobitPayslipReport(report_sxw.rml_parse):

    # Define constants for salary categories
    # ---------------------------------------
    C_BASIC = 'BASIC'
    C_ALW = 'ALW'
    C_RED = 'RED'
    C_NATU = 'NATU'
    C_GROSS = 'GROSS'
    C_DED = 'DED'
    C_TAX = 'TAX'
    C_TAXX = 'TAXX'
    C_ALWN = 'ALWN'
    C_NET = 'NET'

    C_AVCE = 'AVCE'
    C_PAYB = 'PAYB'
    C_SYN = 'SYN'
    C_RETN = 'RETN'

    C_COMP = 'COMP'  # Retenue patronale (-)
    C_COMPP = 'COMPP'  # Retenue patronale (+)

    C_TOTM = 'TOTM'
    C_TOTA = 'TOTA'

    C_RET_EMP ='RET_EMP'
    C_ITS = 'ITS'
    C_CN = 'CN'
    C_CNPS = 'CNPS'
    C_IGR = 'IGR'
    C_BRUT = 'BRUT'
    C_INDM = 'PANC'
    C_BASE_CNPS = 'BASE_CNPS'
    C_ITS_P = 'ITS_P'
    C_CNPS_P = 'CNPS_P'
    C_CPATR = 'CPATR'
    C_TAXEAP = 'TAXEAP'
    C_PF = 'PF'
    C_ACT = 'ACT'
    C_TAXEFP = 'TAXEFP'
    C_FPCR = 'FPCR'



# Constants for some rule codes
#---------------------------------------
    C_R500 = '500'        # rule code for I/R
    C_R550 = '550'        # rule code for TRIMF

# Dict objects containing total values
    total_m = {}
    total_y = {}

    def __init__(self, cr, uid, name, context):
        self.ccnps = 0
        self.ctotal =0
        self.donnes = 0
        super(ErgobitPayslipReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines_main': self.get_payslip_lines_main,
            'get_payslip_lines_total': self.get_payslip_lines_total,
            'get_total': self.get_total,
            'get_quantity': self.get_quantity,
            'get_amount_base1': self.get_amount_base1,
            'get_rate_salarial': self.get_rate_salarial,
            'get_gain_salarial': self.get_gain_salarial,
            'get_deduction_salarial': self.get_deduction_salarial,
            'get_rate_patronal': self.get_rate_patronal,
            'get_contribution_patronal_plus': self.get_contribution_patronal_plus,
            'get_contribution_patronal': self.get_contribution_patronal,
            'parse': self.parse,
            'get_years': self.get_years,
            'get_months': self.get_months,
            'get_worked_hours': self.get_worked_hours,
            'get_somme_rubrique':self.get_somme_rubrique,
            'get_amount_rubrique':self.get_amount_rubrique,
            '_get_retenues':self._get_retenues,
            '_get_gain':self._get_gain,
            '_get_net':self._get_net,
            '_get_net_paie':self._get_net_paie,
            'get_amount_rubrique':self.get_amount_rubrique,
            '_get_taux': self._get_taux,
            '_get_taux_patronal':self._get_taux_patronal,
            'get_employer_line_rate':self.get_employer_line_rate,
            'get_employer_line_amount':self.get_employer_line_amount,
            # 'affiche':self.affiche,
            'get_total_by_rule_category':self.get_total_by_rule_category,
            'amount_to_text_fr':amount_to_text_fr,
            'get_amount_total':self.get_amount_total,
        })

    def parse(self, my_date):
        d, m, y = map(int, my_date.split('/'))
        return date(y, m, d)

    def get_months(self, date_1):
        month = {}
        date_1 = datetime.strptime(str(date_1), '%Y-%m-%d')
        date_1 = datetime.strptime(str(str(date.today().year - 1) + '-' + str(date_1.month) + '-' + str(date_1.day)), '%Y-%m-%d')
        date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
        month = relativedelta.relativedelta(date_2, date_1).months
        return month

    def get_years(self, date_1):
        year = {}
        date_1 = datetime.strptime(str(date_1), '%Y-%m-%d')
        date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
        year = relativedelta.relativedelta(date_2, date_1).years
        return year

    def get_payslip_lines_main(self, lines_ids):
        """ Read the lines for the central table excluding
                - company contribution *_COMP
                - Column totals
                - yearly totals

        env = odoo.api.Environment(self.cr, self.uid, {})
        category_ids = env['hr.salary.rule.category'].search(
            [('code', 'not in', [self.C_COMP, self.C_COMPP, self.C_NET, self.C_TOTA, self.C_TOTM])])
        """
        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_line = env['hr.payslip.line']
        res = []
        ids = []

        for idx in range(len(lines_ids)):
            if (lines_ids[idx].appears_on_payslip is True):
                ids.append(lines_ids[idx].id)
        if ids:
            res = payslip_line.browse(ids)
        print (res)

        return res

    def get_quantity(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        #for p in psline:
        days = env['hr.payslip.worked_days'].search([('payslip_id','=',psline.slip_id.id)])
        print (days)
        for d in days:
            if d.number_of_days:
                return d.number_of_days

        #if round(float(psline.quantity), 2) == 1.00 or round(float(psline.quantity), 2) == 0.00:
           # return ''
#        return report_sxw.rml_parse.formatLang(self, psline.quantity)
       # return psline.quantity
        #return formatl
        return ''



    def get_amount_base(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})

        if round(float(psline.amount), 2) == 0.00:  # '{0:.}'.format(amount)
            return ''
        # no base for I/R, TRIMF
        if psline.code in [self.C_R500, self.C_R550]:
            return ''
        # Only basic, ded and alwn
        category_ids = env['hr.salary.rule.category'].search(
            [('code', 'in', [self.C_BASIC, self.C_DED, self.C_TAX, self.C_TAXX, self.C_ALWN, self.C_ALW])])
        if psline.category_id in category_ids:
            if psline.category_id.code in [self.C_ALW, self.C_BASIC]:
                if psline.code in ['100', '210', '220', '230', '240']:
                    if round(float(psline.amount), 2) == 0.00:
                        return ''
                    #return formatl(psline.amount, 2)
                    return psline.amount
            else:
                if round(float(psline.amount), 2) == 0.00:
                    return ''
                return psline.amount
                # return formatl(psline.amount)
        return ''


    def get_amount_base1(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        res = ''

        category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_RET_EMP,'BRUT','CPATR','IMP_EMP'])])

        line = env['hr.payslip.line'].search([('salary_rule_id.code','=','BASE_CNPS')])

        for l in line:
         self.ccnps = l.amount

        don = env['hr.payslip.line'].search([('salary_rule_id.code', '=', 'BASE_IMP')])
        for d in don:
            self.donnes = d.amount

        if psline.category_id in category_ids:
                if psline.category_id.code in [self.C_RET_EMP,self.C_BRUT,'CPATR','IMP_EMP']:
                    if psline.code == self.C_BRUT:
                      self.ctotal = psline.amount
                    if psline.code in [self.C_CN, self.C_ITS, self.C_ITS_P,self.C_IGR,self.C_TAXEAP, self.C_TAXEFP,self.C_FPCR]:
                           return  self.ctotal
                          # return formatl(psline.amount)
                           #res = total

                    if psline.code in [self.C_CNPS,self.C_CNPS_P]:
                        #if psline.code == self.C_CNPS:
                            #return formatl(psline.amount)
                            # print "self.ccnps = base_cnps"
                            return self.ccnps
                    if psline.code in [self.C_PF, self.C_ACT]:
                        return min(self.donnes,70000)
                   # if psline.code in [self.C_TAXEAP, self.C_TAXEFP,self.C_FPCR]:



                    #if psline.code in ['BASE_CNPS']:
                       #print "ok"
                       #self.ccnps = psline.amount
                       #print "self.ccnps = formatl(psline.amount)"
                       #print self.ccnps
                       #return formatl(psline.amount)




                #if psline.category_id.code == 'BRUT':
                   # if  psline.code == self.C_CNPS:
                      #  print "ok"
                     #   print formatl(psline.amount)
                     #   return formatl(psline.amount)
        else:
            res = ''
        return res

    def get_rate_salarial(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        res = ''

        category_ids = env['hr.salary.rule.category'].search([('code', '=','BASE_CNPS')])
        print (category_ids)

        if psline.category_id in category_ids:
            if psline.category_id.code in [self.C_CNPS]:
                print  (psline.code)

                #if psline.code in [self.C_ITS, self.C_CNPS]:
                   # print  psline.code
                    #if psline.code == self.C_ITS:
                      # return 1.2
                if psline.category_id.code == 'RET':
                    if psline.code == self.C_CNPS:
                   # if psline.code == 'CNPS':
                       print ("6.3")



        #if round(float(psline.rate), 2) == 100.00 or round(float(psline.rate), 2) == 0.00:
        return ''
        #return psline.rate
        #return formatl(psline.rate, 2)

    def get_worked_hours(self, slip, code='WORK100'):
       # return formatl(slip.get_worked_hours(code), 2)
        return slip.get_worked_hours(code)

    def get_gain_salarial(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        if round(float(psline.total), 2) == 0.00:
            return ''
        #self.C_SYN,
        category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_RED, self.C_DED, self.C_TAX, self.C_PAYB, self.C_RETN])])

        if psline.category_id in category_ids:
            return ''

         #if psline.code == '100':
        if psline.code == '100':
            if psline.slip_id.contract_id.time_mod == 'fixed' and \
                    psline.slip_id.contract_id.time_fixed == psline.slip_id.get_worked_hours('WORKED') and \
                    psline.slip_id.get_worked_hours('WORK100') == psline.slip_id.get_worked_hours('WORKED'):

                return psline.slip_id.contract_id.wage
                #return formatl(psline.slip_id.contract_id.wage)
            else:
                return round(float(psline.total))
                #return formatl(round(float(psline.total)))
#                return formatl(math.ceil(float(psline.total)))
        return psline.total
        #return formatl(psline.total)

    def get_deduction_salarial(self, psline):
        ded = 0
        env = odoo.api.Environment(self.cr, self.uid, {})
        if round(float(psline.total), 2) == 0.00:
            tax_cat_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_TAX])])
            if psline.category_id in tax_cat_ids:  # for tax return 0 instead of ''
                return 0
            return ''
        # self.C_SYN,
        category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_RED, self.C_DED, self.C_TAX, self.C_PAYB, self.C_RETN])])

        if psline.category_id in category_ids:
            ded = psline.total
            #ded = formatl(psline.total)

        return ded
        #return ''

    def _get_retenues(self,obj):
        res=''
        #line_obj=self.pool.get('hr.payslip.line') if line.code in ('RET','DED','TAX','TAXX','RED','PAYB','RETN','AVCE','CN','CNPS','IGR','TAXEFP','ITS','ITS_P','CNPS_P','TAXEAP'):
        for id in range(len(obj)):
            line_ids = obj[id]
            for line in line_ids :
                if line.code in ('RET','DED','TAX','TAXX','RED','PAYB','RETN','AVCE','CN','CNPS','IGR','ITS','PSCA','PBIB'):
                    res =line.amount
        return res

    def _get_gain(self,obj):
        env = odoo.api.Environment(self.cr, self.uid, {})
        res = ''
        line_obj=env['hr.payslip.line']
        for id in range(len(obj)):
            line_ids = obj[id]
            for line in line_ids :
               if line.code in ('BASE','SURSA','INDML','PANC','BRUT','BRUT_TOTAL','NET','BASEH','TRSP_IMP','AF','AFEE','ALD','APT','CARBU','AVTGN','APVF','AVN','BON',
                                'GRAT','HS15','HS50','HS75','PDC','PEL','PRD','PRG','PSC','PVE','PFO','PJE','PTEL','PEX','PDR','HS100','TRSP','TGA'):
                    res =line.amount

        return res


    def _get_net(self,obj):
        res=0
        for id in range(len(obj)):
            line_ids = obj[id]
            for line in line_ids :
                if line.code =='NET':
                    res =line.amount
        return res

    def _get_net_paie(self,obj):
        res = 0
        for id in range(len(obj)):
            line_ids = obj[id]
            for line in line_ids:
                for l in line:
                     for ligne in l.line_ids:
                         if ligne.amount != 0 and ligne.code == 'NET':
                             res += ligne.amount

                    #if line.code == 'NET':
                      #  res += line.total
        return res

    def get_payslip_lines(self, lines_ids):
        #env = odoo.api.Environment(self.cr, self.uid, {})

        payslip_line = self.env['hr.payslip.line']
        res = []
        ids = []
        for idx in range(len(lines_ids)):
            if lines_ids[id].appears_on_payslip is True:
                ids.append(lines_ids[idx].id)
        if ids:
            res = payslip_line.browse(ids)


        return res





    def get_rate_patronal(self, psline):
        rat =0
        env = odoo.api.Environment(self.cr, self.uid, {})
        psline_code_comp = psline.code + '_C'
        pooler = env['hr.payslip.line']
        payslip_line_comp_id = pooler.search([('slip_id', '=', psline.slip_id.id), ('code', '=', psline_code_comp)])
        payslip_line_comp = pooler.browse(payslip_line_comp_id.id)

        if payslip_line_comp:
            rate =payslip_line_comp[0].rate

            if round(float(rate), 2) == 100.00:
                return ''
                rat = rate
                #rat = formatl(rate, 2)

       # return ''
        return rat

    def _get_taux(self, psline):
        res = ''
        for id in range(len(psline)):
            line_ids = psline[id]
            for line in line_ids:
                if line.code in ['ITS','ITS_P']:
                    return 1.2
                if line.code in ['CNPS','CNPS_P']:
                    return 6.3

    def _get_taux_patronal(self, psline):
        res = ''
        for id in range(len(psline)):
            line_ids = psline[id]
            for line in line_ids:
                if line.code=='TAXEAP':
                    return 0.04
                if line.code == 'TAXEFP':
                    return 0.06
                if line.code == 'PF':
                    return 5.75
                if line.code == 'ACT':
                    return 2
                if line.code == 'CNPS_P':
                    return 7.7


    def get_contribution_patronal_plus(self, psline):
        res = ''
        for id in range(len(psline)):
            line_ids = psline[id]
            for line in line_ids :
                if line.code in ('TAXEAP','ITS_P','PF','ACT','TAXEFP','TCOMP','CNPS_P'):
                    res =line.amount


        #env = odoo.api.Environment(self.cr, self.uid, {})
       # res = ''
        #global total
       # global panc
       # category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_RET_EMP,'CPATR'])])
        #if psline.category_id in category_ids:
           # if psline.category_id.code in [self.C_RET_EMP,'CPATR']:
              #  print psline.category_id.code
               # if psline.code in [self.C_ITS_P, self.C_CNPS_P,self.C_TAXEAP,self.C_ACT,self.C_PF]:
                    #print psline.code
                   # res = psline.amount
                    #res = formatl(psline.amount)
        return res



    def get_contribution_patronal(self, psline):
        tot = 0
        env = odoo.api.Environment(self.cr, self.uid, {})
        psline_code_comp = psline.code + '_C'
        pooler = env['hr.payslip.line']
        payslip_line_comp_id = pooler.search([('slip_id', '=', psline.slip_id.id), ('code', '=', psline_code_comp)])
        payslip_line_comp = pooler.browse(payslip_line_comp_id.id)
        if payslip_line_comp:
            total = payslip_line_comp[0].total
            if round(float(total), 2) == 0.00:
                return ''
            tot= total
            #tot= formatl(total)
        return tot
        #return ''

    def get_payslip_lines_total(self, lines_ids, timeref='MONTH'):
        """
        Read the monthly and the yearly sum lines for the bottom table and
             save them in a dict object according to timeref MONTH or YEAR
        Returns a pseudo dict object {(PSEUDO, '')}
        """
        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_line = env['hr.payslip.line']

        if timeref == 'MONTH':
            res = dict.fromkeys(['1100', '1200', '1300', '1400', '1500', 'B100', '1600', '1700', '1000', '1020'], 0.00)
            category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_TOTM, self.C_NET])])
            #category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.TOTM, self.NET])])
        else:
            res = dict.fromkeys(['2100', '2200', '2300', '2400', '2500', '2600', '2700', '2000', '2020'], 0.00)
            category_ids = env['hr.salary.rule.category'].search([('code', '=', self.C_TOTA)])
            #category_ids = env['hr.salary.rule.category'].search([('code', '=', self.TOTA)])

        ids = []
        for idx in range(len(lines_ids)):
            if (lines_ids[idx].appears_on_payslip is True):
                ids.append(lines_ids[idx].id)
        if ids:
            payslip_line_total = payslip_line.browse(ids)
            if payslip_line_total:
                for linx in range(len(payslip_line_total)):
                    if payslip_line_total[linx].code in res.keys():
                        d = dict.fromkeys([payslip_line_total[linx].code], payslip_line_total[linx].total)
                        res.update(d)

        if timeref == 'MONTH':
            self.total_m = res
        else:
            self.total_y = res
        return dict.fromkeys(['PSEUDO'], '')



    def get_total(self, timeref, key, lines_ids=None):
        if len(self.total_m) == 0 and bool(lines_ids):
            self.get_payslip_lines_total(lines_ids, 'MONTH')
        if len(self.total_y) == 0 and bool(lines_ids):
            self.get_payslip_lines_total(lines_ids, 'YEAR')
        total = (self.total_y if timeref == 'YEAR' else self.total_m)
        res = total.get(key, '')
        if res == '':
            return ''
        if round(float(res), 2) == 0.00:
            return ''
        if key in ['B100', '1500', '1600', '2500', '2600']:
            return res
        #return formatl(res, 2)
        else:
            return res
            #return formatl(res)

        return res
        #return formatl(res)


    def get_somme_rubrique(self, obj, code):
        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_ids = env['hr.payslip'].search(self.cr, self.uid, [('employee_id', '=', obj.employee_id.id)])
        payslip_obj = env['hr.payslip'].browse(self.cr, self.uid, payslip_ids)

        cpt = 0
        annee = obj.date_to[2:4]

        for payslip in payslip_obj:
            for line in payslip.line_ids:
                if line.salary_rule_id.code == code and obj.date_to >= payslip.date_to and payslip.date_to[
                                                                                           2:4] == annee:
                    cpt += line.total
        return cpt

    def get_amount_rubrique(self, obj, rubrique):

        total = 0
        for id in range(len(obj)):
          line_ids = obj[id]
          for line in line_ids:
            if line.code == rubrique:
                total = line.total
        return total
		
    def get_employer_line_rate(self, obj, rule):

        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_line=env['hr.payslip.line']
        line_ids =payslip_line.search([('slip_id', '=',obj.id),('salary_rule_id.parent_rule_id.id', '=', rule )])
        res=line_ids and payslip_line.browse(line_ids[0].id).rate or False
          
        return res
		
    def get_employer_line_amount(self, obj, rule):

        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_line=env['hr.payslip.line']
        line_ids =payslip_line.search([('slip_id', '=',obj.id),('salary_rule_id.parent_rule_id.id', '=', rule )])
        res=line_ids and payslip_line.browse(line_ids[0].id).total or False
        total=float(res)
          
        return res
		
    def get_amount_total(self,amount):         
        return float(amount)
		

		

			
	#afficher le total d'une categorie		
    def get_total_by_rule_category(self, obj, code):
        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_line=env['hr.payslip.line']
        rule_cate_obj=env['hr.salary.rule.category']

        cate_ids = rule_cate_obj.search([('code', '=', code)])
        category_total = 0.0
        if cate_ids:
            line_ids = payslip_line.search([('slip_id', '=', obj.id),('category_id.id', '=', cate_ids[0].id )])
            for l in line_ids:
                 category_total=category_total+l.total

        return category_total

class WrappedErgobitReportPayslip(models.AbstractModel):
    _name = 'report.l10n_syscoa_payroll.syscoa_report_payslip'
    _inherit = 'report.abstract_report'
    _template = 'l10n_syscoa_payroll.syscoa_report_payslip'
    _wrapped_report_class = ErgobitPayslipReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
