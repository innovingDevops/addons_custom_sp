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

from odoo.http import request
#from odoo.addons_custom.ehcs_qr_code_base.models.qr_code_base import generate_qr_code
from odoo.tools.amount_to_text_frr import amount_to_text_fr

from mock.mock import self
#from amount_to_text_frr import amount_to_text_fr

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}
class InnovingMandat(models.Model):
    _name = "innoving.mandat"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Innoving Mandats de Paiement"
    _order = "date_demande desc"
    
        
    def _get_default_user_id(self):
        return self.env.uid
    

    def _creat_year(self):
        created_year = datetime.today().year
        return created_year
    
    
    def _creat_month(self):
        created_month = datetime.today().month
        return created_month
         
    def amount_to_text_fr(self):
        res = []
        return res
    
    @api.model
    def _default_demandeur(self):
        user_id = self.env.uid
        return user_id
    
    @api.one
    @api.depends('montant_paye')
    def _amount_in_words(self):
        if self.montant_estime == 0.0:
            #raise UserError(_("%s") % (self.montant_lettre))
            self.montant_lettre = amount_to_text_fr(self.montant_paye,'Francs CFA')
        else:
            self.montant_lettre = amount_to_text_fr(self.montant_estime,'Francs CFA')
                    
           
    code = fields.Char(string='Code', default='Nouveau', track_visibility='always')
    name = fields.Char(string='Mandat de paiement N°', default='Nouveau', track_visibility='always')
    type_depense = fields.Selection(string="Type de dépense", selection=[
        ('fonctionnel', 'Dépense de Fonctionnement'),
        ('investissement', 'Dépense d\'Investissement')
        ], track_visibility='always', default='fonctionnel')
    type_fond = fields.Selection(string="Sur", selection=[
        ('Fond propre', 'Fond propre'),
        ('Aide Etat', 'Aide Etat')
        ], track_visibility='always', default='Fond propre')
    user_id = fields.Many2one('res.users', string='Agent', default=_get_default_user_id)
    creat_year = fields.Char(string="Année de création", default=_creat_year)
    creat_month = fields.Char(string="Mois de création", default=_creat_month)
    partner_id = fields.Many2one('res.partner', string='Fournisseur', track_visibility='always')
    #purchase_order_id = fields.Many2one('purchase.order', string='BC NÂ°', track_visibility='always')
    #account_invoice_id = fields.Many2one('account.invoice', string='Facture NÂ°', track_visibility='always')
    account_id = fields.Many2one('account.account','Compte')
    montant_lettre = fields.Text(string='En lettre', readonly=True, compute='_amount_in_words')
    montant_estime = fields.Float('Montant à  payer', compute='_compute_montant_estime', store=True)
    montant_reel = fields.Float('Montant à  payer')
    montant_reste = fields.Float('Reste à  payer', compute='_compute_montant_reste',store=True)
    montant_paye = fields.Float('Total Payé', compute='_compute_montant_paye',store=True)
    montant_a_payer = fields.Float('Total à  Payer')
    date_prevue = fields.Date('Date échéance', track_visibility='always')
    note = fields.Text('Objet de la demande')
    demandeur = fields.Many2one('res.users', 'Demandeur',default=_default_demandeur)
    validateur = fields.Many2one('res.users', 'Validateur')
    approbateur = fields.Many2one('res.users', 'Transmetteur')
    payeur = fields.Many2one('res.users', 'Payeur')
    date_demande = fields.Datetime('Date de demande', readonly=False, select=True
                                , default=lambda self: fields.datetime.now())
    date_validation = fields.Datetime('Date de validation')
    date_approbation = fields.Datetime('Date d\'approbation')
    invoice_ids = fields.Many2many('account.invoice','invoice_mandat_paiement_rel','mandat_id','invoice_id','Factures')
    purchase_order_ids = fields.Many2many('purchase.order','purchase_mandat_paiement_rel','purchase_order_id','purchase_id','Bon de commande')
    purchase_order_id = fields.Many2one('purchase.order',string='Numero BC')
    beneficiaire = fields.Char("A l'ordre de")
    journal_id = fields.Many2one('account.journal','Journal')
    account_id = fields.Many2one('account.account','Compte')
    line_ids = fields.One2many('innoving.mandat.line', 'mandat_id', string='Ligne de reglement', track_visibility='always')
    bon_commande = fields.Char('Bon de commande')
    selon_facture = fields.Char('Numero facture')
    #order_cancel_ids = fields.One2many('mandat.paiement.cancel', 'order_id', string='Historique des refus', track_visibility='always')
    state = fields.Selection([
        ('cancel', 'Annulé'),
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('valid', 'Validé'),
        ('approuv', 'Transmis'),
        ('partiel', 'Partiel'),
        ('regularisation', 'Regularisation'),
        ('paid', 'Payé / Régularisé')
        ], string='Etat', track_visibility='always', default='draft')
    type_reglement = fields.Selection([
        ('ESPECE', 'ESPECE'),
        ('CHEQUE', 'CHEQUE'),
        ('VIREMENT', 'VIREMENT'),
        ], string='Mode de reglement', track_visibility='always', default='CHEQUE')
    type_demande = fields.Selection([
        ('Facture', 'Facture'),
        ('Decision', 'Décision'),
        ], string='Mandat basé sur', track_visibility='always', default="Facture")
    selon_decision = fields.Char('Décision N°', track_visibility='always')
    decision_file = fields.Binary(string="Joindre la décision", track_visibility='always')
    type_demande_facture = fields.Selection([
        ('Normale', 'Normale'),
        ('Taxe', 'Avec taxe')
        ], string='Type Facture', track_visibility='always')
    tax_source = fields.Float("Prelevement à  la source")
    origin = fields.Char("Document d'origine")
    taxe_id = fields.Many2one('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    nature_mandat = fields.Char("Nature du mandat")
    verif_compta = fields.Char('Etat des payement en-cours', default='non')
    order_cancel_ids = fields.One2many('innoving.mandat.cancel', 'order_id', string='Historique des refus', track_visibility='always')
    is_carburant = fields.Boolean(string="Achat de carburant", default=False, track_visibility='always')
    budget_id = fields.Many2one('crossovered.budget','Budget')
    account_fonctionnel_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_fonctionnel_code = fields.Char(string='Code')
    account_analytic_id = fields.Many2one('account.analytic.account','Compte Analytique')
    account_patrimoine_id = fields.Many2one('account.account','Compte Fonctionnel')
    account_patrimoine_code = fields.Char(string='Code')
    account_patrimoine_analytic_id = fields.Many2one('account.analytic.account','Compte Analytique')
    account_patrimoniale_id = fields.Many2one('account.account','Compte Patrimoniale')
    account_patrimoniale_code = fields.Char(string='Code')
    barre_account_fonctionnel = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ], string='Barre fonctionnel', track_visibility='always')
    barre_account_patrimoine = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ], string='Barre patrimoine', track_visibility='always')
    numero_facture_origine = fields.Char(string='NÂ° Facture Origine', track_visibility='always')
    date_edition_fournisseur = fields.Date(string='Date du fournisseur', track_visibility='always')
    montant_alloue = fields.Float('Montant alloué')
    depense_anterieur = fields.Float('Dépense antérieur')
    depense_actuelle = fields.Float('Dépense actuelle')
    montant_disponible = fields.Float('Montant disponible')
    numero_ordre_mandat = fields.Char(string='NÂ° d\'ordre mandat', track_visibility='always')
    compte_id = fields.Many2one(string='Compte Bancaire')
    numero_compte_fournisseur = fields.Char(string='Numéro de compte')
    banque_name = fields.Char(string='Banque')
    agence = fields.Char(string='Agence')
    compte = fields.Char(string='Compte')
    chapitre = fields.Char(string='Chapitre')
    avis_municipalite = fields.Char(string='Avis de municipalité N°')
    numero_deliberation = fields.Char(string='Délibération N°')
    date_deliberation = fields.Date(string='Du', track_visibility='always')
    type_mandat = fields.Selection(string="Type de mandat", selection=[
        ('Normal', 'Normal'),
        ('Prelevement', 'Prelevement'),
        ('Ordre de recette', 'Ordre de recette')
        ], track_visibility='always')
    
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.beneficiaire=self.partner_id.name
            self.account_id=self.partner_id.property_account_payable_id.id
            return {}
        else:
            self.beneficiaire= False
            self.invoice_ids = False
            self.order_ids= False
            self.account_id= False
            return {}
        
        
    
    @api.onchange('account_fonctionnel_id')
    def _onchange_account_fonctionnel_id(self):
        if self.account_fonctionnel_id:
            self.account_fonctionnel_code=self.account_fonctionnel_id.code
            return {}
        
        
    @api.onchange('invoice_ids')
    def _onchange_invoice_ids(self):
        if len(self.invoice_ids) == 1:
            for line in self.invoice_ids:
                #self.note = line.note
                self.date_prevue = line.date_due
                self.selon_facture = line.reference
                self.bon_commande = line.origin
                #raise UserError(_("Merci %s") % (self.note))
                tax = 0.0
                for l in line.tax_line_ids:
                    if l.tax_id.tax_source == True:
                        tax += l.amount
                if abs(tax) > 0:
                    self.tax_source = abs(tax)
                    self.type_demande_facture = "Taxe"
            return {}
        else:
            #self.note = False
            self.date_prevu = False
            self.selon_facture = False
            self.bon_commande = False
            self.tax_source = False
            return {}
        
    @api.onchange('purchase_order_ids')
    def _onchange_purchase_order_ids(self):
        if len(self.purchase_order_ids) == 1:
            for line in self.purchase_order_ids:
                #self.note = line.note
                #self.date_prevue = line.date_planned
                self.bon_commande = line.name
                self.montant_a_payer = sum([l.amount_total for l in self.purchase_order_ids])
            return {}
        else:
            #self.note = False
            self.date_prevue = False
            self.bon_commande = False
            self.montant_a_payer = False
            return {}
        
        
    @api.depends('montant_paye','montant_a_payer','line_ids','note','selon_facture','date_prevue','state')
    def _compute_montant_estime(self):
        for order in self:
            montant_estime=0.0
            if order.type_demande == 'Facture' or order.type_demande == 'Decision':
                for line in order.invoice_ids:
                    montant_estime+=line.residual
            #===================================================================
            # if order.type_demande == 'Bc':
            #     montant_estime=order.montant_a_payer
            #     order.montant_estime = montant_estime or 0.0                    
            #===================================================================
            order.montant_estime = montant_estime or 0.0
            
            
    @api.depends('montant_paye','montant_a_payer','line_ids','invoice_ids.residual','invoice_ids.note','montant_reel','montant_paye')
    def _compute_montant_reste(self):
        montant_reste=0.0
        montant_paye1=0.0
        montant_paye2=0.0
        for order in self:
            order.montant_reste = order.montant_reel - order.montant_paye
        #for order in self:
            #if order.type_demande == 'Facture' or order.type_demande == 'Decision':
               #for line in order.line_ids:
                    #montant_paye1 +=line.montant_paye or 0.0
                #for line in order.invoice_ids:
                    #montant_paye2+=line.residual
                #montant_reste=montant_paye2 - montant_paye1
            #else:
                #montant_reste=order.montant_a_payer
            #order.montant_reste = montant_reste
            
    
    @api.depends('montant_a_payer','line_ids')
    def _compute_montant_paye(self):
        montant_paye=0.0
        for order in self:
            for line in order.line_ids:
                montant_paye+=line.montant_paye
            order.montant_paye = montant_paye or 0.0
            montant_paye=0.0
            
    def _compute_verif_compta(self):
        for manifold in self:
            for line in manifold.line_ids:
                if line.payment_id.state=='draft':
                    manifold.verif_compta='ok'
                    return {}
                else:
                    manifold.verif_compta='non'
    
    @api.multi
    def button_dommy(self, force=False):
        for manifold in self:
            for line in manifold.line_ids:
                if line.payment_id.state=='draft':
                    line.payment_id.post()
                    line.write({'state':'done'})
                    manifold.verif_compta='non'
                    manifold.button_partiel()
                    manifold.button_verif_paid()
                else:
                    manifold.verif_compta='non'
        return {}
     
    @api.multi
    def button_confirm1(self, force=False):
        #if len(self.manifold_line_ids) > 0 and self.type_manifold != 'Mixte':
        if self.name==False or self.name=="Nouveau":
            if self.type_depense == 'fonctionnel':
                seq = self.env['ir.sequence'].next_by_code('innoving.mandat.fonctionnel')
            elif self.type_depense == 'investissement':
                seq = self.env['ir.sequence'].next_by_code('innoving.mandat.investissement')
            self.write({'state': 'confirm', 'date_confirm': fields.Date.context_today(self), 'code':seq, 'name':seq})
    
    @api.multi
    def button_confirm(self, force=False):
        if self.type_demande == "Facture" or self.type_demande == "Decision" :
            if self.invoice_ids:
                self.env.cr.execute(("select count(invoice_id) as nombre from invoice_mandat_paiement_rel where invoice_id = %s") % (self.invoice_ids.id))
            else:
                raise UserError(_("Impossible de poursuivre cette opération! Merci de lier une facture à  ce mandat"))
            res=self.env.cr.dictfetchone()
            line_id=res['nombre']
            if line_id == 1:
                self.env['account.invoice'].browse([self.invoice_ids.id]).write({'paid':True})
                self.button_confirm1()
            else:
                self.env.cr.execute(("select mandat_id as reglement from invoice_mandat_paiement_rel where invoice_id = %s and mandat_id <> %s") % (self.invoice_ids.id,self.id))
                res=self.env.cr.dictfetchone()
                line_or_id=res['reglement']
                raise UserError(_("Impossible de Poursuivre! La ligne de facture fait déjà  l'objet d'un mandat de paiement: NÂ° : %s . Merci de contacter votre administrateur!") % (self.env['innoving.mandat'].browse(line_or_id).name))
        #=======================================================================
        # elif self.type_demande == "Bc":
        #     self.button_confirm1()
        #=======================================================================
        
    
        
    @api.multi
    def button_valid(self):
        for order_r in self:
            if order_r.state=="confirm":
                order_r.write({'state': 'valid', 'date_validation': fields.datetime.now(),'validateur':self.env.uid})
        return {}    
    
    
    @api.multi
    def button_approuv(self, force=False):
        self.write({'state': 'approuv', 'date_approbation': fields.datetime.now(),'approbateur':self.env.uid})
        return {}
            
    
    @api.multi
    def button_partiel(self):
        if self.state=='approuv' and len(self.line_ids) > 0:
            self.write({'state': 'partiel'})
        return {}
    
    
    @api.multi
    def button_regularisation(self):
        return self.write({'state': 'paid'})
    
    @api.multi
    def button_verif_paid(self):
        if (self.type_demande=="Facture" or self.type_demande=="Decision") and (self.state=='approuv' or self.state=='partiel'):
            if self.montant_estime == 0.0 or self.montant_reste == 0.0:
                return self.write({'state': 'paid'})
        if (self.state=='approuv' or self.state=='partiel') and (self.type_demande!="Facture" or self.type_demande=="Decision"):
            if self.montant_estime == 0.0 or self.montant_reste == 0.0:
                return self.write({'state': 'regularisation'})
            if sum(l.montant_paye for l in self.line_ids if l.state == 'draft') - self.montant_paye ==0:
                return self.write({'state': 'regularisation'})
        return {}
    

    @api.multi
    def button_paid(self, force=False):
        for order in self:
            if order.montant_reel > 0.0 :
                move_id = self.env['account.move'].create({
                        'name': '/',
                        'journal_id': order.journal_id.id,
                        'date':fields.Date.context_today(self),
                        'ref':order.name,
                        'currency_id': 42,
                        'company_id' : 1
                        })
                line1_id=move_id
                line2_id=move_id
                if move_id:
                    line1_id=self.env['account.move.line'].create({
                        'name': order.name,
                        'journal_id': order.journal_id.id,
                        'date':fields.Date.context_today(self),
                        'account_id':order.account_id.id,
                        'partner_id':order.partner_id.id,
                        'ref':order.name,
                        'date_maturity': fields.Date.context_today(self),
                        'move_id':move_id.id,
                        'reconciled': False
                        })
                    line2_id=self.env['account.move.line'].create({
                        'name': order.name,
                        'journal_id': order.journal_id.id,
                        'date': fields.Date.context_today(self),
                        'account_id': order.journal_id.default_credit_account_id.id,
                        'partner_id': order.partner_id.id,
                        'ref': order.name,
                        'date_maturity': fields.Date.context_today(self),
                        'move_id': move_id.id,
                        'reconciled': False
                    })
                self.env.cr.execute(("update account_move_line set debit=%s where id = %s") % (order.montant_reel,line1_id.id))
                self.env.cr.execute(("update account_move_line set credit=%s where id = %s") % (order.montant_reel,line2_id.id))
                self.env.cr.execute(("update account_move set amount=%s where id = %s") % (self.montant_paye,move_id.id))
                self.env['innoving.mandat.line'].create({
                    'montant_paye':order.montant_reel,
                    'montant_reste':0.0,
                    'user_id':order.env.uid,
                    'date':fields.Date.context_today(self),
                    'order_id':order.id,
                    'journal_id':order.journal_id.id,
                    'move_id': move_id.id
                    })
                self.button_partiel()
                self.button_verif_paid()
            else:
                raise UserError(_("Merci d'indiquer le montant à  payer pour continuer!"))
        return {}


    def sum_text(self, value=0):
        if value >= 0.0:
            return amount_to_text_fr(value,'Francs CFA')
    
