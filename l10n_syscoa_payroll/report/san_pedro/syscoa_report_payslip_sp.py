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

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from amount_to_text import amount_to_text 
# from amount_to_text_fr import amount_to_text_fr
import odoo






class WrappedErgobitReportPayslip(models.AbstractModel):
    _name = 'report.l10n_syscoa_payroll.syscoa_report_payslip'
    _description = 'Fiche de paie '
	
	
    def get_worked_hours(self, slip, code='WORK100'):
        return slip.get_worked_hours(code)
   

    @api.model
    def _get_report_values(self, docids, data=None):
        if not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        # target_move = data['form'].get('target_move', 'all')
        # date_from = fields.Date.from_string(data['form'].get('date_from')) or fields.Date.today()

        # if data['form']['result_selection'] == 'customer':
            # account_type = ['receivable']
        # elif data['form']['result_selection'] == 'supplier':
            # account_type = ['payable']
        # else:
            # account_type = ['payable', 'receivable']

        get_worked_hours=self.get_worked_hours
        # movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'])
        # movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'])
        # movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'])
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            # 'data': data['form'],
            'docs': docs,
            'time': time,
            'get_worked_hours': get_worked_hours,
            # 'get_direction': total,
            # 'company_id': self.env['res.company'].browse(
                # data['form']['company_id'][0]),
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
