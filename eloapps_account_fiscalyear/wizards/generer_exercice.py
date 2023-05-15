# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from openerp.exceptions import ValidationError,Warning

import logging

class GenererExercice(models.TransientModel):
    _name = 'generer.exercice'

    date_from = fields.Date(
        string='Date de début'
    )

    date_to = fields.Date(
        string='Date de fin'
    )

    type_de_periode = fields.Selection(
        string='Type de période',
        selection=[('quarterly', 'Trimestrielle'), ('monthly', 'Mensuelle')],
    )
    #Un champ booléen pour vérifer le type de période
    tri_ou_men = fields.Boolean(
        string='Pour type de période',
        compute='check_tri_ou_men')
    #Une fonction qui retourne tri_ou_men (vrai si type de période = 'Mensuelle' et faux si ype de période = 'Trimestrielle')
    def check_tri_ou_men(self):
        if self.type_de_periode == 'quarterly':
            self.tri_ou_men = False
        else:
            self.tri_ou_men = True

    def generer_exercice(self):
        self.check_year()
        self.check_period()

        exercice_id = self.env['exercice'].create({
            'name': str(self.date_from.year),
            'code': str(self.date_from.year),
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        if self.type_de_periode == 'quarterly':
            exercice_id.create_period_quarterly()
        else:
            exercice_id.create_period_monthly()

        view_id = self.env.ref('eloapps_account_fiscalyear.exercice_form_view')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'exercice',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id' : view_id.id,
            'res_id':exercice_id.id,
        }

    def check_year(self):
        if self.date_from.year != self.date_to.year:
            raise ValidationError('La période de cet exercice doit se trouver sur une même année')

    def check_period(self):
        if self.date_to < self.date_from:
            raise ValidationError('Période incorrecte')
