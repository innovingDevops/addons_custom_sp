#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
# from amount_to_text import amount_to_text 
# import amount_to_text_fr
# from . import amount_to_text_fr



to_19_fr = ( 'zéro',  'un',   'deux',  'trois', 'quatre',   'cinq',   'six',
          'sept', 'huit', 'neuf', 'dix',   'onze', 'douze', 'treize',
          'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf' )
tens_fr  = ( 'vingt', 'trente', 'quarante', 'Cinquante', 'Soixante', 'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
denom_fr = ( '',
          'Mille',     'Millions',         'Milliards',       'Billions',       'Quadrillions',
          'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
          'Décillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion' )

class PayslipDetailsReportSn(models.AbstractModel):
    _name = 'report.l10n_syscoa_payroll.report_payslip_sn'
    _description = 'Fiche de paye SENEGAL'
	
	

    def _convert_nn_fr(self,val):
        if val < 20:
            return to_19_fr[val]
		
        for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
            if dval + 10 > val:
                if val % 10:
                    return dcap + '-' + to_19_fr[val % 10]
                return dcap

    def _convert_nn_fr(self,val):
        if val < 20:
            return to_19_fr[val]
        elif val // 10 == 7 and val % 10 < 7:
            (mod, rem) = (val % 20, val // 10)
            word = tens_fr[rem-3] + '-' + to_19_fr[mod]
            return word
        elif val // 10 == 9 and val % 10 < 7:
            (mod, rem) = (val % 20, val // 10)
            word = tens_fr[rem-3] + '-' + to_19_fr[mod]
            return word
        else:
            for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
                if dval + 10 > val:
                    if val % 10:
                        return dcap + '-' + to_19_fr[val % 10]
                    return dcap
								
    def _convert_nnn_fr(self,val):
        word = ''
        (mod, rem) = (val % 100, val // 100)
        if rem > 0:
            word = to_19_fr[rem] + ' Cent'
            if mod > 0:
                word = word + ' '
        if rem ==1:
            word = ' Cent '	
        if mod > 0:
            word = word + self._convert_nn_fr(mod)
        return word

    def french_number(self,val):
        if val < 100:
            return self._convert_nn_fr(val)
        if val < 1000:
            return self._convert_nnn_fr(val)
        for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
            if dval > val:
                mod = 1000 ** didx
                l = val // mod
                r = val - (l * mod)
                ret = self._convert_nnn_fr(l) + ' ' + denom_fr[didx]
                if r > 0:
                    ret = ret + ', ' + self.french_number(r)
                return ret

    def amount_to_text_fr(self,number,currency):
        number = '%.2f' % number
        units_name = currency
        list = str(number).split('.')
        start_word = self.french_number(abs(int(list[0])))
        end_word = self.french_number(int(list[1]))
        cents_number = int(list[1])
        cents_name = (cents_number > 1) and '' or ''
        final_result = start_word +' '+units_name+' '+' '+cents_name
        return final_result.upper()
	

    def get_details_by_rule_category(self, payslip_lines):
        PayslipLine = self.env['hr.payslip.line']
        RuleCateg = self.env['hr.salary.rule.category']

        def get_recursive_parent(current_rule_category, rule_categories=None):
            if rule_categories:
                rule_categories = current_rule_category | rule_categories
            else:
                rule_categories = current_rule_category

            if current_rule_category.parent_id:
                return get_recursive_parent(current_rule_category.parent_id, rule_categories)
            else:
                return rule_categories

        res = {}
        result = {}

        if payslip_lines:
            self.env.cr.execute("""
                SELECT pl.id, pl.category_id, pl.slip_id FROM hr_payslip_line as pl
                LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id)
                WHERE pl.id in %s
                GROUP BY rc.parent_id, pl.sequence, pl.id, pl.category_id
                ORDER BY pl.sequence, rc.parent_id""",
                (tuple(payslip_lines.ids),))
            for x in self.env.cr.fetchall():
                result.setdefault(x[2], {})
                result[x[2]].setdefault(x[1], [])
                result[x[2]][x[1]].append(x[0])
            for payslip_id, lines_dict in result.items():
                res.setdefault(payslip_id, [])
                for rule_categ_id, line_ids in lines_dict.items():
                    rule_categories = RuleCateg.browse(rule_categ_id)
                    lines = PayslipLine.browse(line_ids)
                    level = 0
                    for parent in get_recursive_parent(rule_categories):
                        res[payslip_id].append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': sum(lines.mapped('total')),
                        })
                        level += 1
                    for line in lines:
                        res[payslip_id].append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level
                        })
        return res

    def get_lines_by_contribution_register(self, payslip_lines):
        result = {}
        res = {}
        for line in payslip_lines.filtered('register_id'):
            result.setdefault(line.slip_id.id, {})
            result[line.slip_id.id].setdefault(line.register_id, line)
            result[line.slip_id.id][line.register_id] |= line
        for payslip_id, lines_dict in result.items():
            res.setdefault(payslip_id, [])
            for register, lines in lines_dict.items():
                res[payslip_id].append({
                    'register_name': register.name,
                    'total': sum(lines.mapped('total')),
                })
                for line in lines:
                    res[payslip_id].append({
                        'name': line.name,
                        'code': line.code,
                        'quantity': line.quantity,
                        'amount': line.amount,
                        'total': line.total,
                    })
        return res

		
    def get_employer_line_rate(self, obj, rule):

       
        payslip_line=self.env['hr.payslip.line']
        line_ids =payslip_line.search([('slip_id', '=',obj.id),('salary_rule_id.parent_rule_id.id', '=', rule )])
        res=line_ids and payslip_line.browse(line_ids[0].id).rate or False
          
        return res	


    def get_employer_line_amount(self, obj, rule):

        payslip_line=self.env['hr.payslip.line']
        line_ids =payslip_line.search([('slip_id', '=',obj.id),('salary_rule_id.parent_rule_id.id', '=', rule )])
        res=line_ids and payslip_line.browse(line_ids[0].id).total or False
        total=float(res)
          
        return res	



	#afficher le total d'une categorie		
    def get_total_by_rule_category(self, obj, code):
        
        payslip_line=self.env['hr.payslip.line']
        rule_cate_obj=self.env['hr.salary.rule.category']

        cate_ids = rule_cate_obj.search([('code', '=', code)])
        category_total = 0.0
        if cate_ids:
            line_ids = payslip_line.search([('slip_id', '=', obj.id),('category_id.id', '=', cate_ids[0].id )])
            for l in line_ids:
                 category_total=category_total+l.total

        return category_total		
		
		
    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'data': data,
            'get_details_by_rule_category': self.get_details_by_rule_category(payslips.mapped('details_by_salary_rule_category').filtered(lambda r: r.appears_on_payslip)),
            'get_lines_by_contribution_register': self.get_lines_by_contribution_register(payslips.mapped('line_ids').filtered(lambda r: r.appears_on_payslip)),
            'get_employer_line_rate': self.get_employer_line_rate,
            'get_employer_line_amount': self.get_employer_line_amount,
            'get_total_by_rule_category': self.get_total_by_rule_category,
            'amount_to_text_fr': self.amount_to_text_fr,
        }
