# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

from odoo.tools.amount_to_text_frr import amount_to_text_fr


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    _name = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'


    @api.multi
    def compute_sheet(self):
        ttyme=""
        locale=""
        objet=""
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)

            ttyme = datetime.combine(fields.Date.from_string(from_date), time.min)
            locale = self.env.context.get('lang') or 'en_US'
            objet = 'SALAIRE DU MOIS DE %s' % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))

            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
                'hr_grade_id':employee.hr_grade_id.id,
                'hr_echelon_id':employee.hr_echelon_id.id,
                'account_fonctionnel_id': employee.contract_id.account_fonctionnel_id.id,
                'account_fonctionnel_code': employee.contract_id.account_fonctionnel_id.code,
                'numero_compte_id': employee.bank_account_id.id,
                'numero_compte': employee.bank_account_id.acc_number,
                'job_id': employee.job_id.id,
                'chapitre': employee.contract_id.chapitre,
                'analytic_account_id': employee.contract_id.analytic_account_id.id,
                'bank_id': employee.bank_account_id.bank_id.id,
                'compte': employee.contract_id.compte,
                'analytic_account_ref': employee.contract_id.analytic_account_id.code,
                'objet': objet,
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}
