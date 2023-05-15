# -*- coding: utf-8 -*-

import base64
import datetime
import hashlib
import pytz
import threading

from email.utils import formataddr
from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.osv.orm import browse_record
from datetime import datetime
from datetime import date
from datetime import timedelta

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import html_translate


class DemandeActeCaisseLine(models.Model):
    _name = "demande.acte.caisse.line"
    #_inherit = ['etat.civil.naissance']
    _description = "Demande Acte Civil"
    _order = "date_ajout desc"
    
    
    
    #===========================================================================
    # @api.multi
    # def _get_default_code(self):
    #     if self.code == False or "/":
    #         seq = self.env['ir.sequence'].next_by_code('demande.acte.caisse.line')
    #     return seq
    #===========================================================================
    
    def _get_default_user_id(self):
        return self.env.uid
    
    
    code = fields.Char(string="Code")
    name = fields.Char(string="Nom")
    user_id = fields.Many2one("res.users", string="Agent", default=_get_default_user_id)
    date_ajout = fields.Datetime("Date de la demande", default=lambda self: fields.datetime.now())
    quantity = fields.Integer(string="quantité")
    type_acte = fields.Char(string="Type d'acte")
    quantity = fields.Integer(string="quantité")
    unit_price = fields.Float(string="Prix Unitaire")
    amount = fields.Float(string="Montant")
    demande_acte_caisse_id = fields.Many2one("demande.acte.caisse", string="")
    state = fields.Selection(string="Etat", selection=[
                            ('draft', 'Brouillon'),
                            ('confirm', 'Confirmé'),
                            ('approved', 'Approuvé'),
                            ('valid', 'Validé'),
                            ('cancel', 'Annulé/Rejeté')
                            ], default='draft')
    active = fields.Boolean('Active', default=True)
    
    
    
    
    # fonction pour les etats
    @api.multi
    def button_draft(self, force=False):
        self.write({'state': 'draft'})
        
    @api.multi
    def button_confirm(self, force=False):
        
        self.write({'state': 'confirm'})
            
    @api.multi
    def button_approved(self, force=False):
        self.write({'state': 'approved'})

    @api.multi
    def button_valid(self, force=False):
        self.write({'state': 'valid'})

    @api.multi
    def button_cancel(self, force=False):
        self.write({'state': 'cancel'})
    

    
    