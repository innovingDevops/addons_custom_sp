#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from odoo import osv
from odoo.report import report_sxw
import odoo
import time
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta


class payslip_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(payslip_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           # 'get_payslip_lines': self.get_payslip_lines,
            'get_payslip_lines_total': self.get_payslip_lines_total,
            'get_somme_rubrique': self.get_somme_rubrique,
            'get_amount_rubrique': self.get_amount_rubrique,
        })

    def get_payslip_lines(self, lines_ids):
        #env = odoo.api.Environment(self.cr, self.uid, {})
        print "oàààààààààààààààààààààààààààààààààààà"
        payslip_line = self.env['hr.payslip.line']
        res = []
        ids = []
        for idx in range(len(lines_ids)):
            if lines_ids[id].appears_on_payslip is True:
                ids.append(lines_ids[idx].id)
        if ids:
            res = payslip_line.browse(ids)
        print payslip_line
        print res

        return res

    def get_somme_rubrique(self, obj, code):

        payslip_ids = self.pool.get('hr.payslip').search(self.cr, self.uid, [('employee_id','=',obj.employee_id.id)])
        payslip_obj = self.pool.get('hr.payslip').browse(self.cr, self.uid, payslip_ids)

        cpt=0
        annee= obj.date_to[2:4]
        print(annee)
        for payslip in payslip_obj :
            for line in payslip.line_ids :
                if line.salary_rule_id.code == code and obj.date_to >= payslip.date_to and  payslip.date_to[2:4]==annee :
                    cpt += line.total
        return cpt
                    
    def get_amount_rubrique(self,obj,rubrique):
        for id in range(len(obj)):
            line_ids=obj[id].line_ids
            total=0
            for line in line_ids :
                if line.code == rubrique :
                    total = line.total
            print total
            return total
                    
class wrapped_report_payslip(osv.AbstractModel):
    _name = 'report.l10n_syscoa_payroll.report_payslip'
    _inherit = 'report.abstract_report'
    _template = 'l10n_syscoa_payroll.report_payslip'
    _wrapped_report_class = payslip_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
