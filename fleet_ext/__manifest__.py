# -*- coding: utf-8 -*-
# @2017, code write by Stella Fredo in Sweden, based on Fleet Management module from Odoo V12.
{
    'name' : 'Fleet Management extension',
    'version' : '12',
    'author': '',
    'sequence': 166,
    'category': 'Human Resources',
    'website' : '',
    'summary' : 'Vehicle, leasing, insurances, costs',
    'description' : """
Vehicle, leasing, insurances, cost extension
==================================
You need to install the odoo fleet module first, then this module 
add bit more functions on the fleet management module from odoo V10.

Main Features changed
-------------
* vehicle id is license plate and then model id, and then model brand.
* rewrite the fleet.vehicle.form, add notebook and page to the vehicle form
* the user has right to read, not edit, not delete on all vehicles information
* add color selection, and fuel type is reuqired.
* add checking if vin_sn number is unique
""",
    'depends': [
        'fleet',
    ],
    'data': [
        'security/fleet_security.xml',
        'views/fleet_view.xml',
    ],

    'installable': True,
}
