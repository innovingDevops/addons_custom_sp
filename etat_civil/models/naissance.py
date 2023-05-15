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


class EtatCivilNaissance(models.Model):
    _name = "etat.civil.naissance"
    #_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Etat Civil Naissance"
    _order = "date_ajout desc"
    
    def _get_default_user_id(self):
        return self.env.uid

    def _creat_year(self):
        created_year = datetime.today().year
        return created_year
    
    
    def _creat_month(self):
        created_month = datetime.today().month
        return created_month
    
    ref_registre = fields.Char(string="Numéro", track_visibility="always")
    date_registre = fields.Date("Du", track_visibility="always")
    surfixe = fields.Char(string="Surfixe", track_visibility="always", default="CSP/EC")
    numero_acte = fields.Char(string="Acte N°", track_visibility="always")
    code = fields.Char(string="Code", track_visibility="always")
    name = fields.Char(string="N° registre", track_visibility="always")
    nom = fields.Char(string="Nom", track_visibility="always")
    prenom = fields.Char(string="Prénoms", track_visibility="always")
    birthday = fields.Date("Date de naissance", track_visibility="always")
    birthday_str = fields.Text(string='En lettre', compute='get_date_letter')
    lieu_naissance = fields.Char(string="Lieu de naissance", track_visibility="always")
    commune_naissance_enfant = fields.Char(string="Commune", track_visibility="always")
    sous_prefecture_naissance_enfant = fields.Char(string="Sous prefecture", track_visibility="always")
    sexe = fields.Selection(string="Sexe", selection=[
        ("masculin", "Masculin"),
        ("feminin", "Feminin")
        ], track_visibility="always", default="masculin")
    heure_naissance = fields.Integer(string='Heure', default=1)
    #minute_naissance = fields.Char(string='Minute')
    minute_naissance = fields.Integer(string='Minute')
    heure_str = fields.Text(string='Heure en lettre', compute='get_heure_letter')
    user_id = fields.Many2one("res.users", string="Agent", default=_get_default_user_id)
    maire_id = fields.Many2one("etat.civil.maire", string="Maire")
    date_ajout = fields.Datetime("Date ajout", default=lambda self: fields.datetime.now())
    date_ajout_compare = fields.Date("Date ajout Copare", default=lambda self: fields.date.today())
    state = fields.Selection(string="Etat", selection=[
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('approuved' , 'Approuvé'),
        ('valid', 'Validé'),
        ('done' , 'Terminé'),
        ('cancel', 'Annulé/Rejeté')
        ], track_visibility='always', default='draft')
    document = fields.Many2many('etat.civil.document','etat_civil_document_rel','etat_civil_naissance_id','etat_civil_document_id', string="Type")
    nom_pere = fields.Char(string="Nom ", track_visibility="always")
    prenom_pere = fields.Char(string="Prénoms ", track_visibility="always")
    birthday_pere = fields.Date(string="Date de Naissance ", track_visibility="always")
    sous_prefecture_pere = fields.Char(string="Sous-prefecture de", track_visibility="always")
    commune_naissance_pere = fields.Char(string="Commune de", track_visibility="always")
    lieu_naissance_pere = fields.Char(string="Lieu de naissance ", track_visibility="always")
    residence_pere = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_pere = fields.Char(string="Profession ", track_visibility="always")
    nom_mere = fields.Char(string="Nom ", track_visibility="always")
    prenom_mere = fields.Char(string="Prénoms ", track_visibility="always")
    birthday_mere = fields.Date(string="Date de Naissance ", track_visibility="always")
    lieu_naissance_mere = fields.Char(string="Lieu de naissance ", track_visibility="always")
    residence_mere = fields.Char(string="Domicilié a ", track_visibility="always")
    profession_mere = fields.Char(string="Profession ", track_visibility="always")
    sous_prefecture_mere = fields.Char(string="Sous-prefecture", track_visibility="always")
    commune_naissance_mere = fields.Char(string="Commune de", track_visibility="always")
    certificat_naissance= fields.Binary(string="Certificat de naissance")
    cni_pere= fields.Binary(string="CNI du père")
    cni_mere= fields.Binary(string="CNI de la mère")
    date_confirm = fields.Date(string="Date de confirmation", track_visibility="always")
    date_approved = fields.Date(string="Date d'approbation", track_visibility="always")
    date_valid = fields.Date(string="Date de validation", track_visibility="always")
    date_done = fields.Date(string="Date clôture", track_visibility="always")
    birthday_pere_str = fields.Text(string='En lettre', compute='get_date_letter_pere')
    birthday_mere_str = fields.Text(string='En lettre', compute='get_date_letter_mere')
    situation_matrimoniale = fields.Selection(string="Stuation matrimonial", selection=[
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce' , 'Divorcé'),
        ], track_visibility='always', default='celibataire')
    date_mariage = fields.Date(string="Date du mariage", track_visibility="always")
    date_mariage_str = fields.Text(string='En lettre', compute='get_date_letter_mariage')
    conjoint = fields.Char(string="Nom du conjoint", track_visibility="always")
    date_divorce = fields.Date(string="Date divorce", track_visibility="always")
    date_divorce_str = fields.Text(string='En lettre', compute='get_date_letter_divorce')
    decede = fields.Selection(string="Décédé", selection=[
        ('oui', 'Oui'),
        ('non', 'Non'),
        ], track_visibility='always', default='non')
    date_deces = fields.Date(string="Date déces", track_visibility="always")
    date_deces_str = fields.Text(string='En lettre', compute='get_date_letter_deces')
    #demande_acte_ids = fields.One2many('demande.acte','etat_civil_naissance_id', string="Les demandes d'acte de naissance")
    
    nom_demandeur = fields.Char(string="Nom", track_visibility="always")
    prenom_demandeur = fields.Char(string="Prénoms", track_visibility="always")
    date_naissance = fields.Date(string="Date de Naissance", track_visibility="always")
    birthday_demandeur_str = fields.Text(string='En lettre', compute='get_date_letter_demandeur')
    lieu_naissance_demandeur = fields.Char(string="lieu de naissance", track_visibility="always")
    domicile = fields.Char(string="Domicilié a ", track_visibility="always")
    profession = fields.Char(string="Profession ", track_visibility="always")
    duree_declaration = fields.Integer(string="Durée", compute='difference_date', store=True)
    verification_minute = fields.Integer(string="Durée")
    active = fields.Boolean('Active', default=True)
    
    
    
    @api.onchange('ref_registre','date_registre')
    def onchange_numero_registre(self):
        if self.ref_registre:
            if self.date_registre:
                name = self.ref_registre + " du " + str(self.date_registre.strftime("%d/%m/%Y")) + " " + self.surfixe
                self.name = name
                self.code = name + "/NAISSANCE" 
                #raise UserError(_("%s") % (self.code))
        return {}
    
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
            
            
            ma_date = datetime.strptime(str(self.birthday), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.birthday_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]

            
    @api.one
    @api.depends('birthday_pere')
    def get_date_letter_pere(self):
        if self.birthday_pere:
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
            
            
            ma_date = datetime.strptime(str(self.birthday_pere), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.birthday_pere_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            
    @api.one
    @api.depends('birthday_mere')
    def get_date_letter_mere(self):
        if self.birthday_mere:
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
            
            
            ma_date = datetime.strptime(str(self.birthday_mere), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.birthday_mere_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            
    
    @api.one
    @api.depends('date_mariage')
    def get_date_letter_mariage(self):
        if self.date_mariage:
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
            
            
            ma_date = datetime.strptime(str(self.date_mariage), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.date_mariage_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            
            
    @api.one
    @api.depends('date_divorce')
    def get_date_letter_divorce(self):
        if self.date_divorce:
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
            
            
            ma_date = datetime.strptime(str(self.date_divorce), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.birthday_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]            
            
    @api.one
    @api.depends('date_deces')
    def get_date_letter_deces(self):
        if self.date_deces:
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
            
            
            ma_date = datetime.strptime(str(self.date_deces), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.date_deces_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
    
    
    @api.one
    @api.depends('date_naissance')
    def get_date_letter_demandeur(self):
        if self.date_naissance:
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
            
            
            ma_date = datetime.strptime(str(self.date_naissance), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            a = str(annee[0])
            b = str(annee[1])
            c = str(annee[2])
            d = str(annee[3])
            e = str(c+d)
            
            self.birthday_demandeur_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            
            
   

            
        
    @api.one
    @api.depends('heure_naissance','minute_naissance')
    def get_heure_letter(self):
        if self.heure_naissance or self.minute_naissance:
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
         
            h = str(self.heure_naissance)
            m = str(self.minute_naissance)
            
            
            if self.heure_naissance > 1:
                heure = ' heures '
            else:
                heure = ' heure '
            if self.minute_naissance > 1: 
                minute = ' minutes '
            else:
                minute = ' minute '  
            self.heure_str = hr[h] + heure + mn[m] + minute
                
    @api.multi
    def button_draft(self, force=False):
        self.write({'state': 'draft'})
        
    @api.multi
    def button_confirm(self, force=False):
        fmt = '%Y-%m-%d'
        #=======================================================================
        # birthday_pere = self.birthday_pere
        # birthday_mere = self.birthday_mere
        # birthday = self.birthday
        # date_ajout = self.date_ajout
        #=======================================================================
        d1 = datetime.strptime(str(self.birthday), fmt)
        d2 = datetime.strptime(str(self.date_ajout_compare), fmt)
        d3 = datetime.strptime(str(self.birthday_pere), fmt)
        d4 = datetime.strptime(str(self.birthday_mere), fmt)
        if d2 > d1:
            result=(d2 - d1).days
            if result <= 90 :
                self.duree_declaration = (d2 - d1).days
                self.write({'state': 'confirm', 'date_confirm': fields.Date.context_today(self)})
            else:
                raise ValidationError('Cette déclaration de naissance doit suivre le processus de déclaration par audience foraine .')
        else:
            raise ValidationError('La date de naissance ne doit pas être supérieure à la date de déclaration.')
        
        if d3 > d1 or d4 > d1 :
            raise ValidationError("La date de naissance de l'enfant ne doit pas être supérieure à celle des parents.")
        if d3 > d2 or d4 > d2 :
            raise ValidationError('La date de naissance des parents doit être supérieure à celle de la déclaration.')
        
        if self.heure_naissance < 1 or self.minute_naissance < 0 :
            raise ValidationError("Heure ou minute definie incorrecte.")
        
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
    
   
    #===========================================================================
    # @api.onchange('birthday','date_ajout')
    # def difference_date(self):
    #     fmt = '%Y-%m-%d'
    #     birthday = self.birthday
    #     date_ajout = self.date_ajout
    #     d1 = datetime.strptime(str(self.birthday), fmt)
    #     d2 = datetime.strptime(str(self.date_ajout), fmt)
    #     if d2 > d1:
    #         result=(d2 - d1).days
    #         if result <= 90 :
    #             self.duree_declaration = (d2 - d1).days
    #         else:
    #             raise ValidationError('Cette déclaration de naissance doit suivre le processus de déclaration par audience foraine .')
    #     else:
    #         raise ValidationError('La date de début ne doit pas être supérieure à la date de fin.')
    #     
