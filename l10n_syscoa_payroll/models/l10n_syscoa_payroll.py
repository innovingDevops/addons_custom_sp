# -*- coding:utf-8 -*-
# #############################################################################
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
# #############################################################################

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError





class HrPayslip(models.Model):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _order = 'id desc'

    @api.onchange('contract_id')
    def onchange_contract(self):
        super(HrPayslip, self).onchange_contract()
        pay_mod = self.contract_id and self.contract_id.pay_mod or False
        leave_days = self.contract_id and self.contract_id.leave_days or 0
        self.pay_mod = pay_mod
        self.leave_days_won = leave_days

    @api.multi
    def action_payslip_done(self):
        for payslip in self:
            if not payslip.employee_id.address_home_id:
                raise UserError(_("L'employé '%s' n'a pas d'adresse personnelle. \nVeuillez renseigner son adresse personnelle dans la fiche de l'employé, \nonglet 'Information personnelle'") % (payslip.employee_id.name,))
        res = super(HrPayslip, self).action_payslip_done()
        # Set additional leaves
        for payslip in self:
            if payslip.leave_days_won > 0:
                if payslip.state == 'verify':
                    if payslip.credit_note:
                        pass
                        # Here we should have a info mesage w/o cancelling process
                        # raise Warning("Veuillez vérifier le congé.")
                    else:
                        payslip.employee_id.remaining_leaves = payslip.remaining_leaves + payslip.leave_days_won

        self.write({'pay_date': date.today()})
        return res

    @api.multi
    def _calculate_rendement(self):
        for line in self:
            if line.is_waste_collector:
                date_1 = datetime.strptime(str(line.date_from), '%Y-%m-%d')
                date_1 = datetime.strptime(str(str(date_1.year) + '-' + str(date_1.month) + '-' + str(26)), '%Y-%m-%d') + relativedelta.relativedelta(months=-1)
                date_1 = date_1.strftime('%Y-%m-%d')
                date_2 = datetime.strptime(str(line.date_to), '%Y-%m-%d')
                date_2 = datetime.strptime(str(str(date_2.year) + '-' + str(date_2.month) + '-' + str(25)), '%Y-%m-%d')
                date_2 = date_2.strftime('%Y-%m-%d')
                analytic_account = self.env['account.analytic.account'].search([('code', '=', line.employee_id.matricule)])
                if analytic_account == []:
                    line.update({'quantity_delivred': 0.00, 'amount_invoiced': 0.00})
                else:
                    cr = self.env.cr
                    cr.execute("""SELECT COALESCE(SUM(amount), 0.0) as amount, COALESCE(SUM(unit_amount), 0.0) as unit_amount \
                        FROM account_analytic_line \
                        WHERE account_id = %s AND date >= %s AND date <= %s""",
                               [analytic_account[0], date_1, date_2])
                    result = dict(cr.dictfetchone())
                    line.update({'quantity_delivred': result['unit_amount'], 'amount_invoiced': result['amount']})
                    # line. = result['unit_amount']
            else:
                line.update({'quantity_delivred': 0.00, 'amount_invoiced': 0.00})

    @api.multi
    def _get_waste_collector(self):
        for line in self:
            line.is_waste_collector = line.company_id.waste_collection_company

    @api.multi
    def _get_holiday_allowance(self):
        for line in self:
            line.holiday_allowance = 0.0
            if line.type in ['leaves', 'mix']:
                if line.holiday_allowance_manual:
                    line.holiday_allowance = float(line.holiday_allowance_manual_input)
                else:
                    # calculate the current month from contract
                    if line.contract_id:
                        gross_of_current_month = line.contract_id.wage \
                            + line.contract_id.additional_salary
                        # amount_of_current_month = float(gross_of_current_month / 12)
