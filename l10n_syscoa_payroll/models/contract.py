import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _default_governmental_org(self):
        return self.env.user.company_id.governmental_org or False

    @api.model
    def _get_default_journal(self):
        comp_id = 0
        for contract in self:
            comp_id = (contract.company_id and contract.company_id.id)
        if comp_id:
            jrnl = self.env['account.journal'].search([('code', '=', 'PAY'), ('company_id', '=', comp_id)])
        else:
            jrnl = self.env['account.journal'].search([('code', '=', 'PAY')])
        return jrnl and jrnl[0]

    @api.multi
    def _read_governmental_org(self):
        for line in self:
            line.governmental_org = self._default_governmental_org()

    @api.onchange('transport_refund', 'transport_refund_frequence')
    def onchange_transport_refund(self):
        self.ensure_one()
        if self.transport_refund:
            if self.transport_refund_frequence == 'month':
                if self.transport_refund > float(20800.00):
                    self.transport_refund = float(20800.00)
            elif self.transport_refund_frequence == 'day':
                if self.transport_refund > float(950.00):
                    self.transport_refund = float(950.00)

    @api.multi
    def _read_social_parts(self):
        for line in self:
            social_parts = line.employee_id.social_parts or False
            line.niveau = "{:.1f}".format(social_parts)

    @api.multi
    def _read_coefficient(self):
        for line in self:
            line.coef = line.employee_id.coef or False

    @api.multi
    def _get_seniority_date(self):
        for line in self:
            if line.seniority_date_manual:
                line.seniority_date = line.seniority_date_manual_input
            else:
                line.seniority_date = line.date_start

    @api.multi
    def _get_seniority(self):
        for line in self:
            date_1 = datetime.strptime(str(line.seniority_date), '%Y-%m-%d')
            date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
            number_of_year = relativedelta.relativedelta(date_2, date_1).years
            number_of_month = relativedelta.relativedelta(date_2, date_1).months
            year_text = "an" if (number_of_year <= 1) else "ans"
            line.seniority = str(number_of_year) + ' ' + year_text + ' et ' + str(number_of_month) + ' mois'

    @api.multi
    def _calculate_seniority_allowance(self):
        for line in self:
            if line.seniority_allowance_manual:
                line.seniority_allowance = float(line.seniority_allowance_manual_input)
            else:
                # Read seniority in years
                date_1 = datetime.strptime(str(line.seniority_date), '%Y-%m-%d')
                date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
                seniority = relativedelta.relativedelta(date_2, date_1).years
                if seniority > 25:  # max 25 years
                    seniority = 25
                if seniority >= 2:
                    line.seniority_allowance = float(float(line.wage) * seniority / 100)

    @api.multi
    def _get_mutual_insurance_empl(self):
        for line in self:
            if line.mutual_insurance_empl_manual:
                line.mutual_insurance_employee = float(line.mutual_insurance_empl_manual_input)
            else:
                # Read default mutual_insurance for employee from company data
                # B                res[line.id] = float(self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.mutual_insurance_employee or False)
                line.mutual_insurance_employee = 0.0

    def get_somme_rubrique(self, obj, code):

        payslip_ids = self.env['hr.payslip'].search(self.cr, self.uid, [('employee_id', '=', obj.employee_id.id)])
        payslip_obj = self.env['hr.payslip'].browse(self.cr, self.uid, payslip_ids)

        cpt = 0
        annee = obj.date_to[2:4]
        print(annee)
        for payslip in payslip_obj:
            for line in payslip.line_ids:
                if line.salary_rule_id.code == code and obj.date_to >= payslip.date_to and payslip.date_to[
                                                                                           2:4] == annee:
                    cpt += line.total
        return cpt

    @api.multi
    def _get_mutual_insurance_comp(self):
        for line in self:
            if line.mutual_insurance_comp_manual:
                line.mutual_insurance_comp = float(line.mutual_insurance_comp_manual_input)
            else:
                # Read default mutual_insurance for company from company data
                # B                line. = float(self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.mutual_insurance_company or False)
                line.mutual_insurance_comp = 0.0

    @api.multi
    def _get_gross_invoice(self):
        for line in self:
            if line.gross_invoice_manual:
                line.gross_invoice = float(line.wage)
            else:
                line.gross_invoice = float(line.wage)

    @api.multi
    def _get_leave_days(self):
        for line in self:
            line.leave_days = 0.00
            if line.attribute_leave_days:
                if line.leave_days_manual:
                    line.leave_days = float(line.leave_days_manual_input)
                else:
                    line.leave_days = 2.0

    type_id = fields.Many2one('hr.contract.type', "Type de contrat", required=True)
    struct_id = fields.Many2one('hr.payroll.structure', 'Structure salariale')
    governmental_org = fields.Boolean(compute="_read_governmental_org", method=True, string="Organisme gouvernemental")
    functionary = fields.Boolean(
        "Fonctionnaire de l'état",
        default=_default_governmental_org,
        help="Les fonctionnaires ont droit à une remise de 10% sur l'impôt sur le revenu. Si vous êtes une entreprise publique, alors vous pouvez configurer cette remise pour tous les employés dans les paramètres de la société")

    time_mod = fields.Selection((('fixed', 'Heures de travail fixes'), ('variable', 'Heures de travail variables')), string="Mode de gestion du temps", required=True, default="fixed")
    time_fixed = fields.Float(string="Nombre d'heures fixe prévues", default=173.33, required=True)

    pay_mod = fields.Selection((('Virement', 'Virement'), ('Cheque', 'Chèque'), ('Espece', 'Espèce')), 'Mode de paiement préféré')
    qualif = fields.Char("Qualification")
    niveau = fields.Char(compute="_read_social_parts", method=True, string="Niveau")
    coef = fields.Integer(compute="_read_coefficient", method=True, string="Coefficient")
    indice = fields.Char('Indice')
    category = fields.Char('Catégorie')

    gross_invoice_manual = fields.Boolean("Montant brut facturé")
    gross_invoice = fields.Float(compute="_get_gross_invoice", method=True, string="Montant brut facturé", digits_compute=dp.get_precision('Account'))
    additional_salary = fields.Float('Sursalaire', digits_compute=dp.get_precision('Payroll'))

    union_fee = fields.Float('Cotisation syndicale', digits_compute=dp.get_precision('Payroll'))

    performance_bonus = fields.Float('Prime de rendement', digits_compute=dp.get_precision('Payroll'))
    gratification = fields.Float('Gratification', digits_compute=dp.get_precision('Payroll'))

    seniority_date_manual = fields.Boolean("Date de début", help="La date de début pour le calcul de l'ancienneté est normalement eǵale à la date de début du contrat. Mais vous pouvez la saisir manuellement en activant ce bouton.")
    seniority_date_manual_input = fields.Date("Date de début", digits_compute=dp.get_precision('Payroll'), help="La date de début pour le calcul de l'ancienneté est normalement eǵale à la date de début du contrat. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    seniority_date = fields.Date(compute="_get_seniority_date", method=True, string="Date de début", help="La date de début pour le calcul de l'ancienneté est normalement eǵale à la date de début du contrat. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    seniority = fields.Char(compute="_get_seniority", method=True, string="Ancienneté")

    seniority_allowance_manual = fields.Boolean("Indemnité d'ancienneté", help="L'indemnité d'ancienneté est normalement calculée automatiquement. Mais vous pouvez le saisir manuellement en activant ce bouton.")
    seniority_allowance_manual_input = fields.Float("Indemnité d'ancienneté", digits_compute=dp.get_precision('Payroll'), help="L'indemnité d'ancienneté est normalement calculée automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")
    seniority_allowance = fields.Float(compute="_calculate_seniority_allowance", method=True, string="Indemnité d'ancienneté", digits_compute=dp.get_precision('Account'), help="L'indemnité d'ancienneté est normalement calculée automatiquement. Mais vous pouvez le saisir manuellement en activant le bouton à côté.")

    yearly_max_leaves = fields.Float('Droit de congé par année (en jours)')
    attribute_leave_days = fields.Boolean("Attribuer les congés automatiquement", default=True)
    leave_days_manual = fields.Boolean("Nombre de jours à attribuer par mois", help="Le nombre de jours est normalement eǵale à 2. Mais vous pouvez saisir un autre nombre en cochant le bouton à côté.")
    leave_days_manual_input = fields.Float("Nombre de jours à attribuer par mois", default=2.5, help="Le nombre de jours est normalement eǵale à 2. Mais vous pouvez saisir un autre nombre en cochant le bouton à côté.")
    leave_days = fields.Float(compute="_get_leave_days", method=True, string="Nombre de jours à attribuer par mois", help="Le nombre de jours est normalement eǵale à 2,5. Mais vous pouvez saisir un autre nombre en cochant le bouton à côté.")

    risk_bonus = fields.Float('Prime de risque', digits_compute=dp.get_precision('Payroll'))
    home_bonus = fields.Float('Prime de logement', digits_compute=dp.get_precision('Payroll'))
    cashpoint_bonus = fields.Float('Prime de caisse', digits_compute=dp.get_precision('Payroll'))
    expatriation_bonus = fields.Float("Prime d'expratriation", digits_compute=dp.get_precision('Payroll'))
    basket_bonus = fields.Float('Prime de panier', digits_compute=dp.get_precision('Payroll'))
    responsability_bonus = fields.Float('Prime de responsabilité', digits_compute=dp.get_precision('Payroll'))
    subjection_allowance = fields.Float('Indemnité de sujétion', digits_compute=dp.get_precision('Payroll'))

    food_advantage = fields.Float('Avantage pour nourriture', digits_compute=dp.get_precision('Payroll'))
    domesticity_bonus = fields.Float('Avantage pour logement et domesticité', digits_compute=dp.get_precision('Payroll'))
    family_advantage = fields.Float('Avantages familiaux', digits_compute=dp.get_precision('Payroll'))
    company_car_advantage = fields.Float('Avantage pour véhicule de fonction', digits_compute=dp.get_precision('Payroll'))
    company_phone_advantage = fields.Float('Avantage pour téléphone', digits_compute=dp.get_precision('Payroll'))
    water_electricity_advantage = fields.Float("Avantage pour fourniture d'eau et d'électricité", digits_compute=dp.get_precision('Payroll'))

    kilometer_refund = fields.Float('Indemnité kilométrique', digits_compute=dp.get_precision('Payroll'))
    transport_refund = fields.Float('Indemnité de transport', digits_compute=dp.get_precision('Payroll'))
    transport_refund_frequence = fields.Selection((('day', 'Jour'), ('month', 'Mois')), 'Frequence des indemnités de transport', required=True, default='month')
    meal_voucher = fields.Float('Bons de repas', digits_compute=dp.get_precision('Payroll'))
    meal_voucher_frequence = fields.Selection((('day', 'Jour'), ('month', 'Mois')), 'Frequence des bons de repas', required=True, default='month')

    mutual_insurance_empl_manual = fields.Boolean("Cotisation salariale", help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant ce bouton.")
    mutual_insurance_empl_manual_input = fields.Float("Cotisation salariale", digits_compute=dp.get_precision('Payroll'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    mutual_insurance_empl = fields.Float(compute="_get_mutual_insurance_empl", method=True, string="Cotisation salariale", digits_compute=dp.get_precision('Account'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")

    mutual_insurance_comp_manual = fields.Boolean("Cotisation patronale", help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant ce bouton.")
    mutual_insurance_comp_manual_input = fields.Float("Cotisation patronale", digits_compute=dp.get_precision('Payroll'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")
    mutual_insurance_comp = fields.Float(compute="_get_mutual_insurance_comp", method=True, string="Cotisation patronale", digits_compute=dp.get_precision('Account'), help="La cotisation à la mutuelle d'assurance est normalement calculée automatiquement. Mais vous pouvez la saisir manuellement en activant le bouton à côté.")

    dirtiness_allowance = fields.Float('Prime de salissure', digits_compute=dp.get_precision('Payroll'))
    journal_id = fields.Many2one(default=_get_default_journal)
    function_bonus = fields.Float('Prime de fonction', digits_compute=dp.get_precision('Payroll'))
    vehicle_bonus = fields.Float('Prime de véhicule',digits_compute=dp.get_precision('Payroll'))
    toy = fields.Float('Prime de jouets',digits_compute=dp.get_precision('Payroll'))
    bonus = fields.Float('Bonus',digits_compute=dp.get_precision('Payroll'))
    phone_bonus = fields.Float('Prime de téléphone',digits_compute=dp.get_precision('Payroll'))
    electricity = fields.Float('Prime électricité',digits_compute=dp.get_precision('Payroll'))
    schooling_bonus = fields.Float('Prime de scolarité',digits_compute=dp.get_precision('Payroll'))
    transport_bonus = fields.Float('Prime de transport imposable',digits_compute=dp.get_precision('Payroll'))
    transport = fields.Float('Prime de transport non imposable', digits_compute=dp.get_precision('Payroll'))
    ready_bib = fields.Float('Pret bib', digits_compute=dp.get_precision('Payroll'))
    ready_status_car = fields.Float('Pret status car', digits_compute=dp.get_precision('Payroll'))
    transfer_crrae = fields.Float('Reversement Crrae', digits_compute=dp.get_precision('Payroll'))

    _defaults = {
        'transport_refund_frequence': 'month',
        'transport_refund': 20800.0,
        #        'basket_bonus': 33500.0,
        'meal_voucher_frequence': 'month',
        #        'meal_voucher': 33500.0,
        'functionary': _default_governmental_org,
        'journal_id': _get_default_journal
    }

