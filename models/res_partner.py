from .shopify_api import Customer, Address
from odoo import models, fields, api, _


def get_basic_shopify_customer_mapping():
    mapping = dict(
        first_name='first_name',
        last_name='last_name',
        email='email',
    )
    return mapping


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shopify_customer_id = fields.Integer(default=0)
    shopify_address_id = fields.Integer(default=0)
    first_name = fields.Char()
    last_name = fields.Char()


class CustomerResCompany(models.Model):
    _inherit = 'res.company'

    def create_partner(self):
        customer_obj = self.get_customer_or_address_instance()
        print("Customer_obj: ",customer_obj)
        if not customer_obj:
            return
        customer_list = customer_obj.get_customer_list()
        print("customer_list: ", customer_list)
        for customer in customer_list:
            mapping = get_basic_shopify_customer_mapping()
            customer_dict = {}
            for k, v in mapping.items():
                customer_dict[v] = customer.get(k)

            name = customer.get('first_name') + " " + customer.get('last_name')
            customer_dict['name'] = name
            customer_dict['company_type'] = 'person'
            customer_dict['type'] = False
            existing_partner = self.get_existing_partner(customer.get('id'))
            if existing_partner:
                existing_partner.write(customer_dict)
            else:
                customer_dict['shopify_customer_id'] = customer.get('id')

                self.env['res.partner'].create(customer_dict)
        del customer_obj

    def get_existing_partner(self, customer_id):
        partner = self.env['res.partner'].search([('shopify_customer_id', '=', customer_id)], limit=1)
        if partner:
            return partner
        return False

    def create_address(self):
        address_obj = self.get_customer_or_address_instance(address=True)
        if not address_obj:
            return
        address_list = address_obj.get_address_list()
        address_type = self.default_address_type
        for address in address_list:
            customer = self.env['res.partner'].search([('shopify_customer_id', '=', address.get('customer_id'))],
                                                      limit=1)
            if not customer:
                continue
            data = dict(
                street=address.get('address1', ''),
                street2=address.get('address2', ''),
                city=address.get('city', ''),
                country_id=self.get_country_id(address.get('country_code')),
                state_id=self.get_state_id(address.get('state_or_province')),
                zip=address.get('postal_code', ''),
                phone=address.get('postal_code'),
            )
            existing_address = self.env['res.partner'].search([('shopify_address_id', '=', address.get('id'))],
                                                              limit=1)
            if existing_address:
                del data['shopify_address_id']
                del data['type']
                existing_address.update(data)

            else:
                customer.write({
                    'child_ids': [(0, 0, data)]
                })
        del address_obj

    def get_country_id(self, country_code):
        if country_code:
            country_obj = self.env['res.country'].search([('code', '=', country_code)], limit=1)
            if country_obj:
                return country_obj.id

        return False

    def get_state_id(self, state):
        if state:
            state_obj = self.env['res.country.state'].search([('name', '=', state.strip())], limit=1)
            if state_obj:
                return state_obj.id
        return False

    def get_customer_or_address_instance(self, address=False):
        api_data = self.get_api_data()
        # client_secret = self.shopify_client_id
        if address:
            address_obj = Address(*api_data)
            return address_obj
        customer = Customer(*api_data)
        print("customer: ",customer)
        return customer
