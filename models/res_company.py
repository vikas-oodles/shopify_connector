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

    shopify_api_key = fields.Char(string='Shopify Api Key')
    shopify_secret_key = fields.Char(string='Shopify Password')
    shopify_client_id = fields.Char(string='Shopify Client Id')
    shopify_access_token = fields.Char(string='Shopify Access Token')
    default_location_id = fields.Many2one(
        'stock.location', string='Locations', check_company=True,
        domain=[('company_id', '=', id), ('usage', 'in', ['internal', 'transit'])]
    )
    default_address_type = fields.Selection(
        [('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
         ("private", "Private Address"),
         ], string='Default Address Type', default='invoice',
        help='Default address type created for Shopify user'
    )
    shopify_default_lead_time = fields.Float(default='1.0', help='Default Lead time for sale order')
    default_sales_person = fields.Many2one('res.users', string='Salesperson',
                                           domain=lambda self: [
                                               ('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)])
