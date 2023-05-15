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


class DemandeActe(models.Model):
    _name = "demande.acte"
    #_inherit = ['etat.civil.naissance']
    _description = "Demande Acte Civil"
    _order = "date_ajout desc"
    
    
    def _get_default_user_id(self):
        return self.env.uid
    
    @api.multi
    def _get_default_code(self):
        if self.code == False or "/":
            seq = self.env['ir.sequence'].next_by_code('code.demande')
        return seq
    
    
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'CI')], limit=1)
        return country
    
    
    code = fields.Char(string="Code de la demande", default=_get_default_code , track_visibility="always")
    name = fields.Char(string="Nom", track_visibility="always")
    user_id = fields.Many2one("res.users", string="Agent", default=_get_default_user_id)
    date_ajout = fields.Datetime("Date de la demande", default=lambda self: fields.datetime.now())
    date_ajout_compare = fields.Date("Date ajout Copare", default=lambda self: fields.date.today())
    nom_demandeur = fields.Char(string="Nom", track_visibility="always")
    prenom_demandeur = fields.Char(string="Prénoms", track_visibility="always")
    numero_piece = fields.Char(string="Numéro piece", track_visibility="always")
    telephone = fields.Char(string="Téléphone", track_visibility="always")
    nombre_copie = fields.Integer(string="Nombre de copie",default="1", track_visibility="always")
    type_acte = fields.Selection([
                            ("an","Acte de naissance"),
                            ("cian","Copie intégrale d'acte de naissance"),
                            ("am","Acte de mariage"),
                            ("ciam","copie intégrale d'acte de mariage"),
                            ("ad","Acte de décès"),
                            ("ciad","copie intégrale d'acte de deces"),
                            ("cv","Certificat de vie"),
                            ("cve","Certificat de vie et entretien"),
                            ("cn","Certificatde non remariage, de non divorce et de non separation de corps")] , string='Type Acte')
    state = fields.Selection(string="Etat", selection=[
                            ('draft', 'Brouillon'),
                            ('confirm', 'Confirmé'),
                            ('approved', 'Approuvé'),
                            ('valid', 'Validé'),
                            ('cancel', 'Annulé/Rejeté')
                            ], track_visibility='always', default='draft')
    date_confirm = fields.Date(string="Date de confirmation", track_visibility="always")
    date_approved = fields.Date(string="Date d'approbation", track_visibility="always")
    date_valid = fields.Date(string="Date de validation", track_visibility="always")
    #etat_civil_naissance_id = fields.Char(string="an")
    etat_civil_naissance_id = fields.Many2one('etat.civil.naissance', string="N° extrait")
    etat_civil_mariage_id = fields.Many2one('etat.civil.mariage', string="N° extrait")
    etat_civil_deces_id = fields.Many2one('etat.civil.deces', string="N° extrait")
    code_registre = fields.Char(string="Code extrait")
    nom = fields.Char(string="Nom")
    prenom = fields.Char(string="Prénoms")
    birthday_cv = fields.Date(string="Date de naissance")
    date_deces = fields.Date(string="Date de décès")
    lieu_deces = fields.Char(string="Lieu de décès")
    lieu_naissance = fields.Char(string="Lieu de naissance")
    sexe = fields.Selection(string="Sexe", selection=[
                            ('masculin', 'Masculin'),
                            ('feminin', 'Feminin')
                            ], track_visibility='always', default='masculin')
    nom_femme = fields.Char(string="Nom de la mariée")
    prenom_femme = fields.Char(string="prénoms de la mariée")
    nom_homme = fields.Char(string="Nom du marié")
    prenom_homme = fields.Char(string="prénoms du marié")
    date_mariage = fields.Date(string="Date du mariage")
    country_id = fields.Many2one('res.country' ,string="Pays demandeur", default=_get_default_country)
    domicile = fields.Char(string="Domicilié a", track_visibility="always")
    nom_pere_certificat_vie = fields.Char(string="Nom entier père", track_visibility="always")
    nom_mere_certificat_vie = fields.Char(string="Nom entier mère", track_visibility="always")
    profession_demandeur_certificat_vie = fields.Char(string="Profession", track_visibility="always")
    numero_matricule_cgrae = fields.Char(string="Matricule CGRAE/CNPS")
    nom_temoin_premier = fields.Char(string="Nom temoin 1", track_visibility="always")
    prenom_temoin_premier = fields.Char(string="Prénoms temoin 1", track_visibility="always")
    nom_temoin_deuxieme = fields.Char(string="Nom temoin 2", track_visibility="always")
    prenom_temoin_deuxieme = fields.Char(string="Prénoms temoin 2", track_visibility="always")
    #nom_prenom_enfant = fields.Char(string="Nom entier de l'enfant ", track_visibility="always")
    #demande_acte_enfant_id = fields.Many2one('demande.acte.enfant', string="")
    enfant_ids = fields.One2many('demande.acte.enfant', 'demande_acte_id', string="")
    ref_demande_ponctuelle = fields.Char(string="Ref dmde ponctuelle", track_visibility="always")
    birthday_cv_str = fields.Text(string="En lettre" ,compute='get_date_letter_cv')
    maire_id = fields.Many2one("etat.civil.maire", string="Signé par")
    date_jour = fields.Date("", default=lambda self: fields.date.today())
    date_jour_lettre_str = fields.Text("Date demande", compute='get_date_letter')
    date_jour_str = fields.Text("Date demande", compute='get_date_jour')
    heure_jour_str = fields.Text("", compute='get_heure_jour')
    active = fields.Boolean('Active', default=True)
    

    
    @api.onchange('type_acte','etat_civil_naissance_id','etat_civil_mariage_id','etat_civil_deces_id')
    def onchange_etat_civil(self):
        if self.type_acte:
            if self.type_acte in ["an","ad","am","cian","ciam","ciad","cv","cve","cn"]:
                if self.type_acte in ["an","cian"]:
                    if self.etat_civil_naissance_id: # si le numero est existe
                        self.name = self.code
                        self.nom = self.etat_civil_naissance_id.nom
                        self.prenom = self.etat_civil_naissance_id.prenom
                        self.birthday_cv = self.etat_civil_naissance_id.birthday
                        self.lieu_naissance = self.etat_civil_naissance_id.lieu_naissance
                        self.sexe = self.etat_civil_naissance_id.sexe
                        self.code_registre = self.etat_civil_naissance_id.code
                elif self.type_acte in ["am","ciam"]:
                    if self.etat_civil_mariage_id:
                        self.name = self.code
                        self.nom_homme = self.etat_civil_mariage_id.nom_homme
                        self.prenom_homme = self.etat_civil_mariage_id.prenom_homme
                        self.nom_femme = self.etat_civil_mariage_id.nom_femme
                        self.prenom_femme = self.etat_civil_mariage_id.prenom_femme
                        self.date_mariage = self.etat_civil_mariage_id.date_mariage
                        self.code_registre = self.etat_civil_mariage_id.code
                elif self.type_acte in ["ad","ciad"]:
                    if self.etat_civil_deces_id:
                        self.name = self.code
                        self.nom = self.etat_civil_deces_id.nom
                        self.prenom = self.etat_civil_deces_id.prenom
                        self.birthday_cv = self.etat_civil_deces_id.birthday
                        self.lieu_naissance = self.etat_civil_deces_id.lieu_naissance
                        self.sexe = self.etat_civil_deces_id.sexe
                        self.date_deces = self.etat_civil_deces_id.date_deces
                        self.lieu_deces = self.etat_civil_deces_id.lieu_deces
                        self.code_registre = self.etat_civil_deces_id.code
                if self.type_acte in ["cv","cve","cn"]:
                    self.name = self.code
                    ref = self.env['ir.sequence'].next_by_code('demande.ponctuelle')
                    self.ref_demande_ponctuelle = ref + "/C-SPED/SG/DECAG"
                    if self.type_acte in ["cv"]:
                        self.code_registre = self.ref_demande_ponctuelle + "/CERTIF DE VIE"
                    elif self.type_acte in ["cve"]:
                        self.code_registre = self.ref_demande_ponctuelle + "/CERTIF DE VIE ET ENT"
                    elif self.type_acte in ["cn"]:
                        self.code_registre = self.ref_demande_ponctuelle + "/CERTIF DE NON"
            else:
                raise UserError(_("Recherche non conforme !"))
        return {}

    
    # fonction pour les etats
    @api.multi
    def button_draft(self, force=False):
        self.write({'state': 'draft'})
        
    @api.multi
    def button_confirm(self, force=False):
        
        self.write({'state': 'confirm', 'date_confirm': fields.Date.context_today(self)})
            
    @api.multi
    def button_approved(self, force=False):
        self.write({'state': 'approved', 'date_approved': fields.Date.context_today(self)})
        
    #ce code permet de créer une ligne de de caisse par demande
    
    @api.multi
    def button_valid(self, force=False):
        amount=0.0
        unit_price=500.0
        if self.code:
            # Cette ligne permet de vérifier si l'agent a deja faire une demande ce jour
            caisse_ids=self.env['demande.acte.caisse'].search([('date_jour','=',fields.Date.context_today(self)),('user_id','=',self.user_id.id)])
            #raise UserError(_('%s') % (self.req_ticket_html()))
            amount = self.nombre_copie*unit_price
            type_acte =""
            if self.type_acte == "an" :
                type_acte = "Acte de naissance"
            elif self.type_acte == "am":
                type_acte = "Acte de mariage"
            elif self.type_acte == "ad":
                type_acte = "Acte de décès"
            elif self.type_acte == "cian":
                type_acte = "Copie intégrale d'acte de naissance"
            elif self.type_acte == "ciam":
                type_acte= "Copie intégrale d'acte de mariage"
            elif self.type_acte == "ciad":
                type_acte = "Copie intégrale d'acte de décès"
            elif self.type_acte == "cv":
                type_acte = "Certificat de vie"
            elif self.type_acte == "cve":
                type_acte = "Certificat de vie et entretien"
            elif self.type_acte == "cn":
                type_acte = "Certificatde non remariage, de non divorce et de non separation de corps"
            if len(caisse_ids) == 0:
                # Creer une caisse 
                caisse = self.env['demande.acte.caisse'].create({
                    'code':self.env['ir.sequence'].next_by_code('demande.acte.caisse'),
                    'user_id':self.user_id.id,
                    'date_ajout':self.date_ajout,
                    'date_jour':fields.Date.context_today(self),
                    'quantity':self.nombre_copie,
                    'amount':amount,
                    })
                # Creer une ligne de caisse
                caisse_line=self.env['demande.acte.caisse.line'].create({
                    'code':self.env['ir.sequence'].next_by_code('demande.acte.caisse.line'),
                    'user_id':self.user_id.id,
                    'date_ajout':self.date_ajout,
                    'quantity':self.nombre_copie,
                    'type_acte':type_acte,
                    'unit_price':unit_price,
                    'amount':amount,
                    'demande_acte_caisse_id':caisse.id,
                    })
                self.write({'state': 'valid', 'date_valid': fields.Date.context_today(self)})
            elif len(caisse_ids) == 1:
                # Incrementer le montant et le nombre de demande
                self.env['demande.acte.caisse'].browse([caisse_ids.id]).write({
                    'amount':caisse_ids.amount + amount,
                    'quantity':caisse_ids.quantity + self.nombre_copie,
                    })
                # #Creation d'une autre ligne de caisse
                caisse_line = self.env['demande.acte.caisse.line'].create({
                    'code':self.env['ir.sequence'].next_by_code('demande.acte.caisse.line'),
                    'user_id':self.user_id.id,
                    'date_ajout':self.date_ajout,
                    'quantity':self.nombre_copie,
                    'type_acte':type_acte,
                    'unit_price':unit_price,
                    'amount':amount,
                    'demande_acte_caisse_id':caisse_ids.id,
                    })
                self.write({'state': 'valid', 'date_valid': fields.Date.context_today(self)})
            else:
                raise UserError(_("Impossible de continuer, vous avez déja une ligne de caisse pour aujourd'dhui"))
        return {}

    #===========================================================================
    # @api.multi
    # def button_valid(self, force=False):
    #     self.write({'state': 'valid', 'date_valid': fields.Date.context_today(self)})
    #===========================================================================

    @api.multi
    def button_cancel(self, force=False):
        self.write({'state': 'cancel'})
        
    
    @api.one
    @api.depends('date_jour')
    def get_date_jour(self):
        if self.date_jour:
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
            
            ma_date = datetime.strptime(str(self.date_jour), "%Y-%m-%d")
            #raise UserError(_("%s") % (ma_date))
            jour = str(ma_date.day)
            #raise UserError(_("%s") % (jour))
            num_jour = str(ma_date.weekday())
            #raise UserError(_("%s") % (num_jour))
            mois = str(ma_date.month)
            annee = str(ma_date.year)
            self.date_jour_str = num_jour +' '+ nm[mois] +' '+ annee
            
    @api.one
    @api.depends('date_jour')
    def get_date_letter(self):
        if self.date_jour:
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
            
            
            ma_date = datetime.strptime(str(self.date_jour), "%Y-%m-%d")
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
            
            self.date_jour_lettre_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]
            
            
    @api.one
    @api.depends('date_jour')
    def get_date_letter_cv(self):
        if self.birthday_cv:
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
            
            
            ma_date = datetime.strptime(str(self.birthday_cv), "%Y-%m-%d")
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
            
            self.birthday_cv_str = nj[num_jour] +' '+ njj[jour] +' '+ nm[mois] +' '+ nba[a]+' '+ nbb[b]+' '+ nbe[e]    
            
    
    
   
    
    @api.one
    @api.depends('date_ajout')
    def get_heure_jour(self):
        if self.date_ajout :
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
             
            heure = str(self.date_ajout.hour)
            minute = str(self.date_ajout.minute)
            if int(heure) > 1:
                h=" heures "
            else:
                h=" heure "
            if int(minute) > 1:
                m=" minutes "
            else:
                m=" minute "
            #raise UserError(_("%s") % (minute))
            self.heure_jour_str =  hr[heure] + h + mn[minute] + m
    
            
            
    
    @api.onchange('nom','nom_homme','nom_femme','nom_temoin_premier','nom_temoin_deuxieme','nom_demandeur')
    def set_upper(self):
        if self.nom:
            self.nom = str(self.nom).upper()
        if self.nom_demandeur:
            self.nom_demandeur = str(self.nom_demandeur).upper()
        if self.nom_homme:
            self.nom_homme = str(self.nom_homme).upper()
        if self.nom_femme:
            self.nom_femme = str(self.nom_femme).upper()
        if self.nom_temoin_premier:
            self.nom_temoin_premier = str(self.nom_temoin_premier).upper()
        if self.nom_temoin_deuxieme:     
            self.nom_temoin_deuxieme = str(self.nom_temoin_deuxieme).upper()                        
        return
    
    
    @api.onchange('prenom','prenom_homme','prenom_femme','nom_pere_certificat_vie','nom_mere_certificat_vie','prenom_temoin_premier','prenom_temoin_deuxieme','prenom_demandeur')
    def caps_name(self):
        if self.prenom:
            self.prenom = str(self.prenom).title()
        if self.prenom_demandeur:
            self.prenom_demandeur = str(self.prenom_demandeur).title()
        if self.prenom_homme:
            self.prenom_homme = str(self.prenom_homme).title()
        if self.prenom_femme:
            self.prenom_femme = str(self.prenom_femme).title()
        if self.nom_pere_certificat_vie:
            self.nom_pere_certificat_vie = str(self.nom_pere_certificat_vie).title()
        if self.nom_mere_certificat_vie:
            self.nom_mere_certificat_vie = str(self.nom_mere_certificat_vie).title()
        if self.prenom_temoin_premier:
            self.prenom_temoin_premier = str(self.prenom_temoin_premier).title()
        if self.prenom_temoin_deuxieme:     
            self.prenom_temoin_deuxieme = str(self.prenom_temoin_deuxieme).title() 
        return