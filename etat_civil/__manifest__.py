# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Etat Civil',
    'version': '1.0',
    'summary': "Enregistrement des actes civils (Naissance, Mariage, Décès, etc...)",
    'sequence': 15,
    'autor':'INNOVING',
    'description': """
Déclaration et enregistrement des naissances, mariages, décès, etc...
====================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'documents,project',
    'website': 'https://www.innoving.info/',
    'images': [''],
    'depends': ['base_setup','base'],
    'data': [
        'security/group_security.xml',
        'security/ir.model.access.csv',
        'data/data_registre.xml',
        'data/data_document.xml',
        'views/etat_civil_naissance_view.xml',
        'views/etat_civil_mariage_view.xml',
        'views/etat_civil_deces_view.xml',
        'views/etat_civil_registre_view.xml',
        'views/etat_civil_document_view.xml',
        'views/etat_civil_maire_view.xml',
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
