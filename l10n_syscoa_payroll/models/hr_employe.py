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




class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _get_part_igr(self):
        result = 0
        if self.marital :
            t1 =self.marital
            B38 = t1[0]
            B39 = self.children
            B40 = self.children

            if ((B38 == "s") or (B38 == "d")):
                if (B39 == 0):
                    if (B40 != 0):
                        result = 1.5
                    else:
                        result = 1
                else:
                    if ((1.5 +  B39 * 0.5) > 5):
                        result = 5
                    else:
                        result = 1.5 + B39 * 0.5
            else:
                if (B38 == "m"):
                    if (B39 == 0):
                        result = 2
                    else:
                        if ((2 + 0.5 * B39) > 5):
                            result = 5
                        else:
                            result = 2 + 0.5 * B39
                else:
                    if (B38 == "w"):
                        if (B39 == 0):
                            if (B40 != 0):
                                result = 1.5
                            else:
                                result = 1
                        else:
                            if ((2 + B39 * 0.5) > 5):
                                result = 5
                            else:
                                result = 2 + 0.5 * B39
                    else:
                        result += 2 + 0.5 * B39
        # print result
        self.social_parts = result


    @api.multi
    def _calculate_coefficient(self):
        for line in self:
            if line.marital == 'married':
                coef = 2 if line.status_spouse == 'non_salaried' else 1
            else:
                coef = 1
            line.coef = coef

    @api.multi
    def _user_left_days(self):
        for employee in self:
            legal_leave = employee.company_id.legal_holidays_status_id
            values = legal_leave.get_days(employee.id)
            employee.leaves_taken = values.get('leaves_taken')
            employee.max_leaves = values.get('max_leaves')
        # print "congé"

    social_parts = fields.Float(compute="_get_part_igr", method=True, string="Nombre de parts sociales", store=False)
    ipres_id = fields.Char('N° CNPS')
    css_id = fields.Char('N° Sécurité Sociale')
    status_spouse = fields.Selection((('salaried', 'Salarié(e)'), ('non_salaried', 'Non-salarié(e)')), string='Statut du/de la conjoint(e)', default='salaried')
    coef = fields.Integer(compute="_calculate_coefficient", method=True, string="Coefficient de TRIMF", store=True)
    matricule = fields.Char('Matricule', size=64)
    max_leaves = fields.Float(compute="_user_left_days", string='Acquis', help='This value is given by the sum of all holidays requests with a positive value.',)
    leaves_taken = fields.Float(compute="_user_left_days", string='Pris', help='This value is given by the sum of all holidays requests with a negative value.',)


