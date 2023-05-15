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


class EtatCivilMariage(models.Model):
    _name = "etat.civil.mariage"
    #_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Etat Civil Mariage"
    _order = "date_ajout desc"
    
    def _get_default_user_id(self):
        return self.env.uid

    
    ref_registre = fields.Char(string="Numéro", track_visibility="always")
    date_registre = fields.Date("Du", track_visibility="always")
    surfixe = fields.Char(string="Surfixe", track_visibility="always", default="CSP/EC")
    name = fields.Char(string="N° registre", track_visibility="always")
    numero_acte = fields.Char(string="Acte N°", track_visibility="always")
    code = fields.Char(string="Code", track_visibility="always")
    user_id = fields.Many2one("res.users", string="Agent", default=_get_default_user_id)
    date_ajout = fields.Datetime("Date ajout", default=lambda self: fields.datetime.now())
    date_ajout_compare = fields.Date("Date ajout Copare", default=lambda self: fields.date.today())
    date_mariage = fields.Date("Date du mariage")
    numero_registre = fields.Char(string=" N° du registre", track_visibility="always")
    lieu_mariage = fields.Char(string="Lieu du mariage", track_visibility="always")
    nom_homme = fields.Char(string="Nom", track_visibility="always")
    prenom_homme = fields.Char(string="Prénoms ", track_visibility="always")
    birthday_homme = fields.Date(string="Date de Naissance ", track_visibility="always")
    birthday_homme_str = fields.Text(string='En lettre', compute='get_date_letter')
    lieu_naissance_homme = fields.Char(string="Lieu de naissance ", track_visibility="always")
    commune_naissance_homme = fields.Char(string="Commune ", track_visibility="always")
    sous_prefecture_naissance_homme = fields.Char(string="Sous préfecture ", track_visibility="always")
    profession_homme = fields.Char(string="Profession ", track_visibility="always")
    nom_femme = fields.Char(string="Nom ", track_visibility="always")
    prenom_femme = fields.Char(string="Prénoms ", track_visibility="always")
    birthday_femme = fields.Date(string="Date de Naissance ", track_visibility="always")
    birthday_femme_str = fields.Text(string='En lettre', compute='get_date_letter')
    lieu_naissance_femme = fields.Char(string="Lieu de naissance ", track_visibility="always")
    commune_naissance_femme = fields.Char(string="Commune ", track_visibility="always")
    sous_prefecture_naissance_femme = fields.Char(string="Sous préfecture ", track_visibility="always")
    photo_mari = fields.Binary(string="Photo du mari ", track_visibility="always")
    photo_mariee = fields.Binary(string="Photo de la mariée ", track_visibility="always")
    profession_femme = fields.Char(string="Profession ", track_visibility="always")
    nom_pere_homme = fields.Char(string="Nom ", track_visibility="always")
    prenom_pere_homme = fields.Char(string="Prénoms ", track_visibility="always")
    residence_pere_homme = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_pere_homme = fields.Char(string="Profession ", track_visibility="always")
    nom_mere_homme = fields.Char(string="Nom ", track_visibility="always")
    prenom_mere_homme = fields.Char(string="Prénoms ", track_visibility="always")
    residence_mere_homme = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_mere_homme = fields.Char(string="Profession ", track_visibility="always")
    nom_pere_femme = fields.Char(string="Nom ", track_visibility="always")
    prenom_pere_femme = fields.Char(string="Prénoms ", track_visibility="always")
    residence_pere_femme = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_pere_femme = fields.Char(string="Profession ", track_visibility="always")
    nom_mere_femme = fields.Char(string="Nom ", track_visibility="always")
    prenom_mere_femme = fields.Char(string="Prénoms ", track_visibility="always")
    residence_mere_femme = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_mere_femme = fields.Char(string="Profession ", track_visibility="always")
    nom_temoin_homme = fields.Char(string="Nom ", track_visibility="always")
    prenom_temoin_homme = fields.Char(string="Prénoms ", track_visibility="always")
    residence_temoin_homme = fields.Char(string="Domicilié à ", track_visibility="always")
    profession_temoin_homme = fields.Char(string="Profession ", track_visibility="always")
    age_temoin_homme = fields.Integer(string="Age ", track_visibility="always")
    age_temoin_homme_str = fields.Text(string="En lettre",compute='get_date_letter', track_visibility="always")
    nom_temoin_femme = fields.Char(string="Nom ", track_visibility="always")
    prenom_temoin_femme = fields.Char(string="Prénoms ", track_visibility="always")
    residence_temoin_femme = fields.Char(string="Domicilié à", track_visibility="always")
    profession_temoin_femme = fields.Char(string="Profession ", track_visibility="always")
    age_temoin_femme = fields.Integer(string="Age ", track_visibility="always")
    age_temoin_femme_str = fields.Text(string="En lettre ", compute='get_date_letter', track_visibility="always")
    heure_mariage = fields.Integer(string='Heure de mariage')
    state = fields.Selection(string="Etat", selection=[
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('approuved' , 'Approuvé'),
        ('valid', 'Validé'),
        ('done' , 'Terminé'),
        ('cancel', 'Annulé/Rejeté')
        ], track_visibility='always', default='draft')
    type_personne_homme = fields.Selection(string="type de personne", selection=[
        ('civile', 'Civile'),
        ('corps habille', 'Corps habillé'),
        ('etranger' , 'Etrangé')
        ], track_visibility='always', default='civile')
    type_personne_femme = fields.Selection(string="type de personne", selection=[
        ('civile', 'Civile'),
        ('corps habille', 'Corps habillé'),
        ('etranger' , 'Etrangé')
        ], track_visibility='always', default='civile')
    date_confirm = fields.Date(string="Date de confirmation", track_visibility="always")
    date_approved = fields.Date(string="Date d'approbation", track_visibility="always")
    date_valid = fields.Date(string="Date de validation", track_visibility="always")
    date_done = fields.Date(string="Date clôture", track_visibility="always")
    date_mariage_str = fields.Text("Date en lettre", compute='get_date_letter')
    minute_mariage = fields.Integer(string='Minute')
    heure_str = fields.Text(string='Heure en lettre', compute='get_heure_letter')
    document = fields.Many2many('etat.civil.document','etat_civil_document_mariage_rel','etat_civil_mariage_id','etat_civil_document_id', string="Type")
    cni_homme = fields.Binary(string="CNI de l'homme")
    cni_femme= fields.Binary(string="CNI de la femme")
    cni_temoin_homme= fields.Binary(string="CNI témoin du marié")
    cni_temoin_femme= fields.Binary(string="CNI témoin de la mariée")
    certificat_residence_homme= fields.Binary(string="Certificat de residence homme")
    certificat_residence_femme= fields.Binary(string="Certificat de residence femme")
    extrait_homme= fields.Binary(string="Extrait homme")
    extrait_femme= fields.Binary(string="Extrait femme")
    certificat_presence_homme= fields.Binary(string="Certificat de présence au corps homme")
    certificat_presence_femme = fields.Binary(string="Certificat de présence au corps femme")
    certificat_de_capacite_homme= fields.Binary(string="Certificat de capacité matrimoniale homme")
    certificat_de_capacite_femme = fields.Binary(string="Certificat de capacité matrimoniale femme")
    maire_id = fields.Many2one("etat.civil.maire", string="Maire")
    active = fields.Boolean('Active', default=True)
    
    @api.multi
    def button_draft(self, force=False):
        self.write({'state': 'draft'})
        
    
    @api.multi
    def button_confirm(self, force=False):
        fmt = '%Y-%m-%d'
        #=======================================================================
        # date_mariage = self.date_mariage
        # date_ajout = self.date_ajout
        #=======================================================================
        d1 = datetime.strptime(str(self.date_mariage), fmt)
        d2 = datetime.strptime(str(self.date_ajout_compare), fmt)
        if d2 < d1:
            raise ValidationError('La date du mariage ne doit pas être supérieure à la date de déclaration.')
        else:
            self.write({'state': 'confirm', 'date_confirm': fields.Date.context_today(self)})
        
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
                self.code = name + "/MARIAGE" 
                #raise UserError(_("%s") % (self.name))
        return {}
    
    @api.one
    @api.depends('birthday_homme','birthday_femme','date_mariage','age_temoin_femme','age_temoin_homme')
    def get_date_letter(self):
        if self.birthday_homme or self.birthday_femme or self.date_mariage:
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
            
            
            #debut convertion de la date de naissance des temoins des mariés
            age_femme_lettre = str(self.age_temoin_femme)
            age_homme_lettre = str(self.age_temoin_homme)
            if self.age_temoin_femme or self.age_temoin_homme:
                self.age_temoin_femme_str = nbe[age_femme_lettre] +' ans '
                self.age_temoin_homme_str = nbe[age_homme_lettre] +' ans '
                
            #fin de la convertion
            
            
            if self.birthday_homme :
                ma_date = datetime.strptime(str(self.birthday_homme), "%Y-%m-%d")
                jour = str(ma_date.day)
                num_jour = str(ma_date.weekday())
                mois = str(ma_date.month)
                annee = str(ma_date.year)
                a = str(annee[0])
                b = str(annee[1])
                c = str(annee[2])
                d = str(annee[3])
                e = str(c+d)
                
                self.birthday_homme_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            if self.birthday_femme :
                ma_date = datetime.strptime(str(self.birthday_femme), "%Y-%m-%d")
                jour = str(ma_date.day)
                num_jour = str(ma_date.weekday())
                mois = str(ma_date.month)
                annee = str(ma_date.year)
                a = str(annee[0])
                b = str(annee[1])
                c = str(annee[2])
                d = str(annee[3])
                e = str(c+d)
                
                self.birthday_femme_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            if self.date_mariage :
                ma_date = datetime.strptime(str(self.date_mariage), "%Y-%m-%d")
                jour = str(ma_date.day)
                num_jour = str(ma_date.weekday())
                mois = str(ma_date.month)
                annee = str(ma_date.year)
                a = str(annee[0])
                b = str(annee[1])
                c = str(annee[2])
                d = str(annee[3])
                e = str(c+d)
                
                self.date_mariage_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
                
                
    @api.one
    @api.depends('heure_mariage','minute_mariage')
    def get_heure_letter(self):
        if self.heure_mariage or self.minute_mariage:
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
         
            h = str(self.heure_mariage)
            m = str(self.minute_mariage)
            if self.heure_mariage > 1:
                heure = ' heures '
            else:
                heure = ' heure '
            if self.minute_mariage > 1: 
                minute = ' minutes '
            else:
                minute = ' minute '        
            self.heure_str = hr[h] + heure + mn[m] + minute
    
    
    @api.onchange('nom_homme','nom_femme','nom_pere_homme','nom_mere_homme','nom_pere_femme','nom_mere_femme','nom_temoin_homme','nom_temoin_femme')
    def set_upper(self):
        if self.nom_homme:
            self.nom_homme = str(self.nom_homme).upper()
        if self.nom_femme:
            self.nom_femme = str(self.nom_femme).upper()
        if self.nom_pere_homme:
            self.nom_pere_homme = str(self.nom_pere_homme).upper()
        if self.nom_mere_homme:     
            self.nom_mere_homme = str(self.nom_mere_homme).upper()
        if self.nom_pere_femme:
            self.nom_pere_femme = str(self.nom_pere_femme).upper()
        if self.nom_mere_femme:     
            self.nom_mere_femme = str(self.nom_mere_femme).upper()
        if self.nom_temoin_homme:
            self.nom_temoin_homme = str(self.nom_temoin_homme).upper()
        if self.nom_temoin_femme:     
            self.nom_temoin_femme = str(self.nom_temoin_femme).upper()                        
        return
    
    
    @api.onchange('prenom_homme','prenom_femme','prenom_pere_homme','prenom_mere_homme','prenom_pere_femme','prenom_mere_femme','prenom_temoin_homme','prenom_temoin_femme')
    def caps_name(self):
        if self.prenom_homme:
            self.prenom_homme = str(self.prenom_homme).title()
        if self.prenom_femme:
            self.prenom_femme = str(self.prenom_femme).title()
        if self.prenom_pere_homme:
            self.prenom_pere_homme = str(self.prenom_pere_homme).title()
        if self.prenom_mere_homme:     
            self.prenom_mere_homme = str(self.prenom_mere_homme).title()
        if self.prenom_pere_femme:
            self.prenom_pere_femme = str(self.prenom_pere_femme).title()
        if self.prenom_mere_femme:     
            self.prenom_mere_femme = str(self.prenom_mere_femme).title()
        if self.prenom_temoin_homme:
            self.prenom_temoin_homme = str(self.prenom_temoin_homme).title()
        if self.prenom_temoin_femme:     
            self.prenom_temoin_femme = str(self.prenom_temoin_femme).title() 
        return
    