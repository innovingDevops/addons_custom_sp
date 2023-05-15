# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
import calendar
from openerp.exceptions import ValidationError, Warning

import logging

class Exercice(models.Model):
    _name = 'exercice'

    name = fields.Char(
        string='Exercice'
    )

    date_from = fields.Date(
        string='Date de début'
    )

    date_to = fields.Date(
        string='Date de fin'
    )

    code = fields.Char(
        string='Code'
    )

    journal_id = fields.Many2one(
        'account.journal',
        string="Journal des opérations de fin d'année"
    )

    period_ids = fields.One2many(
        'periode',
        'exercice_id',
        string="Périodes"
    )

    have_periods = fields.Boolean(
        default=False
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.user.company_id.id
    )
    state = fields.Selection(
        string='État',
        selection=[('open', 'Ouvert'), ('close', 'Fermé')],
        default='open',
    )
    tri_ou_men = fields.Boolean(
        string='Pour type de période')

    _sql_constraints = [
        ('unique_code', 'UNIQUE (code)', "Le code d'exercice exist déjà"),
        ('unique_name', 'UNIQUE (name)', "Le nom d'exercice exist déjà")
    ]

    @api.one
    def create_period_quarterly(self):
        self.with_context({'period_monthly': 3}).create_period_monthly()
        return True

    @api.one
    def create_period_monthly(self):
        self.check_year()
        self.check_period()

        interval = self._context.get('period_monthly') or 1
        period_obj = self.env['periode']
        date_from = self.date_from
        period_obj.create({
            'name':  "Période d'ouverture " + date_from.strftime('%Y'),
            'code': date_from.strftime('00/%Y'),
            'date_from': date_from,
            'date_to': date_from,
            'is_opening_date': True,
            'exercice_id': self.id,
        })

        while date_from < self.date_to:
            date_to = date_from + relativedelta(months=interval, days=-1)
            if date_to > self.date_to:
                date_to = self.date_to

            period_obj.create({
                'name': date_from.strftime('%m/%Y'),
                'code': date_from.strftime('%m/%Y'),
                'date_from': date_from,
                'date_to': date_to,
                'exercice_id': self.id,
            })
            date_from = date_from + relativedelta(months=interval)

        period_obj.create({
            'name': 'Période de clôture ' + self.date_to.strftime('%Y'),
            'code': self.date_to.strftime('99/%Y'),
            'date_from': self.date_to,
            'date_to': self.date_to,
            'is_closing_date': True,
            'exercice_id': self.id,
        })

        self.have_periods = True

        return True

    def check_year(self):
        if self.date_from.year != self.date_to.year:
            raise ValidationError('La période de cet exercice doit se trouver sur une même année')

    def check_period(self):
        if self.date_to < self.date_from:
            raise ValidationError('Période incorrecte')
