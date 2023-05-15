# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.report import report_sxw
from itertools import groupby


class ReportHrPayroll(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportHrPayroll, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            '_lines': self._lines,
        })

    _codes_rules = []

    def _lines(self, date_from, date_to):
        res = {}
        resultats = []
        _headers = ['NOM ET PRENOMS']
        rules = self.env['hr.salary.rule'].search([('appears_on_payroll', '=', True)])
        emp_obj = self.env['hr.employee']
        date_from = date_from
        date_to = date_to
        print "---------------------------------------------------------------------------------------------------------"
        for rule in rules :
            print rule.name
            _headers.append(rule.name)
        print "---------------------------------------------------------------------------------------------------------"
        self._codes_rules = rules.mapped(lambda r: r.code)
        res['codes'] = self._codes_rules
        res['headers'] = _headers
        self.env.cr.execute("SELECT id FROM hr_payslip WHERE (date_from between to_date(%s,'yyyy-mm-dd') AND "
            "to_date(%s,'yyyy-mm-dd')) AND (date_to between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (date_from, date_to ))
        payslip_ids = [x[0] for x in self._cr.fetchall()]
        if payslip_ids :
            payslips= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
            print payslips
            for employee, lines in groupby(payslips, lambda l: l.employee_id):
                vals = {'NAME': employee.name}
                print vals
                print employee
                slips = list(lines)
                for rule in self._codes_rules :
                    amount = 0.0
                    for slip in slips :
                        self.env.cr.execute("SELECT SUM(total) FROM hr_payslip_line WHERE slip_id=%s AND code=%s",
                                     (slip.id, rule))
                        result = self.env.cr.dictfetchall()
                        if result :
                            amount+= result[0].get('sum')
                    print amount
                    vals[rule] = amount
                print vals
                resultats+=[vals]
        res['lines']= resultats
        print res
        return res

    def _lines_total(self, codes, lines):
        res = {}
        for code in codes :
            total = 0
            for line in lines :
                if line[code] is not None :
                    total+= line[code]
            res[code] = total
        return res

    #@api.model
    #def render_html(self, docids, data=None):
       # print self.context
        #self.model = self.env.context.get('active_model')
       # self.model = data['model']
       # docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        #docs = self.env[self.model].browse(data['ids'])
        #print data['form']
        #results = self._lines(data['form']['date_from'], data['form']['date_to'])
        #lines = results['lines']
        #codes = results['codes']
        #headers = results['headers']
       # lang_code = self.env.context.get('lang') or 'en_US'
       # lang = self.env['res.lang']
        #lang_id = lang._lang_get(lang_code)
        #date_format = lang_id.date_format
        #date_from = datetime.strptime(data['form']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        #date_to = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        #total = self._lines_total(codes, lines)

       # docargs = {
          #  'doc_ids': self.ids,
           # 'doc_model': self.model,
           # 'data': data['form'],
            #'docs': docs,
            #'date_from': date_from,
            #'date_to': date_to,
            #'lines': lines,
           # 'lines_total': total,
           # 'codes': codes,
            #'headers': headers,
            #'time': time,
            #'format_amount': format_amount,
       # }
       # return self.env['report'].render('l10n_syscoa_payroll.report_payroll', docargs)

class wrapped_report_livre(models.AbstractModel):
        _name = 'report.l10n_syscoa_payroll.report_payroll'
        _inherit = 'report.abstract_report'
        _template = 'l10n_syscoa_payroll.report_payroll'
        _wrapped_report_class = ReportHrPayroll
