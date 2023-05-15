# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from odoo import api, fields, models, tools


class BookReport(models.Model):
    _name = "book.report"
    _description = "Livre de paie"
    _auto = False
    _order = 'name_related asc, salary_rule_id asc'

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('verify', 'En attente'),
        ('done', 'Terminé'),
        ('cancel', 'Rejeté')
        ], 'Statut', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employe', readonly=True)
    name_related = fields.Char('Nom et prenoms', readonly=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Rubrique', readonly=True)
    total = fields.Float('Montant', readonly=True)
    date_from = fields.Date('Date de debut', readonly=True)
    date_to = fields.Date('Date de fin', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'book_report')
        self._cr.execute("""
            create view book_report as (
			
			select min(b.id) as id , a.state as state ,c.id as employee_id ,c.name as name_related , b.salary_rule_id as salary_rule_id ,b.total as total,a.date_from as date_from , a.date_to as date_to from hr_payslip a, hr_payslip_line b , hr_employee c 

			where a.id=b.slip_id and c.id=a.employee_id

			group by c.id,c.name ,a.state,b.salary_rule_id,b.total,date_from,date_to

			order by c.name asc
                
            )""")
        
