# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
#from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ['purchase.order']
    _description = "Purchase Order"
    _order = 'date_order desc, id desc'


    note = fields.Text('Objet', copy=True)
    paid = fields.Boolean("Etat paiement", default=False)
    mandat_id = fields.Many2one('innoving.mandat',string="N° Mandat")
    
    
    @api.multi
    def button_draft(self):
        raise UserError(_("Impossible de poursuivre les traitements. Vous ne pouvez pas reutiliser un BC annulé!"))
        self.write({'state': 'draft'})
        return {}
