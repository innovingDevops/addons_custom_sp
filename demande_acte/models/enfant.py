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

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import html_translate


class DemandeActeEnfant(models.Model):
    _name = "demande.acte.enfant"
    #_inherit = ['etat.civil.naissance']
    _description = "Enfants a charge"
    #_order = "date_ajout desc" 
    
    demande_acte_id = fields.Many2one('demande.acte', string="Nom du demandeur")
    code = fields.Char(string="N°", track_visibility="always")
    name = fields.Char(string="Nom entier enfant ", track_visibility="always")
    lieu_naissance = fields.Char(string="Lieu de naissance")
    birthday = fields.Date(string="Date de naissance")
    birthday_str = fields.Text(string="En lettre" ,compute='get_date_letter')
    active = fields.Boolean('Active', default=True)
    
    
    
    @api.one
    @api.depends('birthday')
    def get_date_letter(self):
        if self.birthday:
            nj = {'0': 'lundi','1': 'mardi','2': 'mercredi', '3': 'jeudi', '4': 'vendredi','5': 'samedi', '6': 'dimanche'}
            nm = {'1': 'janvier','2': 'février', '3': 'mars', '4': 'avril','5': 'mai', '6': 'juin', '7': 'juillet','8': 'août','9': 'septembre', '10': 'octobre','11': 'novembre', '12': 'décembre' }
            njj = {'1': 'premier','2': 'deux','3': 'trois', '4': 'quatre', '5': 'cinq','6': 'six','7': 'sept',
                  '8':'huit','9':'neuf','10':'dix','11':'onze','12':'douze','13':'treize','14':'quatorze',
                  '15':'quinze','16':'seize','17':'dix-sept','18':'dix-huit','19':'dix-neuf','20':'vingt',
                  '21':'vingt et une','22':'vingt-deux','23':'vingt-trois','24':'vingt-quatre','25':'vingt-cinq',
                  '26':'vingt-six','27':'vingt-sept','28':'vingt-huit','29':'vingt-neuf','30':'trente',
                  '31':'trente et un'}
            
            #raise UserError(_("%s") % (type(self.birthday)))
            #ma_date = datetime.strptime(self.birthday, "%Y-%m-%d")
            
            ma_date = datetime.strptime(str(self.birthday), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            self.birthday_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ annee
    
    
    
    
    @api.onchange('name')
    def caps_name(self):
        if self.name :
            self.name = str(self.name).title()
        return