#===============================================================================
#     @api.multi
#     def button_draft(self, force=False):
#         self.write({'state': 'draft'})
#         
#     @api.multi
#     def button_confirm(self, force=False):
#         if self.code == 'Nouveau' or self.ref:
#             if self.type_depense == 'fonctionnel':
#                 seq = self.env['ir.sequence'].next_by_code('innoving.mandat.fonctionnel')
#             elif self.type_depense == 'investissement':
#                 seq = self.env['ir.sequence'].next_by_code('innoving.mandat.investissement')
#             self.write({'state': 'confirm', 'date_confirm': fields.Date.context_today(self), 'code':seq, 'name':seq})
#         return {}
# 
#     @api.multi
#     def button_valid(self, force=False):
#         self.write({'state': 'valid', 'date_valid': fields.Date.context_today(self)})
# 
#     @api.multi
#     def button_cancel(self, force=False):
#         self.write({'state': 'cancel'})
#         
#     
#     @api.onchange('partner_id')
#     def _onchange_partner_id(self):
#         if self.partner_id:
#             self.account_id=self.partner_id.property_account_payable_id.id
#             return {}
#         else:
#             self.account_id= False
#             return {}
#         
#     @api.onchange('account_invoice_id')
#     def _onchange_account_invoice_id(self):
#         line=""
#         amount_paid=0
#         amount_reste=0
#         if self.account_invoice_id:
#             self.amount_reste = amount_reste
#             return {}
#         else:
#             self.amount_to_paid = False
#             self.date_prevue = False
#             self.amount_to_paid = False
#             self.amount_reste = False
#             return {}
#===============================================================================
        
        
class InnovingMandatLine(models.Model):
    _name = 'innoving.mandat.line'
    _inherit = ['mail.thread']
    _description = 'Innoving mandat Historique de Reglement'
    _order = "date desc"
    
    @api.model
    def _default_user_id(self):
        user_id = self.env.uid
        return user_id
    
    @api.model
    def default_get(self, fields):
        #rec = super(OrdreReglementLine, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        #raise UserError(_("Merci %s") % (active_ids))

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'innoving.mandat':
            raise UserError(_("Programmation error: the expected model for this action is 'OrdreReglementLine'. The provided one is '%s'.") % active_model)

        invoices = self.env[active_model].browse(active_ids)
        rec = {} #super(OrdreReglementLine, self).default_get(fields)
        #raise UserError(_("Merci %s") % (type(datetime.now())))
        rec.update({
            'montant_paye': invoices[0].montant_reste,
            'partner_id': invoices[0].partner_id.id,
            'beneficiaire': invoices[0].beneficiaire,
            'user_id' : self._default_user_id(),
            'date' : str(datetime.now()), #str(datetime.strptime(datetime.now(), '%Y-%m-%d')),
        })
        return rec
            
    
    name = fields.Char('Reference')
    montant_paye = fields.Float('Montant à  Payer')
    montant_reste = fields.Float('Reste à  payer')
    user_id = fields.Many2one('res.users','Utilisateur',default=_default_user_id)
    date = fields.Date('Date', default = fields.Datetime.now)
    mandat_id = fields.Many2one('innoving.mandat','Mandat de paiement')
    journal_id = fields.Many2one('account.journal','Journal')
    move_id = fields.Many2one('account.move','Piece comptable')
    payment_id = fields.Many2one('account.payment','Paiement')
    beneficiaire = fields.Char("A l'ordre de")
    type_reglement = fields.Selection([
        ('ESPECE', 'ESPECE'),
        ('CHEQUE', 'CHEQUE'),
        ('VIREMENT', 'VIREMENT'),
        ], string='Mode de reglement', track_visibility='always', default='CHEQUE')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    account_id = fields.Many2one('account.account','Compte')
    partner_id = fields.Many2one('res.partner','Fournisseurs')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', oldname="payment_method")
    state = fields.Selection([
        ('draft', '...'),
        ('done', 'Fait'),
        ], string='Etat', track_visibility='always', default='draft')  
    
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.account_id=self.partner_id.property_account_payable_id.id
            return {}
        else:
            self.account_id= False
            return {}
        
        
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.type=='cash':
                self.type_reglement="ESPECE"
            if self.journal_id.type=='bank':
                self.type_reglement="CHEQUE"
            return {}
        else:
            self.type_reglement= False
            return {}
        
        
    
    @api.multi
    def confirm(self):
        #raise UserError(_("Merci %s") % (self.montant_paye))
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        reglement_obj=self.env['innoving.mandat'].browse(active_ids[0])
        if (self.montant_paye > 0.0 and  self.montant_paye <= reglement_obj.montant_estime) or (self.montant_paye > 0.0) :
            pay_amount=self.montant_paye
            date=self.date
            partner_type='supplier'
            writeoff_acc=None
            pay_journal=self.journal_id.id
            #if isinstance( pay_journal, ( int, long ) ):
            if isinstance( pay_journal, ( int ) ):
                pay_journal = self.env['account.journal'].browse([pay_journal])
            payment_type = 'outbound'
            if payment_type == 'outbound':
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                journal_payment_methods = pay_journal.outbound_payment_method_ids
            if payment_method not in journal_payment_methods:
                raise UserError(_('No appropriate payment method enabled on journal %s') % pay_journal.name)
            communication = self.name
            payment_vals = {
                #'invoice_ids': [(0, 0, {invoice.ids})],
                'amount': pay_amount,
                'payment_date': date,
                'communication': communication,
                'partner_id': self.partner_id.id,
                'partner_type': partner_type,
                'journal_id': pay_journal.id,
                'payment_type': payment_type,
                'payment_method_id': payment_method.id,
                'payment_difference_handling': writeoff_acc and 'reconcile' or 'open',
                'writeoff_account_id': writeoff_acc and writeoff_acc.id or False,
            }
            if self.env.context.get('tx_currency_id'):
                payment_vals['currency_id'] = self.env.context.get('tx_currency_id')
    
            payment = self.env['account.payment'].create(payment_vals)
            if reglement_obj.type_demande=='Facture':
                invoice1 = self.env['innoving.mandat'].browse(active_ids[0]).invoice_ids[0]
                invoice = self.env['account.invoice'].browse(invoice1.id)
                self.env.cr.execute(("insert into account_invoice_payment_rel (payment_id,invoice_id) values (%s,%s)") % (payment.id,invoice.id))
                self.write({'payment_id':payment.id,'mandat_id':self._context.get('active_ids')[0]})
                reglement_obj.write({'verif_compta':'ok','montant_a_payer':reglement_obj.montant_a_payer-pay_amount})
            else:
                amount_diff = reglement_obj.montant_a_payer - pay_amount
                self.write({'payment_id':payment.id,'mandat_id':self._context.get('active_ids')[0]})
        else:
            raise UserError(_("Erreur sur le montant à  payer. Merci d'indiquer un montant entre %s et %s pour continuer!") % (1,reglement_obj.montant_reste))
        return {}
    
    
    
