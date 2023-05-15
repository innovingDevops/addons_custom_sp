# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Website(models.Model):
    _inherit = 'website'

    captcha_sitekey = fields.Char()
    captcha_secretkey = fields.Char()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    captcha_sitekey = fields.Char(
        string="Recaptcha Site Key",
        related='website_id.captcha_sitekey',
        readonly=False,
    )
    captcha_secretkey = fields.Char(
        string="Recaptcha Secret Key",
        related='website_id.captcha_secretkey',
        readonly=False,
    )