import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path

from random import randrange
from PIL import Image


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    api_key = fields.Char(string='Api Key')
    secret_key = fields.Char(string='Secret Key')
    client_id = fields.Char(string='Client Id')


