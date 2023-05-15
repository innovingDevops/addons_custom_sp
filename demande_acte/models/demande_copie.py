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
#from datetime import datetime
#from datetime import date

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import html_translate

from datetime import date, datetime, timedelta
import time
#from odoo.addons_custom import etat_civil
#from odoo.custom-addons import etat_civil


class DemandeActeDemande(models.Model):
    _name = "demande.acte.demande"
    #_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Demande Acte Demande"
    #_order = "date_ajout desc"
    
    def _get_default_user_id(self):
        return self.env.uid

    def _creat_year(self):
        created_year = datetime.today().year
        return created_year
    
    
    def _creat_month(self):
        created_month = datetime.today().month
        return created_month
    
    code = fields.Char(string="Code", track_visibility="always")
    name = fields.Char(string="Nom", track_visibility="always")
    type = fields.Char(string="", track_visibility="always")
    active = fields.Boolean('Active', default=True)
    
    
    @api.multi 
    def open_demande_acte_naissance(self):
         
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Copie acte de naissance', 
            'view_type': 'form', 
            'view_mode': 'form',
            #'type_acte':'an', 
            'context':{'default_type_acte':'an'},
            'target': 'current', 
        }
        
    @api.multi 
    def open_demande_acte_mariage(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Copie acte de mariage', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'am'},
            'target': 'current',  
        }


    @api.multi 
    def open_demande_acte_deces(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Copie acte de deces', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'ad'},
            'target': 'current', 
        }
        
    @api.multi 
    def open_demande_cpi_acte_naissance(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Copie integrale naissance', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'cian'},
            'target': 'current', 
        }
        
    @api.multi 
    def open_demande_cpi_acte_mariage(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Copie integrale mariage', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'ciam'},
            'target': 'current', 
        }
        
    @api.multi 
    def open_demande_cpi_acte_deces(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Copie integrale deces', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'ciad'},
            'target': 'current', 
        }
        
    @api.multi 
    def open_demande_certificat_vie(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Certificat de vie', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'cv'},
            'target': 'current', 
        }
        
    @api.multi 
    def open_demande_certificat_vie_entretien(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Certificat de vie et entretien', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'cve'},
            'target': 'current', 
        }
    
    @api.multi 
    def open_demande_certificat_non(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'demande.acte', 
            'name': 'Certificat de non', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'context':{'default_type_acte':'cn'},
            'target': 'current', 
        }
        
        
    #===========================================================================
    # @api.onchange('type_acte')
    # def onchange_etat_civil(self):
    #     if self.type_acte:
    #         if self.type_acte == "an":
    #                 if self.etat_civil_naissance_id: # si le numero est existe
    #                     self.name = self.code
    #                     
    #         else:
    #             raise UserError(_("Recherche non conforme !"))
    #     return {}
    #===========================================================================