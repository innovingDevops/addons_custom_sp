
from datetime import datetime
from dateutil import parser
from dateutil import relativedelta
from odoo import models
from odoo.report import report_sxw
from datetime import date
import odoo
from odoo import fields,models

class BookReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(BookReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            '_get_lines_paie': self._get_lines_paie,
        })

    def _get_lines_paie(self,date_from,date_to):

        env = odoo.api.Environment(self.cr, self.uid, {})
       # self.cr.execute("select e.name_related as name, c.category as cate,j.name as poste,c.wage as wage,"
                        #"c.additional_salary as sural,c.transport as tp ,hp.cn_amount as cn,"
                        #" hp.cnps_amount as cnps,hp.ret_amount as ret,hp.total_amount as total,"
                        #"hp.brut_amount as brut, hp.its_amount as its,hp.igr_amount as igr " \
                       #" from hr_employee e,hr_contract c,hr_job j,hr_payslip hp " \
                       # " where e.job_id=j.id and e.id=c.employee_id and hp.employee_id=e.id "
                        #" and hp.contract_id=c.id "
                        #" and hp.create_date>=%s and hp.create_date<=%s"
                        #,(date_from, date_to,))
        #res = self.cr.dictfetchall()


        self.cr.execute("SELECT hr_employee.name_related AS name,hr_contract.wage AS wage, hr_contract.additional_salary AS sursal, "
                        "hr_contract.transport AS tp,hr_payslip.brut_amount AS brut,hr_payslip.cn_amount AS cn,hr_payslip.its_amount AS its," 
                        "hr_payslip.igr_amount AS igr,hr_payslip.cnps_amount AS cnps,hr_payslip.ret_amount AS ret, "
                        "hr_payslip.total_amount AS total,hr_contract.category AS cate,hr_job.name AS poste "
                        "FROM public.hr_payslip, public.hr_employee, public.hr_contract,public.hr_job "
                        "WHERE hr_payslip.contract_id = hr_contract.id AND hr_employee.id = hr_payslip.employee_id AND "
                        "hr_job.id = hr_employee.job_id AND hr_payslip.create_date BETWEEN %s and %s",(date_from, date_to,))
        resultat = self.cr.dictfetchall()
        print resultat
        return resultat


class wrapped_report_book(models.AbstractModel):
    _name = 'report.l10n_syscoa_payroll.report_book_pay'
    _inherit = 'report.abstract_report'
    _template = 'l10n_syscoa_payroll.report_book_pay'
    _wrapped_report_class = BookReport