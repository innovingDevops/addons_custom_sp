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


class EtatCivilRegistre(models.Model):
    _name = "etat.civil.registre"
    #_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Etat Civil Registre"
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
    active = fields.Boolean('Active', default=True)
    
    @api.multi 
    def open_registre_naissance(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'etat.civil.naissance', 
            'name': 'Naissance', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'target': 'current', 
        }
        
    @api.multi 
    def open_registre_mariage(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'etat.civil.mariage', 
            'name': 'Mariage', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'target': 'current', 
        }


    @api.multi 
    def open_registre_deces(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'etat.civil.deces', 
            'name': 'Deces', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'target': 'current', 
        }