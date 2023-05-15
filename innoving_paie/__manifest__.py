# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Innoving paie',
    'version': '1.0',
    'summary': "Suivie de la paie",
    'sequence': 15,
    'autor':'INNOVING',
    'description': """
Suivie de la paies ...
====================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'documents,project',
    'website': 'https://www.innoving.info/',
    'images': [''],
    'depends': ['base_setup','base','hr_payroll','hr','account'],
    'data': [
        'security/group_security.xml',
        'security/ir.model.access.csv',
        'data/data_hr_grade.xml',
        'data/data_hr_echelon.xml',
        'data/data_sequence.xml',
        'report/innoving_paie_bordereau_report.xml',
        'report/innoving_paie_bordereau_template.xml',
        'report/innoving_paie_bordereau_retenue_report.xml',
        'report/innoving_paie_bordereau_retenue_template.xml',
        'report/innoving_paie_etat_solde_report.xml',
        'report/innoving_paie_etat_solde_template.xml',
        'report/innoving_paie_single_etat_solde_report.xml',
        'report/innoving_paie_single_etat_solde_template.xml',
        'report/innoving_paie_etat_virement_report.xml',
        'report/innoving_paie_etat_virement_template.xml',
        'report/innoving_paie_etat_retenue_report.xml',
        'report/innoving_paie_etat_retenue_template.xml',
        'report/innoving_paie_mandat_retenue_report.xml',
        'report/innoving_paie_mandat_retenue_template.xml',
        'report/innoving_paie_mandat_salaire_report.xml',
        'report/innoving_paie_mandat_salaire_template.xml',
        'report/innoving_paie_single_mandat_salaire_report.xml',
        'report/innoving_paie_single_mandat_salaire_template.xml',
        'report/innoving_paie_etat_virement_retenue_report.xml',
        'report/innoving_paie_etat_virement_retenue_template.xml',
        'wizard/innoving_paie_etat_solde_wizard.xml',
        'wizard/innoving_paie_etat_retenue_wizard.xml',
        'wizard/innoving_paie_etat_virement_wizard.xml',
        'wizard/innoving_paie_mandat_retenue_wizard.xml',
        'wizard/innoving_paie_mandat_salaire_wizard.xml',
        'wizard/innoving_paie_etat_virement_retenue_wizard.xml',
        'wizard/innoving_paie_bordereau_retenue_wizard.xml',
        'views/hr_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/menu_view.xml',
    ],
    'demo': [
        
    ],
    'js': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    # 'post_init_hook': '_auto_install_l10n',
}
