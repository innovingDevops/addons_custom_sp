# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': "Fiscal year and periods",
    'version': '12.0.1.2',
    'category': 'Accounting/Accounting',
    "license": "OPL-1",
    'author': 'Elosys',
    'website': 'https://www.elosys.net',
    'support'     : "support@elosys.net",
    "price": 50,
    "currency": 'EUR',
    'live_test_url': "https://www.elosys.net/shop/exercice-fiscale-et-periodes-29?category=6#attr=48",
    "contributors": [
        "1 <Kamel BENCHEHIDA>",
        "2 <Nassim REFES>",
        "3 <Mohamed Ould Miloud>",
        "4 <Fatima MESSADI",
    ],
    'depends': [
            'base',
            'account',
    ],
    'data': [
        'views/periode.xml',
        'views/exercice.xml',
        'views/account_move.xml',

        'wizards/close_periode.xml',
        'wizards/message_error.xml',
        'wizards/generer_ecriture.xml',
        'wizards/lettrer_ecriture.xml',
        'wizards/annuler_ecriture.xml',
        'wizards/fermer_exercice.xml',
        'wizards/generer_exercice.xml',

        'security/ir.model.access.csv',

        'data/cron_remplir_periode.xml',
    ],
    'images': ['images/baneer.gif'],
    'installable': True,
    'auto_install': False,
    "application": True,
}
