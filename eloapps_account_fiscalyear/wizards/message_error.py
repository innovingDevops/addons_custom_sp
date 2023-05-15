# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from openerp.exceptions import ValidationError,Warning

import logging

class MessageError(models.TransientModel):
    _name = 'message.error'

    body = fields.Char()