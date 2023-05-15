# -*- coding: utf-8 -*-

import time
import datetime
from dateutil.relativedelta import relativedelta

import openerp
from openerp import tools
from openerp import api, fields, osv, exceptions, models
from openerp.tools.translate import _

import logging

_logger = logging.getLogger(__name__)


def str_to_datetime(strdate):
    dt = datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)
    return  dt
#23/09/17
class hr_type_piece(models.Model):
    _name="hr.type.piece"
    _description="Type de pièce d'identité"


    name= fields.Char("Désignation",size=128,required=True)
    description= fields.Text("Description")


class hr_piece_identite(models.Model):
    _name="hr.piece.identite"
    _rec_name="numero_piece"
    _decription="Pièce d'identité"

    numero_piece = fields.Char("Numéro de la pièce",size=128,required=True)
    nature_piece= fields.Selection([('attestion',"Attestation d'indentité"),("carte_sejour","Carte de séjour"),
                                   ("cni","CNI"),("passeport","Passeport")],string="Nature",required=True)
    date_etablissement= fields.Date("Date d'établissement",required=True)
    autorite= fields.Char("Autorité",size=128)

class hr_contract(models.Model):

    @api.multi
    def calcul_anciennete_actuel(self):
        anciennete={}
        self.ensure_one()
        #date_debut=datetime.strptime(self.date_start,'%Y-%m-%d')
        date_debut=datetime.datetime.strptime(self.date_start,'%Y-%m-%d')
        #today = datetime.now()
        today = datetime.datetime.now()
        nbre_year=0
        nbre_mois= 0
        while date_debut <= today :
            #date_debut = date_debut + relativedelta.relativedelta(years=+1)
            date_debut = date_debut + relativedelta(years=+1)
            if date_debut > today :
                #date_debut = date_debut + relativedelta.relativedelta(years=-1)
                date_debut = date_debut + relativedelta(years=-1)
                break

            nbre_year+=1
        while date_debut < today :
            #date_debut = date_debut + relativedelta.relativedelta(months=+1)
            date_debut = date_debut + relativedelta(months=+1)
            if date_debut > today :
                break
            nbre_mois+=1
        nbre_mois +=self.mois_report
        temp = nbre_mois - 12
        if temp >= 0:
            nbre_year+=1
            nbre_mois = temp
        anciennete={
                'year_old':nbre_year + self.an_report,
                'month_old':nbre_mois,
            }

        return anciennete


    @api.one
    def _get_anciennete(self):
        res={}
        anciennete=self.calcul_anciennete_actuel()
        if anciennete:
            self.an_anciennete= anciennete['year_old']
            self.mois_anciennete= anciennete['month_old']

        
    _inherit="hr.contract"

    expatried= fields.Boolean('Expatrié', default=False)
    an_report= fields.Integer('Année',size=2)
    mois_report= fields.Integer('Mois report')
    an_anciennete= fields.Integer("Nombre d'année", compute=_get_anciennete)
    mois_anciennete= fields.Integer('Nombre de mois', compute=_get_anciennete)
    anne_anc= fields.Integer('Année')
    categorie_id= fields.Many2one("hr.categorie.contract",'Catégorie')
    sursalaire= fields.Integer('Sur Salaire',required=False)
    hr_convention_id= fields.Many2one('hr.convention',"Convention",required=False)
    hr_secteur_id= fields.Many2one('hr.secteur.activite',"Secteur d'activité",required=False)
    categorie_salariale_id= fields.Many2one('hr.categorie.salariale', 'Catégorie salariale', required=False)
    hr_payroll_prime_ids= fields.One2many("hr.payroll.prime.montant",'contract_id',"Primes")
    wage = fields.Float("Salaire de base", required=True)
    # state= fields.Selection([('draft','Draft'),('in_progress',"En cours"),('ended','Terminé'),('cancel','Annulé')]
    #                         ,'Eat du contrat', select=True, readonly=True, default="draft")
    type_ended= fields.Selection([('licenced','Licencement'),('hard_licenced','Licencement faute grave'),
                ('ended','Fin de contract'),], 'Type de clôture', select=True)
    description_cloture= fields.Text("Motif de Clôture")
    code_type_contrat = fields.Char(related='type_id.code',string="Code type contrat",store=True)
    time_fixed = fields.Float('Nombre d''heures fixe prévues')
    trial_date_start = fields.Date('Date de fin essai')


    @api.multi
    def validate_contract(self):
        return self.write({'state':'open'})


    @api.multi
    def closing_contract(self):
        view_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'hr_contract_extension', 'hr_contract_closed_form_view')
        #raise osv.except_osv('Test',view_id)
    
        return {
                'name':_("Clôture de contrat"),
                'view_mode': 'form',
                'view_id': view_id[1],
                'view_type': 'form',
                'res_model': 'hr.contract.closed',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': self._context,
            }

    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})


    @api.onchange("hr_convention_id")
    def on_change_convention_id(self):
        if self.hr_convention_id :
            return {'domain':{'hr_secteur_id':[('hr_convention_id','=',self.hr_convention_id.id)]}}
        else :
            return {'domain':{'hr_secteur_id':[('hr_convention_id','=',False)]}}

    @api.onchange("hr_secteur_id")
    def on_change_secteur_id(self):
        if self.hr_secteur_id :
            return {'domain':{'categorie_salariale_id':[('hr_secteur_activite_id','=', self.hr_secteur_id.id)]}}
        else :
            return {'domain':{'categorie_salariale_id':[('hr_secteur_activite_id','=',False)]}}
        

    @api.onchange('categorie_salariale_id')
    def on_change_categorie_salariale_id(self):
        if self.categorie_salariale_id:
            self.wage= self.categorie_salariale_id.salaire_base

