# -*- coding: utf-8 -*-

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang

from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools.amount_to_text_frr import amount_to_text_fr

import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ['account.invoice']          
            
            
    note = fields.Text('Objet de la dépense', copy=True, track_visibility='always')
    paid = fields.Boolean("Mandat", default=False, track_visibility='always')
    mandat_id = fields.Many2one('innoving.mandat',string="N° Mandat", track_visibility='always')
    numero_facture_origine = fields.Char(string='N° Facture Origine', track_visibility='always')
    is_carburant = fields.Boolean(string="Achat de carburant", default=False, track_visibility='always')
    date_edition_fournisseur = fields.Date(string='Date du fournisseur', track_visibility='always')
    type_depense = fields.Selection(string="Type de dépense", selection=[
        ('fonctionnel', 'Dépense de Fonctionnement'),
        ('investissement', 'Dépense d\'Investissement')
        ], track_visibility='always', default='fonctionnel')
    type_fond = fields.Selection(string="Sur", selection=[
        ('Fond propre', 'Fond propre'),
        ('Aide Etat', 'Aide Etat')
        ], track_visibility='always', default='Fond propre')
    type_mandat = fields.Selection(string="Type de mandat", selection=[
        ('Normal', 'Normal'),
        ('Prelevement', 'Prelevement'),
        ('Ordre de recette', 'Ordre de recette')
        ], track_visibility='always', default='Normal')
    mandat_ok = fields.Boolean(string="Mandat Ok")
    account_patrimoine_id = fields.Many2one('account.account','Compte Patrimoniale')
    budget_id = fields.Many2one('crossovered.budget','Budget')
    
    @api.onchange('date_edition_fournisseur')
    def _onchange_date_edition_fournisseur(self):
        if self.date_edition_fournisseur:
            self.date_invoice=fields.Date.context_today(self)
            return {}
        
    def sum_text(self, value=0):
        if value >= 0.0:
            return amount_to_text_fr(value,'Francs CFA')
        
    @api.multi
    def button_gen_mandat(self, force=False):
        for order_r in self:
            if order_r.mandat_ok == False:
                if order_r.state=="open":
                    tax = 0.0
                    budget_id = ""
                    montant_alloue=""
                    depense_anterieur=""
                    montant_disponible=""
                    compte_fonctionel = ""
                    code = ""
                    compte_analytic = ""
                    barre = ""
                    compte_patrimoine = ""
                    code_patrimoine = ""
                    account_patrimoniale_id = ""
                    code_patrimoniale = ""
                    compte_analytic_patrimoine = ""
                    barre_patrimoine = ""
                    md=""
                    type_demande = ""
                    type_fond = ""
                    type_mandat = ""
                    compte_id = order_r.partner_bank_id.id
                    numero_compte_fournisseur = order_r.partner_bank_id.acc_number
                    banque_name = order_r.partner_bank_id.bank_id.name
                    agence = order_r.partner_bank_id.bank_id.city
                    montant_reste = order_r.residual
                    
                    for l in order_r.tax_line_ids:
                        tax += l.amount
                    for ol in order_r.invoice_line_ids:
                        if len(ol) == 1:
                            if self.type_depense == "fonctionnel":
                                compte_patrimoine = ol.account_id.id
                                code_patrimoine = ol.account_id.code
                                account_patrimoniale_id = order_r.account_patrimoine_id.id
                                code_patrimoniale = order_r.account_patrimoine_id.code
                                compte_fonctionel = ol.account_id.id
                                code = ol.account_id.code
                                compte_analytic = ol.account_analytic_id.id
                                barre = ol.account_analytic_id.code
                                type_demande = "Facture"

                            elif self.type_depense == "investissement":
                                compte_analytic = ol.account_analytic_id.id
                                compte_patrimoine = ol.account_id.id
                                code_patrimoine = ol.account_id.code
                                compte_analytic_patrimoine = ol.account_analytic_id.id
                                barre_patrimoine = ol.account_analytic_id.code
                                type_demande = "Decision"
                                type_fond = order_r.type_fond
                                type_mandat = order_r.type_mandat
                                account_patrimoniale_id = order_r.account_patrimoine_id.id
                                code_patrimoniale = order_r.account_patrimoine_id.code
                            #for cbl in ol.account_analytic_id.crossovered_budget_line:
                            budget_id = order_r.budget_id.id
                            account_name = ol.account_id.code + ' ' + ol.account_id.name
                            record = self.env['crossovered.budget.lines'].search([('crossovered_budget_id', '=', budget_id),('analytic_account_id', '=', compte_analytic),('general_budget_id.name', '=', account_name)])
                            #raise UserError(_("%s") % (record.id))
                            for cbl in record:
                                #for self.env['crossovered.budget.line'].search([('invoice_id', '=', val)]):
                                if len(cbl) == 1:
                                    mt_alloue = cbl.planned_amount
                                    dp_anterieur = cbl.practical_amount
                                    if mt_alloue < 0:
                                        montant_alloue = cbl.planned_amount * (-1)
                                    else:
                                        montant_alloue = cbl.planned_amount
                                    if dp_anterieur < 0:
                                        depense_anterieur = (cbl.practical_amount * (-1)) - order_r.residual
                                    else:
                                        depense_anterieur = cbl.practical_amount
                                    md = montant_alloue - depense_anterieur
                                    montant_disponible = md - order_r.residual
                                    budget_id = cbl.crossovered_budget_id.id
                                else:
                                    raise UserError(_("Attention, Une erreur de saisi dans les lignes du budget"))
                    mandat_id = self.env['innoving.mandat'].create({
                        'note': order_r.note,
                        'partner_id': order_r.partner_id.id,
                        'is_carburant': order_r.is_carburant,
                        'numero_facture_origine': order_r.reference,
                        'selon_facture': order_r.reference,
                        'date_edition_fournisseur': order_r.date_edition_fournisseur,
                        'type_depense': order_r.type_depense,
                        'type_fond': type_fond,
                        'type_mandat': type_mandat,
                        'beneficiaire': order_r.partner_id.name,
                        'compte_id':compte_id,
                        'numero_compte_fournisseur':numero_compte_fournisseur,
                        'banque_name':banque_name,
                        'agence':agence,
                        'account_id': order_r.partner_id.property_account_payable_id.id,
                        'budget_id':budget_id,
                        'account_fonctionnel_id': compte_fonctionel,
                        'account_fonctionnel_code':code,
                        'account_analytic_id':compte_analytic,
                        'barre_account_fonctionnel':barre,
                        'montant_alloue':montant_alloue,
                        'depense_anterieur':depense_anterieur,
                        'depense_actuelle':order_r.residual,
                        'montant_disponible':montant_disponible,
                        'account_patrimoine_id':compte_patrimoine,
                        'account_patrimoine_code':code_patrimoine,
                        'account_patrimoine_analytic_id':compte_analytic_patrimoine,
                        'barre_account_patrimoine':barre_patrimoine,
                        'date_prevue': order_r.date_due,
                        'montant_estime': order_r.residual,
                        'type_demande': type_demande,
                        'montant_reel': order_r.residual,
                        'montant_reste': montant_reste,
                        'montant_a_payer': order_r.residual,
                        'account_patrimoniale_id': account_patrimoniale_id,
                        'account_patrimoniale_code': code_patrimoniale,
                    })
                    #raise UserError(_("%s") % (code_patrimoniale))
                    if mandat_id:
                        self.env['account.invoice'].browse(order_r.id).write({'mandat_id': mandat_id.id,'mandat_ok':True})
                        self.env.cr.execute(("insert into invoice_mandat_paiement_rel (mandat_id,invoice_id) values (%s,%s)") % (mandat_id.id,order_r.id))
                        self.env['innoving.mandat'].browse(mandat_id.id).button_confirm1()
                        #self.env['innoving.mandat'].browse(mandat_id.id).button_valid()
                    #raise UserError(_("%s") % (montant_reste))
                else:
                    raise UserError(_("Le mandat ne peut être généré car facture est encore au brouillon"))
            else:
                raise UserError(_("Le mandat de cette facture a déjà été généré"))
        return {}
    
