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


class EtatCivilMaire(models.Model):
    _name = "etat.civil.maire"
    #_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Etat Civil Maire"
    #_order = "date_ajout desc"
    
    def _get_default_user_id(self):
        return self.env.uid

    def _creat_year(self):
        created_year = datetime.today().year
        return created_year
    
    
    def _creat_month(self):
        created_month = datetime.today().month
        return created_month
    
    
    name = fields.Char(string="Nom et prénoms", track_visibility="always")
    sexe = fields.Selection(string="Sexe", selection=[
        ('homme', 'Homme'),
        ('femme', 'Femme')
        ], track_visibility='always', default='')
    rang = fields.Selection(string="Rang", selection=[
        ('maire', 'Maire'),
        ('premier', '1 er adjoint au maire'),
        ('deuxieme', '2e adjoint au maire'),
        ('troisieme', '3e adjoint au maire'),
        ('quatrieme', '4e adjoint au maire'),
        ('cinquieme' , '5e adjoint au maire'),
        ('sixieme', '6e adjoint au maire'),
        ('septieme', '7e adjoint au maire'),
        ('huitieme', '8e adjoint au maire'),
        ('neuvieme', '9e adjoint au maire'),
        ('dixieme', '10e adjoint au maire')
        ], track_visibility='always', default='')
    active = fields.Boolean('Active', default=True)
    
    
    @api.onchange('name')
    def caps_name(self):
        if self.name:     
            self.name = str(self.name).title()   
        return