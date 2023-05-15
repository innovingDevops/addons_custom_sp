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


class EtatCivilDeces(models.Model):
    _name = "etat.civil.deces"
    #_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Etat Civil Deces"
    _order = "date_ajout desc"
    
    def _get_default_user_id(self):
        return self.env.uid
    
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'CI')], limit=1)
        return country

    
    ref_registre = fields.Char(string="Numéro", track_visibility="always")
    date_registre = fields.Date("Du", track_visibility="always")
    surfixe = fields.Char(string="Surfixe", track_visibility="always", default="CSP/EC")
    name = fields.Char(string="N° registre", track_visibility="always")
    numero_acte = fields.Char(string="Acte N°", track_visibility="always")
    code = fields.Char(string="Code", track_visibility="always")
    user_id = fields.Many2one("res.users", string="Agent", default=_get_default_user_id)
    date_ajout = fields.Datetime("Date ajout", default=lambda self: fields.datetime.now())
    date_ajout_compare = fields.Date("Date ajout Copare", default=lambda self: fields.date.today())
    sexe = fields.Selection(string="Sexe", selection=[
                    ("masculin", "Masculin"),
                    ("feminin", "Feminin")
                    ], track_visibility="always", default="masculin")
    nom = fields.Char(string="Nom", track_visibility="always")
    prenom = fields.Char(string="Prénoms", track_visibility="always")
    date_deces = fields.Date(string="Date de déces", track_visibility="always")
    lieu_deces = fields.Char(string="Lieu de déces", track_visibility="always")
    birthday = fields.Date(string="Date de naissance", track_visibility="always")
    lieu_naissance = fields.Char(string="Lieu de naissance", track_visibility="always")
    commune_naissance_defunt = fields.Char(string="Commune", track_visibility="always")
    sous_prefecture_naissance_defunt = fields.Char(string="Sous préfecture ", track_visibility="always")
    profession = fields.Char(string="Profession", track_visibility="always")
    residence_defunt = fields.Char(string="Domilié a", track_visibility="always")
    nom_pere = fields.Char(string="Nom ", track_visibility="always")
    prenom_pere = fields.Char(string="Prénoms ", track_visibility="always")
    residence_pere = fields.Char(string="Domicilié a ", track_visibility="always")
    nom_mere = fields.Char(string="Nom ", track_visibility="always")
    prenom_mere = fields.Char(string="Prénoms ", track_visibility="always")
    residence_mere = fields.Char(string="Domicilié a ", track_visibility="always")
    nom_demandeur = fields.Char(string="Nom ", track_visibility="always")
    prenom_demandeur = fields.Char(string="Prénoms ", track_visibility="always")
    age_demandeur = fields.Integer(string="Age ", track_visibility="always")
    residence_demandeur = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_demandeur = fields.Char(string="Profession ", track_visibility="always")
    state = fields.Selection(string="Etat", selection=[
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('approuved' , 'Approuvé'),
        ('valid', 'Validé'),
        ('done' , 'Terminé'),
        ('cancel', 'Annulé/Rejeté')
        ], track_visibility='always', default='draft')
    heure_deces = fields.Integer(string='Heure de décès')
    date_confirm = fields.Date(string="Date de confirmation", track_visibility="always")
    date_approved = fields.Date(string="Date d'approbation", track_visibility="always")
    date_valid = fields.Date(string="Date de validation", track_visibility="always")
    date_done = fields.Date(string="Date clôture", track_visibility="always")    
    minute_deces = fields.Integer(string='Minute')
    heure_str = fields.Text(string='Heure en lettre', compute='get_heure_letter')
    birthday_str = fields.Text(string='En lettre', compute='get_date_letter')
    date_deces_str = fields.Text(string="Date de déces" ,compute='get_date_letter')
    document = fields.Many2many('etat.civil.document','etat_civil_document_deces_rel','etat_civil_deces_id','etat_civil_document_id', string="Type")
    cni_defunt = fields.Binary(string="CNI du defunt")
    cni_declarant = fields.Binary(string="CNI du déclarant")
    certificat_medical_deces= fields.Binary(string="Certificat médical de décès")
    maire_id = fields.Many2one("etat.civil.maire", string="Maire")
    country_id = fields.Many2one('res.country' ,string="Pays", default=_get_default_country)
    active = fields.Boolean('Active', default=True)
    
    
    @api.multi
    def button_draft(self, force=False):
        self.write({'state': 'draft'})
        
    @api.multi
    def button_confirm(self, force=False):
        fmt = '%Y-%m-%d'
        #=======================================================================
        # date_deces = self.date_deces
        # date_ajout = self.date_ajout
        #=======================================================================
        d1 = datetime.strptime(str(self.date_deces), fmt)
        d2 = datetime.strptime(str(self.date_ajout_compare), fmt)
        if d2 > d1:
            result=(d2 - d1).days
            if result <= 15 :
                self.duree_declaration = (d2 - d1).days
                self.write({'state': 'confirm', 'date_confirm': fields.Date.context_today(self)})
            else:
                raise ValidationError('Cette déclaration doit suivre le processus de déclaration de décès par audience foraine .')
        else:
            raise ValidationError('La date de décès ne doit pas être supérieure à la date de déclaration.')
        
        
    @api.multi
    def button_approuved(self, force=False):
        self.write({'state': 'approuved', 'date_approved': fields.Date.context_today(self)})

    @api.multi
    def button_valid(self, force=False):
        self.write({'state': 'valid', 'date_valid': fields.Date.context_today(self)})

    @api.multi
    def button_done(self, force=False):
        self.write({'state': 'done', 'date_done': fields.Date.context_today(self)})
        
    @api.multi
    def button_cancel(self, force=False):
        self.write({'state': 'cancel'})
    
    @api.onchange('ref_registre','date_registre')
    def onchange_numero_registre(self):
        if self.ref_registre:
            if self.date_registre:
                name = self.ref_registre + " du " + str(self.date_registre.strftime("%d/%m/%Y")) + " " + self.surfixe
                self.name = name
                self.code = name + "/DECES" 
                #raise UserError(_("%s") % (self.name))
        return {}
    
    
    @api.onchange('nom','nom_pere','nom_mere','nom_demandeur')
    def set_upper(self):
        if self.nom:
            self.nom = str(self.nom).upper()
        if self.nom_pere:
            self.nom_pere = str(self.nom_pere).upper()
        if self.nom_mere:
            self.nom_mere = str(self.nom_mere).upper()
        if self.nom_demandeur:     
            self.nom_demandeur = str(self.nom_demandeur).upper()                   
        return
    
    
    @api.onchange('prenom','prenom_pere','prenom_mere','prenom_demandeur')
    def caps_name(self):
        if self.prenom :
            self.prenom = str(self.prenom).title()
        if self.prenom_pere:
            self.prenom_pere = str(self.prenom_pere).title()
        if self.prenom_mere:
            self.prenom_mere = str(self.prenom_mere).title()
        if self.prenom_demandeur:     
            self.prenom_demandeur = str(self.prenom_demandeur).title()
        return
    
    
    
    @api.one
    @api.depends('birthday','date_deces')
    def get_date_letter(self):
        if self.birthday or self.date_deces:
            nj = {'0': 'lundi','1': 'mardi','2': 'mercredi', '3': 'jeudi', '4': 'vendredi','5': 'samedi', '6': 'dimanche'}
            nm = {'1': 'janvier','2': 'février', '3': 'mars', '4': 'avril','5': 'mai', '6': 'juin', '7': 'juillet','8': 'août','9': 'septembre', '10': 'octobre','11': 'novembre', '12': 'décembre' }
            njj = {'1': 'premier','2': 'deux','3': 'trois', '4': 'quatre', '5': 'cinq','6': 'six','7': 'sept',
                  '8':'huit','9':'neuf','10':'dix','11':'onze','12':'douze','13':'treize','14':'quatorze',
                  '15':'quinze','16':'seize','17':'dix-sept','18':'dix-huit','19':'dix-neuf','20':'vingt',
                  '21':'vingt et une','22':'vingt-deux','23':'vingt-trois','24':'vingt-quatre','25':'vingt-cinq',
                  '26':'vingt-six','27':'vingt-sept','28':'vingt-huit','29':'vingt-neuf','30':'trente',
                  '31':'trente et un'}
            nba = {'1': 'mille','2': 'deux mille','3': 'trois mille'}
            nbb = {'0': '','1': 'cent','2': 'deux cent','3': 'trois cent', '4': 'quatre cent', '5': 'cinq cent','6': 'six cent','7': 'sept cent',
                  '8':'huit cent','9':'neuf cent'}
            nbe = {'00': '','01': 'un','02': 'deux','03': 'trois', '04': 'quatre', '05': 'cinq','06': 'six','07': 'sept',
                  '08':'huit','09':'neuf','10':'dix','11':'onze','12':'douze','13':'treize','14':'quatorze',
                  '15':'quinze','16':'seize','17':'dix-sept','18':'dix-huit','19':'dix-neuf','20':'vingt',
                  '21':'vingt et un','22':'vingt-deux','23':'vingt-trois','24':'vingt-quatre','25':'vingt-cinq',
                  '26':'vingt-six','27':'vingt-sept','28':'vingt-huit','29':'vingt-neuf','30':'trente',
                  '31':'trente et un','32':'trente-deux','33':'trente-trois','34':'trente-quatre','35':'trente-cinq',
                  '36':'trente-six','37':'trente-spet','38':'trente-huit','39':'trente-neuf','40':'quarante','41':'quarante et un',
                  '42':'quarante-deux','43':'quarante-trois','44':'quarante-quatre','45':'quarante-cinq','46':'quarante-six',
                  '47':'quarante-sept','48':'quarante-huit','49':'quarante-neuf','50':'cinqante','51':'cinquante et un',
                  '52':'cinqante-deux','53':'cinqante-trois','54':'cinqante-quatre','55':'cinqante-cinq','56':'cinqante-six',
                  '57':'cinqante-sept','58':'cinqante-huit','59':'cinqante-neuf','60':'soixante','61':'soixante et un',
                  '62':'soixante-deux','63':'soixante-trois','64':'soixante-quatre','65':'soixante-cinq','66':'soixante-six',
                  '67':'soixante-sept','68':'soixante-huit','69':'soixante-neuf','70':'soixante-dix','71':'soixante-onze','72':'soixante-douze',
                  '73':'soixant-treize','74':'soixante-quatorze','75':'soixante-quinze','76':'soixante-seize','77':'soixante-dix-sept',
                  '78':'soixante-dix','79':'soixante-dix-neuf','80':'Quatre-vingts','81':'Quatre-vingts-un','82':'Quatre-vingts-deux' ,
                  '83':'Quatre-vingts-trois','84':'Quatre-vingts-quart',
                  '85':'Quatre-vingts-cinq','86':'Quatre-vingts-six','87':'Quatre-vingts-sept','88':'Quatre-vingts-huit','89':'Quatre-vingts-neuf',
                  '90':'Quatre-vingts-dix','91':'Quatre-vingts_onze','92':'Quatre-vingts-douze',
                  '93':'Quatre-vingts-treize','94':'Quatre-vingts-quatorze','95':'Quatre-vingts-quinze','96':'Quatre-vingts-seize','97':'Quatre-vingts-dix-sept',
                  '98':'Quatre-vingts-dix-huit','99':'Quatre-vingts-dix-neuf'}
            
            
            if self.birthday :
                ma_date = datetime.strptime(str(self.birthday), "%Y-%m-%d")
                jour = str(ma_date.day)
                num_jour = str(ma_date.weekday())
                mois = str(ma_date.month)
                annee = str(ma_date.year)
                a = str(annee[0])
                b = str(annee[1])
                c = str(annee[2])
                d = str(annee[3])
                e = str(c+d)
                self.birthday_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            if self.date_deces :
                ma_date = datetime.strptime(str(self.date_deces), "%Y-%m-%d")
                jour = str(ma_date.day)
                num_jour = str(ma_date.weekday())
                mois = str(ma_date.month)
                annee = str(ma_date.year)
                a = str(annee[0])
                b = str(annee[1])
                c = str(annee[2])
                d = str(annee[3])
                e = str(c+d)
                self.date_deces_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
                      
    

    @api.one
    @api.depends('heure_deces','minute_deces')
    def get_heure_letter(self):
        if self.heure_deces or self.minute_deces:
            hr = {'1': 'une','2': 'deux','3': 'trois', '4': 'quatre', '5': 'cinq','6': 'six','7': 'sept',
                  '8':'huit','9':'neuf','10':'dix','11':'onze','12':'douze','13':'treize','14':'quatorze',
                  '15':'quinze','16':'seize','17':'dix-sept','18':'dix-huit','19':'dix-neuf','20':'vingt',
                  '21':'vingt et une','22':'vingt-deux','23':'vingt-trois','24':'vingt-quatre'}
            mn = {'0': 'zéro','1': 'une','2': 'deux','3': 'trois', '4': 'quatre', '5': 'cinq','6': 'six','7': 'sept',
                  '8':'huit','9':'neuf','10':'dix','11':'onze','12':'douze','13':'treize','14':'quatorze',
                  '15':'quinze','16':'seize','17':'dix-sept','18':'dix-huit','19':'dix-neuf','20':'vingt',
                  '21':'vingt et une','22':'vingt-deux','23':'vingt-trois','24':'vingt-quatre','25':'vingt-cinq',
                  '26':'vingt-six','27':'vingt-sept','28':'vingt-huit','29':'vingt-neuf','30':'trente',
                  '31':'trente et une','32':'trente deux','32':'trente deux','33':'trente trois','34':'trente quatre',
                  '35':'trente cinq','36':'trente six','37':'trente sept','38':'trente huit','39':'trente neuf',
                  '40':'quarante','41':'quarante et une','42':'quarante deux','43':'quarante trois','44':'quarante quatre',
                  '45':'quarante cinq','46':'quarante six','47':'quarante sept','48':'quarante huit','49':'quarante neuf',
                  '50':'cinquante','51':'cinquante et une','52':'cinquante deux','53':'cinquante trois','54':'cinquante quatre',
                  '55':'cinquante cinq','56':'cinquante six','57':'cinquante sept','58':'cinquante huit','59':'cinquante neuf'}
         
            h = str(self.heure_deces)
            m = str(self.minute_deces)
            if self.heure_deces > 1:
                heure = ' heures '
            else:
                heure = ' heure '
            if self.minute_deces > 1: 
                minute = ' minutes '
            else:
                minute = ' minute '        
            self.heure_str = hr[h] + heure + mn[m] + minute
          
        