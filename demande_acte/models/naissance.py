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


class EtatCivilNaissance(models.Model):
    _inherit ='etat.civil.naissance'
    _name = 'etat.civil.naissance'
    
    demande_acte_ids = fields.One2many('demande.acte','etat_civil_naissance_id', string="Les demandes d'acte de naissance")
    
    