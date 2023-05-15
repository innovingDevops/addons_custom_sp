# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class create_book_payslip(models.TransientModel):
    _name = 'create.book.payslip'
    _description = 'Generer un livre de paie'

    date_start = fields.Date('Du', required=True)
    date_end = fields.Date('Au', required=True)
   
    

    @api.multi
    def create_book(self):
        book_obj = self.env['book.report']
        book_line = []

        if self.date_start and self.date_end :
            para=[('date_from','>=',self.date_start),('date_to','<=',self.date_end)]
            liste=book_obj.search(para)
            for l in liste:
                book_line.append(l.id)
        return { 'domain': "[('id','in', ["+','.join(map(str, book_line))+"])]", 'view_type': 'form',"view_mode": 'pivot,tree','res_model': 'book.report','type': 'ir.actions.act_window',}
