# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from mock.mock import self
from odoo.tools.amount_to_text_frr import amount_to_text_fr


class InnovingMandatTransaction(models.TransientModel):
    _name = 'innoving.mandat.transaction'
    _description = 'Innoving mandat wizard de Reglement transaction'
    
    
    @api.model
    def _default_user_id(self):
        user_id = self.env.uid
        return user_id
    
    user_id = fields.Many2one('res.users',string='Utilisateur',default=_default_user_id)
    date_from = fields.Date('Date de debut',default=fields.Datetime.now)
    date_to = fields.Date('Date de fin',default=fields.Datetime.now)
    date = fields.Date('Date Operation',default=fields.Datetime.now)
    note = fields.Text('Note',default="NB: Tous les virement s et ch�ques sont confirm�s par Mme OUATTARAN'gniotin Fatoumata")
    type_reglement = fields.Selection([
        ('ESPECE', 'ESPECE'),
        ('CHEQUE', 'CHEQUE'),
        ('VIREMENT', 'VIREMENT'),
        ('CHEQUE-VIREMENT', 'CHEQUE-VIREMENT'),
        ('TOUS', 'TOUS'),
        ], string='Mode de reglement', track_visibility='always', default='CHEQUE-VIREMENT')
    journal_id = fields.Many2one('account.journal','Journal')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.account_id=self.partner_id.property_account_payable_id.id
            self.beneficiaire=self.partner_id.name
            return {}
        else:
            self.account_id= False
            self.beneficiaire = False
            return {}
        
    # new code ------------------------------

    

    
    
class InnovingMandatBalance(models.TransientModel):
    _name = 'innoving.mandat.balance'
    _description = 'Innoving mandat wizard de Reglement balance'
    
    
    @api.model
    def _default_user_id(self):
        user_id = self.env.uid
        return user_id

    
    user_id = fields.Many2one('res.users',string='Utilisateur',default=_default_user_id)
    date_from = fields.Date('Date de debut',default=fields.Datetime.now)
    date_to = fields.Date('Date de fin',default=fields.Datetime.now)
    date = fields.Date('Date Operation',default=fields.Datetime.now)
    note = fields.Text('Note',default="")
    state = fields.Selection([
        ('MANDAT DE PAIEMENT EN ATTENTE DE PAIEMENT', 'OR EN ATTENTE DE PAIEMENT'),
        ('MANDAT DE PAIEMENT EN ATTENTE DE REGULARISATION', 'OR EN ATTENTE DE REGULARISATION'),
        ('MANDAT DE PAIEMENT  EN PAIEMENT PARTIEL', 'OR EN PAIEMENT PARTIEL'),
        ('MANDAT DE PAIEMENT  EN ATTENTE DE PAIEMENT DGI', 'OR EN ATTENTE DE PAIEMENT DGI')
        ], string='Mode de paiement', track_visibility='always', default='MANDAT DE PAIEMENT  EN ATTENTE DE PAIEMENT')
    destinataire = fields.Text("A l'attention de ",default="""A l'attention de """)
    destinateur = fields.Text("Adresse ",default="""Le Directeur Général""")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.account_id=self.partner_id.property_account_payable_id.id
            self.beneficiaire=self.partner_id.name
            return {}
        else:
            self.account_id= False
            self.beneficiaire = False
            return {}
        
    # new code ------------------------------
