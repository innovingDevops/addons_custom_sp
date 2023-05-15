# -*- coding: utf-8 -*-
# ©  2015 ERGOBIT Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    legal_holidays_status_id_n1 = fields.Many2one('hr.leave.type', 'Legal Leave Status N-1', )
    legal_holidays_status_id_n2 = fields.Many2one('hr.leave.type', 'Legal Leave Status N-2', )
    number_cnps = fields.Char('Numéro CNPS')
    governmental_org = fields.Boolean('Organisme gouvernemental')
    conv_coll_national = fields.Char('Convention Collective Nationale')
    css_percentage = fields.Selection((('one', '1,0%'), ('three', '3,0%'), ('five', '5,0%')), required=True, default="three", string="CSS - Accident de travail")
    waste_collection_company = fields.Boolean("Entrep. de collecte d'ordure")
	

