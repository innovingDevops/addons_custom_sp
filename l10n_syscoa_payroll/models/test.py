import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _order = 'id desc'

    cn_amount = fields.Float(compute='_amount_all',store=True)
    its_amount = fields.Float(compute='_amount_all',store=True)
    igr_amount = fields.Float(compute='_amount_all',store=True)
    cnps_amount = fields.Float(compute='_amount_all',store=True)
    ret_amount = fields.Float(compute='_amount_all',store=True)
    total_amount = fields.Float(compute='_amount_all',store=True)
    brut_amount = fields.Float(compute='_amount_all',
                               store=True)



    @api.multi
    def _amount_all(self):
        print "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
        for payslip in self:
            ret_amount = total_amount = cnps_amount = igr_amount = cn_amount = its_amount = 0.0
            for line in payslip.line_ids:
                if line.code == 'CN':
                   payslip.cn_amount = line.amount
                if line.code == 'ITS':
                  payslip.its_amount = line.amount
                if line.code == 'IGR':
                  payslip.igr_amount = line.amount
                if line.code == 'CNPS':
                  payslip.cnps_amount = line.amount
                if line.code == 'RET':
                   payslip.ret_amount = line.amount
                if line.code == 'NET':
                   payslip.total_amount = line.amount
                if line.code == 'BRUT':
                   payslip.brut_amount = line.amount