#                    # calculate the previous months validated payslips
#                    date_to = line.date_from
#                    date_from = date_to-367
#                    payslip_ids = self.pool.get('hr.payslip').search(cr, uid, \
#                                    [('employee_id', '=', line.employee_id), ('state', '=', 'done'), \
#                                     ('date_from', '>',  date_from), ('date_to', '<',  date_to)])
#                    for idx in range(len(lines_ids)):
# #                    date_from = datetime.strptime(str(line.date_from), '%Y-%m-%d')
# #                    date_from = datetime.strptime(str(str(date_to.year-1) + '-' + str(date_to.month+1) + '-' + str(01)), '%Y-%m-%d')
# #                    date_from = date_to.strftime('%Y-%m-%d')
# #                    mt = line.date_from-1
# if mt in [1, 3, 5, 7, 8, 10, 12]:
# #                        last_day_of_month = 31
# else:
# if mt == 2:
# #                            last_day_of_month = 28
# else:
# #                            last_day_of_month = 30
# #                    date_to = datetime.strptime(str(line.date_from), '%Y-%m-%d')
# #                    date_to = datetime.strptime(str(str(date_to.year) + '-' + str(date_to.month-1) + '-' + str(28)), '%Y-%m-%d')
# #                    date_to = date_to.strftime('%Y-%m-%d')
# #                    payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('date_from', '>=',  date_from), ('date_from', '<=',  date_to)])

                    gross_of_previous_month = 0.0
                    line.holiday_allowance = float(gross_of_current_month + gross_of_previous_month)

    @api.multi
    def _compute_leave_days(self):
        for record in self:
            employee_id = record.employee_id
            hr_holidays_status_pooler = self.env['hr.holidays.status']
            if employee_id:
                #                res[record.id] = {'leaves_taken': employee_id.leaves_taken, 'remaining_leaves': employee_id.remaining_leaves, 'max_leaves': employee_id.max_leaves}
                hr_holidays_status = hr_holidays_status_pooler.search([('id', 'in', [employee_id.company_id.legal_holidays_status_id.id,
                                                                                     employee_id.company_id.legal_holidays_status_id_n1.id,
                                                                                     employee_id.company_id.legal_holidays_status_id_n2.id])])
                leave_days = hr_holidays_status_pooler.get_days(hr_holidays_status, employee_id.id)
                record.update({
                    'leaves_taken': leave_days[employee_id.company_id.legal_holidays_status_id.id]['leaves_taken'] if employee_id.company_id.legal_holidays_status_id else 0.0,
                    'remaining_leaves': leave_days[employee_id.company_id.legal_holidays_status_id.id]['remaining_leaves'] if employee_id.company_id.legal_holidays_status_id else 0.0,
                    'max_leaves': leave_days[employee_id.company_id.legal_holidays_status_id.id]['max_leaves'] if employee_id.company_id.legal_holidays_status_id else 0.0,
                    'leaves_taken_n1': leave_days[employee_id.company_id.legal_holidays_status_id_n1.id]['leaves_taken'] if employee_id.company_id.legal_holidays_status_id_n1 else 0.0,
                    'remaining_leaves_n1': leave_days[employee_id.company_id.legal_holidays_status_id_n1.id]['remaining_leaves'] if employee_id.company_id.legal_holidays_status_id_n1 else 0.0,
                    'max_leaves_n1': leave_days[employee_id.company_id.legal_holidays_status_id_n1.id]['max_leaves'] if employee_id.company_id.legal_holidays_status_id_n1 else 0.0,
                    'leaves_taken_n2': leave_days[employee_id.company_id.legal_holidays_status_id_n2.id]['leaves_taken'] if employee_id.company_id.legal_holidays_status_id_n2 else 0.0,
                    'remaining_leaves_n2': leave_days[employee_id.company_id.legal_holidays_status_id_n2.id]['remaining_leaves'] if employee_id.company_id.legal_holidays_status_id_n2 else 0.0,
                    'max_leaves_n2': leave_days[employee_id.company_id.legal_holidays_status_id_n2.id]['max_leaves'] if employee_id.company_id.legal_holidays_status_id_n2 else 0.0,
                })
            else:
                #                res[record.id] = {'leaves_taken': 0, 'remaining_leaves': 0, 'max_leaves': 0}
                record.update({
                    'leaves_taken': 0,
                    'remaining_leaves': 0,
                    'max_leaves': 0,
                    'leaves_taken_n1': 0,
                    'remaining_leaves_n1': 0,
                    'max_leaves_n1': 0,
                    'leaves_taken_n2': 0,
                    'remaining_leaves_n2': 0,
                    'max_leaves_n2': 0
                })

    def _get_days_conge(self):
        # print "days"
        for payslip in self:
            days_number = 0.0
            for days in payslip.worked_days_line_ids:
                if days:
                    print (days.number_of_days)
                    days_number = days.number_of_days
            payslip.update({
                'days_number': days_number
            })

            #date1 = datetime.strptime(payslip.date_to, "%Y-%m-%d")
           # date2 = datetime.strptime(payslip.date_from, "%Y-%m-%d")
            #days_number = (date1 - date2).days

    type = fields.Selection((('salary', 'Salaire'), ('leaves', 'Congé'), ('mix', 'Salaire et Congé')), readonly=True, states={'draft': [('readonly', False)]}, required=True, default="salary", string="Type de bulletin")
    pay_date = fields.Date('Date de Paiement', default=lambda *a: time.strftime("%Y-%m-%d"))
    pay_mod = fields.Selection((('Virement', 'Virement'), ('Cheque', 'Chèque'), ('Espece', 'Espèce')), 'Mode de Paiement')
    is_waste_collector = fields.Boolean(compute="_get_waste_collector", method=True, store=False)
    quantity_delivred = fields.Float(compute="_calculate_rendement", method=True, digits_compute=dp.get_precision('Product UoS'), store=True,)
    amount_invoiced = fields.Float(compute="_calculate_rendement", method=True, digits_compute=dp.get_precision('Payroll'), store=True,)
    leave_days_won = fields.Float(string="À ajouter", readonly=True, states={'draft': [('readonly', False)]}, help="Le nombre de jours de congés acquis par l'emploi dans le mois payé.")
    max_leaves = fields.Float(compute="_compute_leave_days", string='Acquis', store=True, help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken = fields.Float(compute="_compute_leave_days", string='Pris', store=True, help='This value is given by the sum of all holidays requests with a negative value.',)
    remaining_leaves = fields.Float(compute="_compute_leave_days", string='Restant', store=True, help='Maximum Leaves Allowed - Leaves Already Taken',)
    max_leaves_n1 = fields.Float(compute="_compute_leave_days", string='Acquis N-1', store=True, help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken_n1 = fields.Float(compute="_compute_leave_days", string='Pris N-1', store=True, help='This value is given by the sum of all holidays requests with a negative value.',)
    remaining_leaves_n1 = fields.Float(compute="_compute_leave_days", string='Restant N-1', store=True, help='Maximum Leaves Allowed - Leaves Already Taken',)
    max_leaves_n2 = fields.Float(compute="_compute_leave_days", string='Acquis N-2', store=True, help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken_n2 = fields.Float(compute="_compute_leave_days", string='Pris N-2', store=True, help='This value is given by the sum of all holidays requests with a negative value.',)
    remaining_leaves_n2 = fields.Float(compute="_compute_leave_days", string='Restant N-2', store=True, help='Maximum Leaves Allowed - Leaves Already Taken',)
    holiday_allowance_manual = fields.Boolean("Montant brut de l'indemnité", readonly=True, states={'draft': [('readonly', False)]}, help="Le montant du droit de congé est normalement calculé automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    holiday_allowance_manual_input = fields.Float("Montant brut de l'indemnité", readonly=True, states={'draft': [('readonly', False)]}, digits_compute=dp.get_precision('Payroll'), help="Le montant du droit de congé est normalement calculé automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    holiday_allowance = fields.Float(compute="_get_holiday_allowance", method=True, string="Montant brut de l'indemnité", store=True, digits_compute=dp.get_precision('Payroll'), help="Le montant du droit de congé est normalement calculé automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    cn_amount = fields.Float(string="CN",compute='_amount_all', store=True)
    its_amount = fields.Float(string="ITS",compute='_amount_all', store=True)
    igr_amount = fields.Float(string="IGR",compute='_amount_all', store=True)
    cnps_amount = fields.Float(string="CNPS",compute='_amount_all', store=True)
    ret_amount = fields.Float(string="Total Retenues",compute='_amount_all', store=True)
    total_amount = fields.Float(string="Total",compute='_amount_all', store=True)
    brut_amount = fields.Float(string="BRUT",compute='_amount_all', store=True)

    cn_amount_store = fields.Float(related='cn_amount',string='CN', store=True)
    its_amount_store = fields.Float(related='its_amount', string='ITS', store=True)
    igr_amount_store = fields.Float(related='igr_amount', string='IGR', store=True)
    cnps_amount_store = fields.Float(related='cnps_amount', string='CNPS', store=True)
    ret_amount_store = fields.Float(related='ret_amount', string='Total Retenues', store=True)
    total_amount_store = fields.Float(related='total_amount', string='TOTAL', store=True)
    brut_amount_store = fields.Float(related='brut_amount', string='BRUT', store=True)


    days_number = fields.Float(compute='_get_days_conge', store=True,
                               string="Nombre de jours")



    def _get_retenues(self):
        lines = self.env['hr.payslip.line'].search([('slip_id','=',self.id)])
        # print "lines"
        # print lines

        for r in self:
            for line in r.line_ids:
                if line.code == 'ITS':
                    r.its_amount = line.amount
                if line.code == 'CN':
                    r.cn_amount = line.amount
                if line.code == 'IGR':
                   r.igr_amount = line.amount
                if line.code == 'CNPS':
                   r.cnps_amount = line.amount
                if line.code == 'RET':
                    r.ret_amount = line.amount
                if line.code == 'NET':
                   r.total_amount = line.amount

    @api.one
    @api.depends('line_ids.code')
    def _amount_all(self):
        for payslip in self:
            ret_amount = total_amount = cnps_amount = igr_amount = cn_amount = its_amount = 0.0
            for line in payslip.line_ids:
                if line.code == 'CN':
                   self.cn_amount = line.amount
                if line.code == 'ITS':
                  self.its_amount = line.amount
                if line.code == 'IGR':
                  self.igr_amount = line.amount
                if line.code == 'CNPS':
                  self.cnps_amount = line.amount
                if line.code == 'RET':
                   self.ret_amount = line.amount
                if line.code == 'NET':
                   self.total_amount = line.amount
                if line.code == 'BRUT':
                   self.brut_amount = line.amount
            #payslip.update({'cn_amount':payslip.cn_amount,
                           # 'its_amount':payslip.its_amount,
                           # 'igr_amount':payslip.igr_amount,
                            #'cnps_amount':payslip.cnps_amount,
                           # 'ret_amount':payslip.ret_amount,
                           # 'total_amount':payslip.total_amount,
                          #  'brut_amount':payslip.brut_amount
            #})

    @api.multi
    def get_worked_hours(self, code):
        """
        @return: the workday hours in the payslip by worked_days_line code.
        Mainly called from payslip report
        """
        result = 0.00
        for payslip in self:
            for wdline in payslip.worked_days_line_ids:
                if wdline.code == code:
                    result += wdline.number_of_hours
        return result

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
            day = fields.Date.to_string(datetime_day)
            return self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', day),
                ('date_to', '>=', day)
            ], limit=1).holiday_status_id.name

        res = []
        # fill only if the contract as a working schedule linked
        for contract in self.env['hr.contract'].browse(contract_ids):  # .filtered(lambda contract: contract.working_hours):
            attendances = {
                'name': _("Temps de travail contractuel"),
                # 'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}
            day_from = fields.Datetime.from_string(date_from)
            day_to = fields.Datetime.from_string(date_to)
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = contract.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                if working_hours_on_day:
                    # the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day))
                    if leave_type:
                        # if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        # add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        # attendances['number_of_hours'] += working_hours_on_day  # B replaced by the next 4 lines
                        if contract.time_mod == 'fixed':
                            attendances['number_of_hours'] = contract.time_fixed
                        else:
                            attendances['number_of_hours'] += working_hours_on_day

            if attendances['number_of_hours'] == 0.0:
                attendances['number_of_hours'] = contract.time_fixed

            leaves = [value for key, value in leaves.items()]

# B          add a placeholder for actually worked days/hours (to be entered by user if needed)
            actually_worked = {
                'name': _("Temps de travail effectif"),
                'sequence': 2,
                'code': 'WORKED',
                'number_of_days': attendances['number_of_days'],
                'number_of_hours': contract.time_fixed,
                'contract_id': contract.id,
            }

            res += [attendances] + [actually_worked] + leaves
        return res



class HrPayslipLine(models.Model):
    '''
    Payslip Line
    '''
    _name = 'hr.payslip.line'
    _inherit = 'hr.payslip.line'
	
    @api.multi
    def _amount(self):
        for line in self:
            if line.slip_id:
                if line.code == 'CN':
                    self.cn_amount = line.amount

    @api.multi
    def _calculate_total2(self):
        for line in self:
            line.total2 = float(line.quantity2) * line.amount2 * line.rate2 / 100

    rate2 = fields.Float('Rate2 (%)', digits_compute=dp.get_precision('Payroll Rate'), default=100.0)
    amount2 = fields.Float('Amount2', digits_compute=dp.get_precision('Payroll'))
    quantity2 = fields.Float('Quantity2', digits_compute=dp.get_precision('Payroll'), default=1.0)
    total2 = fields.Float(compute="_calculate_total2", method=True, string='Total2', digits_compute=dp.get_precision('Payroll'), store=True)
    cn_amount = fields.Float(compute="_amount", store=True, string="CN")







class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _order = 'id desc'