class InnovingMandatLine2(models.Model):
    _name = 'innoving.mandat.line2'
    #_inherit = ['mail.thread']
    _description = 'Innoving mandat Historique reguls'
    _order = "date desc"
    
    @api.model
    def _default_user_id(self):
        user_id = self.env.uid
        return user_id
    
    @api.model
    def default_get(self, fields):
        rec = super(InnovingMandatLine2, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        #raise UserError(_("Merci %s") % (active_ids))

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'innoving.mandat':
            raise UserError(_("Programmation error: the expected model for this action is 'OrdreReglementLine'. The provided one is '%s'.") % active_model)

        invoices = self.env[active_model].browse(active_ids)
        rec.update({
            'montant_paye': invoices[0].montant_reste,
            'partner_id': invoices[0].partner_id.id,
            'beneficiaire': invoices[0].beneficiaire
        })
        return rec
    
    
    name = fields.Char('Reference')
    montant_paye = fields.Float('Montant retourné')
    montant_reste = fields.Float('Reste à  payer')
    user_id = fields.Many2one('res.users','Utilisateur',default=_default_user_id)
    #date = fields.Date('Date', default = fields.Datetime.now)
    date = fields.Datetime('Date', default=lambda self: fields.datetime.now())
    order_id = fields.Many2one('innoving.mandat','Ordre de reglement')
    journal_id = fields.Many2one('account.journal','Journal')
    move_id = fields.Many2one('account.move','Piece comptable')
    payment_id = fields.Many2one('account.payment','Paiement')
    beneficiaire = fields.Char("A l'ordre de")
    type_reglement = fields.Selection([
        ('ESPECE', 'ESPECE'),
        ('CHEQUE', 'CHEQUE'),
        ('VIREMENT', 'VIREMENT'),
        ], string='Mode de reglement', track_visibility='always', default='CHEQUE')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    account_id = fields.Many2one('account.account','Compte')
    partner_id = fields.Many2one('res.partner','Fournisseurs')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', oldname="payment_method")
    state = fields.Selection([
        ('draft', '...'),
        ('done', 'Fait'),
        ], string='Etat', track_visibility='always', default='draft')
    regularisation = fields.Selection([
        ('retour', 'Avec retour en caisse'),
        ('regul', 'Sans retour en caisse'),
        ], string='Régularisation', track_visibility='always', default='regul')
    
    
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.account_id=self.partner_id.property_account_payable_id.id
            return {}
        else:
            self.account_id= False
            return {}
        
        
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.type=='cash':
                self.type_reglement="ESPECE"
            if self.journal_id.type=='bank':
                self.type_reglement="CHEQUE"
            return {}
        else:
            self.type_reglement= False
            return {}
    
    @api.multi
    def confirm(self):
        #raise UserError(_("Merci %s") % (self.montant_paye))
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        reglement_obj=self.env['innoving.mandat'].browse(active_ids[0])
        if self.montant_paye > 0.0 and  self.montant_paye <= reglement_obj.montant_paye and self.regularisation == "retour":           
            pay_amount=self.montant_paye
            date=fields.Date.context_today(self)
            partner_type='supplier'
            writeoff_acc=None
            pay_journal=self.journal_id.id
            if isinstance( pay_journal, ( int) ):
                pay_journal = self.env['account.journal'].browse([pay_journal])
            payment_type = 'inbound'
            if payment_type == 'inbound':
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                journal_payment_methods = pay_journal.outbound_payment_method_ids
            if payment_method not in journal_payment_methods:
                raise UserError(_('No appropriate payment method enabled on journal %s') % pay_journal.name)
            
            communication = self.name
            payment_vals = {
                #'invoice_ids': [(0, 0, {invoice.ids})],
                'amount': pay_amount,
                'payment_date': date,
                'communication': communication,
                'partner_id': self.partner_id.id,
                'partner_type': partner_type,
                'journal_id': pay_journal.id,
                'payment_type': payment_type,
                'payment_method_id': payment_method.id,
                'payment_difference_handling': writeoff_acc and 'reconcile' or 'open',
                'writeoff_account_id': writeoff_acc and writeoff_acc.id or False,
            }
            
            if self.env.context.get('tx_currency_id'):
                payment_vals['currency_id'] = self.env.context.get('tx_currency_id')
                
            
    
            payment = self.env['account.payment'].create(payment_vals)
            #raise UserError(_("Pive_ids in context.  %s") % (self.partner_id.id))
            line_vals = {
                'name' : communication,
                'montant_paye' : -pay_amount,
                'montant_reste' : 0.0,
                'user_id' : self.user_id.id ,
                'date' : date,
                'order_id' : self._context.get('active_ids')[0],
                'journal_id' : pay_journal.id,
                #'move_id' : ,
                'payment_id' : payment.id,
                'beneficiaire' : self.beneficiaire,
                'type_reglement' : self.type_reglement,
                'currency_id' : self.currency_id.id,
                'account_id' : self.account_id.id,
                'partner_id' : self.partner_id.id,
                #'company_id' : '',
                'payment_method_id' : payment_method.id,
                'state' : 'draft',
            }
            #raise UserError(_(" ok "))
            payment_line = self.env['innoving.mandat.line'].create(line_vals)
            for line in reglement_obj.line_ids:
                self.env['account.payment'].browse(line.payment_id.id).write({'partner_id' : self.partner_id.id})
        elif self.regularisation == "regul":
            for line in reglement_obj.line_ids:
                #line.write({'partner_id' : self.partner_id.id})
                self.env['account.payment'].browse(line.payment_id.id).write({'partner_id' : self.partner_id.id})
        ### Comptabilisation    
        for line in reglement_obj.line_ids:
            if line.payment_id.state=='draft':
                line.payment_id.post()
                #raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
                line.write({'state':'done'})
                 
                reglement_obj.verif_compta='non'
                reglement_obj.button_regularisation()
                reglement_obj.write({'partner_id':self.partner_id.id,'account_id':self.account_id.id})
                reglement_obj.button_verif_paid()
            else:
                reglement_obj.verif_compta='non'
            return {}
    
    
    
class InnovingMandatWizard(models.TransientModel):
    _name = 'innoving.mandat.wizard'
    _description = 'innoving mandat wizard de Reglement'
    
    
    @api.model
    def _default_user_id(self):
        user_id = self.env.uid
        return user_id
    
    @api.model
    def default_get(self, fields):
        rec = super(InnovingMandatWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        #raise UserError(_("Merci %s") % (active_ids))

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'innoving.mandat':
            raise UserError(_("Programmation error: the expected model for this action is 'OrdreReglementWizard'. The provided one is '%s'.") % active_model)

        invoices = self.env[active_model].browse(active_ids)
        rec.update({
            'montant_paye': invoices[0].montant_estime,
            'partner_id': invoices[0].partner_id.id,
            'beneficiaire': invoices[0].beneficiaire
        })
        return rec
    
    name = fields.Char('Reference')
    montant_paye = fields.Float('Montant Payé')
    montant_reste = fields.Float('Reste à  payer')
    user_id = fields.Many2one('res.users','Utilisateur',default=_default_user_id)
    date = fields.Datetime('Date', default = fields.Datetime.now)
    #order_id = fields.Many2one('innoving.mandat','Ordre de reglement')
    journal_id = fields.Many2one('account.journal','Journal')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    account_id = fields.Many2one('account.account','Compte')
    partner_id = fields.Many2one('res.partner','Fournisseurs')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    beneficiaire = fields.Char("A l'ordre de")
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method")
    type_reglement = fields.Selection([
        ('ESPECE', 'ESPECE'),
        ('CHEQUE', 'CHEQUE'),
        ('VIREMENT', 'VIREMENT'),
        ], string='Mode de reglement', track_visibility='always', default='CHEQUE')
    
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.account_id=self.partner_id.property_account_payable_id.id
            return {}
        else:
            self.account_id= False
            return {}
        
        
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.type=='cash':
                self.type_reglement="ESPECE"
            if self.journal_id.type=='bank':
                self.type_reglement="CHEQUE"
            return {}
        else:
            self.type_reglement= False
            return {}
    
    @api.multi
    def confirm(self):
        #raise UserError(_("Merci %s") % (self.montant_paye))
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        #raise UserError(_(" : .%s") % (active_ids))
        if self.montant_paye > 0.0 :
            invoice1 = self.env['innoving.mandat'].browse(active_ids[0]).invoice_ids[0]
            invoice = self.env['account.invoice'].browse(invoice1.id)
            #raise UserError(_("Merci %s") % (invoice.ids))            
            pay_amount=self.montant_paye
            date=fields.Date.context_today(self)
            partner_type='supplier'
            writeoff_acc=None
            #ids=invoice.id
            pay_journal=self.journal_id.id
            if isinstance( pay_journal, ( int ) ):
                pay_journal = self.env['account.journal'].browse([pay_journal])
            payment_type = 'outbound'
            if payment_type == 'outbound':
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                journal_payment_methods = pay_journal.outbound_payment_method_ids
            if payment_method not in journal_payment_methods:
                raise UserError(_('No appropriate payment method enabled on journal %s') % pay_journal.name)
    
            communication = self.name
            #raise UserError(_("Merci %s") % (ids))
            payment_vals = {
                #'invoice_ids': [(0, 0, {invoice.ids})],
                'amount': pay_amount,
                'payment_date': date,
                'communication': communication,
                'partner_id': self.partner_id.id,
                'partner_type': partner_type,
                'journal_id': pay_journal.id,
                'payment_type': payment_type,
                'payment_method_id': payment_method.id,
                'payment_difference_handling': writeoff_acc and 'reconcile' or 'open',
                'writeoff_account_id': writeoff_acc and writeoff_acc.id or False,
            }
            if self.env.context.get('tx_currency_id'):
                payment_vals['currency_id'] = self.env.context.get('tx_currency_id')
    
            payment = self.env['account.payment'].create(payment_vals)
            if invoice1.type_demande== 'Facture' or invoice1.type_demande== 'Decision' :
                self.env.cr.execute(("insert into account_invoice_payment_rel (payment_id,invoice_id) values (%s,%s)") % (payment.id,invoice.id))
            
            self.env['innoving.mandat.line'].create({
                    'montant_paye':self.montant_paye,
                    'montant_reste':0.0,
                    'user_id':self.env.uid,
                    'date':fields.Date.context_today(self),
                    'order_id':active_ids[0],
                    'journal_id':self.journal_id.id,
                    #'move_id': move_id,
                    'payment_id' : payment.id
                    })
            self.env['innoving.mandat'].browse(active_ids[0]).button_partiel()
            self.env['innoving.mandat'].browse(active_ids[0]).button_verif_paid()
        else:
            raise UserError(_("Merci d'indiquer le montant à  payer pour continuer!"))
        return {}
    
    
class InnovingMandatCancel(models.Model):
    _name = 'innoving.mandat.cancel'
    _inherit = ['mail.thread']
    _description = 'Innoving mandat reglement cancel'
    _order = "date desc"
    
    @api.model
    def _default_demandeur(self):
        user_id = self.env.uid
        return user_id
    
    order_id = fields.Many2one('innoving.mandat', string='Mandat', track_visibility='always')
    name = fields.Text("Motif")
    date = fields.Datetime('Date',default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'Utilisateur',default=_default_demandeur)
    
    @api.multi
    def confirm(self):
        #raise UserError(_("Merci %s") % (self._context.get('active_ids')))
        self.write({'order_id':self._context.get('active_ids')[0]})
        self.env['innoving.mandat'].browse(self._context.get('active_ids')).button_cancel()
        #self.env['manifold'].button_cancel()
        return True