#26/09/2017

    @api.multi
    def report_print(self):
        template = 'hr_contract_extension.report_contract_determiner'
        return self.env['report'].get_action(self, template)

    @api.multi
    def report_convention(self):
        template = 'hr_contract_extension.report_contract_convention'
        return self.env['report'].get_action(self, template)

    @api.multi
    def report_fin(self):
        template = 'hr_contract_extension.report_contract_fin'
        return self.env['report'].get_action(self, template)

    @api.one
    def send_contract(self, email_id, context=None):
        tmp_id = self.env['ir.model.data'].get_object_reference('hr_contract_extension', email_id)[1]
        try:
            mail_tmp = self.env['mail.template'].browse(tmp_id)
            mail_tmp.send_mail(res_id=self.id, force_send=True)
            return True
        except:
            return False

    @api.model
    def send_notification(self):
        _logger.info('Debut du Cron pour envoi de notification')
        #sélectionne les types de contrats ayant un modèle de notification
        type_contract = self.env['hr.contract.type'].search([('notify_id','!=',False)])

        for type in type_contract:
            for lines in type.notify_id.line_ids:
                if lines.type=='mois':
                    notif_date=datetime.datetime.now()+relativedelta(months=lines.number)
                if lines.type=='an':
                    notif_date=datetime.datetime.now()+relativedelta(years=lines.number)
                if lines.type=='day':
                    notif_date=datetime.datetime.now()+relativedelta(days=lines.number)
                if lines.type=='hours':
                    notif_date=datetime.datetime.now()+relativedelta(hours=lines.number)

                contract_notif=self.env['hr.contract'].search([('type_id','=',type.id),('state','=','open'),('date_end','<=',notif_date)])
                for contract in contract_notif:
                    contract.send_contract("email_template_leave_request_contract")


class hr_payroll_prime(models.Model):
    _name = "hr.payroll.prime"
    _description = "prime"

    name= fields.Char('name', size=64,required=True)
    code= fields.Char('Code', size=64, required=True)
    description= fields.Text('Description')



class hr_payroll_prime_montant(models.Model):

    @api.one
    @api.depends('prime_id')
    def _get_code_prime(self):
        if self.prime_id :
            self.code= self.prime_id.code
    
    _name="hr.payroll.prime.montant"

    prime_id= fields.Many2one('hr.payroll.prime','prime',required=True)
    code= fields.Char("Code",compute=_get_code_prime)
    contract_id= fields.Many2one('hr.contract','Contract')
    montant_prime= fields.Integer('Montant', required=True)



class hr_contract_type(models.Model):
    _inherit="hr.contract.type"
    _name="hr.contract.type"
	
    @api.multi
    @api.depends("notify_users")
    def get_mail(self):
        mail_user = ''
        for user in self.notify_users:
            mail_user += user.login + ';'
        self.notify_user_mail = mail_user

    code = fields.Char("Code",siez=5,required=True)
    notify_id = fields.Many2one("notify.model",'Modèle de notification')
    notify_users = fields.Many2many('res.users' , string='Personnes à notifier')
    notify_user_mail = fields.Char(compute='get_mail')



