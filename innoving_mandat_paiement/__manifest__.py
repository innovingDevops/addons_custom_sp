# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Innoving Mandat de paiement',
    'version': '1.0',
    'summary': "Suivi des mandats de paiement",
    'sequence': 15,
    'autor':'INNOVING',
    'description': """
Enregistrement et suivi des mandats de paiement ...
====================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Human Resources, Purchase, Account',
    'website': 'https://www.innoving.info/',
    'images': [''],
    'depends': ['base_setup','base','purchase','account'],
    'data': [
        'security/group_security.xml',
        'security/ir.model.access.csv',
        'data/data_sequence.xml',
        'report/innoving_certificat_dotation_report.xml',
        'report/innoving_certificat_dotation_template.xml',
        'report/innoving_mandat_paiement_report.xml',
        'report/innoving_mandat_paiement_template.xml',
        'report/innoving_mandat_bordereau_report.xml',
        'report/innoving_mandat_bordereau_template.xml',
        'report/innoving_mandat_bordereau_ordre_recette_report.xml',
        'report/innoving_mandat_bordereau_ordre_recette_template.xml',
        'report/innoving_draft_mandat_paiement_report.xml',
        'report/innoving_draft_mandat_paiement_template.xml',
        'report/innoving_mandat_prelevement_report.xml',
        'report/innoving_mandat_prelevement_template.xml',
        'report/innoving_mandat_ordre_recette_report.xml',
        'report/innoving_mandat_ordre_recette_template.xml',
        #'report/innoving_mandat_paiement_report.xml',
        #'report/innoving_mandat_paiement_template.xml',
        #'report/innoving_mandat_bordereau_report.xml',
        #'report/innoving_mandat_bordereau_template.xml',
        #'report/innoving_mandat_bordereau_1_report.xml',
        #'report/innoving_mandat_bordereau_1_template.xml',
        #'views/innoving_mandat_report_view.xml',
        'views/innoving_mandat_wizard_view.xml',
        'views/innoving_mandat_view.xml',
        'views/purchase_views.xml',
        'views/account_invoice_view.xml',
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
