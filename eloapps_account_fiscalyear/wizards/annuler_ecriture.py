# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import ValidationError,Warning

import logging

class AnnulerEcriture(models.TransientModel):
    _name = 'annuler.ecriture'

    exercice_id = fields.Many2one(
        'exercice',
        string='Exercice'
    )

    def annuler_lettrage(self, move_id):
        wizard_unreconcile = self.env['account.unreconcile'].with_context(active_ids=move_id.line_ids.ids).create({})
        wizard_unreconcile.trans_unrec()

    def cancel_ecriture(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']

        closing_period_id = self.env['periode'].search(['&',('exercice_id','=',self.exercice_id.id),
                                                            ('is_closing_date','=',True)])

        if not closing_period_id:
            raise ValidationError("L'exercice n'a pas une période de cloture")

        closing_move_id = account_move_obj.search(['&',('period_id','=',closing_period_id.id),
                                                       ('company_id','=',self.env.user.company_id.id)])

        if not closing_move_id:
            raise ValidationError("La pièce de clôture de l'exercice sélectionné n'existe pas")

        closing_move_line_id = closing_move_id.line_ids[1]
        opening_move_line_id = account_move_line_obj.search(['&',('full_reconcile_id','=',closing_move_line_id.full_reconcile_id.id),
                                                             '&',('full_reconcile_id','!=',False),
                                                                 ('move_id','!=',closing_move_id.id)], limit=1)
        opening_move_id = opening_move_line_id.move_id

        if opening_move_id:
            if not (opening_move_id.state != 'posted' and closing_move_id.state != 'posted'):
                raise ValidationError('Les pièces sont validées, il est plus possible de lancer le processus d\'annulation des écritures de clôture')

        if opening_move_id and opening_move_id.state != 'posted':
            self.annuler_lettrage(opening_move_id)
            opening_move_id.unlink()

        if closing_move_id and closing_move_id.state != 'posted':
            self.annuler_lettrage(closing_move_id)
            # ouvrir l'exercice
            closing_move_id.period_id.exercice_id.state = 'open'
            closing_move_id.unlink()





