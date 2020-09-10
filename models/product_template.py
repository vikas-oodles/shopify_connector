from odoo import models, fields, api, _
from .shopify_api import Product


def get_basic_shopify_product_mapping():
    mapping = {
        'title': 'name',
        'description': 'description_sale',
        'price': 'standard_price',
        'sku': 'default_code',
        'weight': 'weight',
        'inventory_quantity': 'qty_available',

    }
    return mapping


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_product_id = fields.Integer(default=0)
    sync_with_shopify = fields.Boolean(string='Enable Shopify Sync', default=True)

    @api.model
    def create(self,vals):
        obj = super(ProductTemplate, self).create(vals)
        if obj.shopify_product_id == 0 and obj.sync_with_shopify:
            self.create_shopify_product(obj)
        return obj

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for obj in self:
            if obj.sync_with_shopify:
                self.update_shopify_product(obj)
        return res

    def update_shopify_product(self, product_obj):
        obj = self.env.company.get_product_instance()
        if not obj:
            return
        data = self.get_product_data(product_obj)
        obj.update_product(product_obj.shopify_product_id, data)

    def create_shopify_product(self, product_obj):
        if not self.env.company.auto_create_product:
            return
        obj = self.env.company.get_product_instance()
        if not obj:
            return
        data = self.get_product_data(product_obj)
        res = obj.create_product(data)
        if res:
            product_obj.update({
                'shopify_product_id': res.get('id')
            })

    def get_product_data(self, product_obj):
        mapping = get_basic_shopify_product_mapping()
        data = {}
        inventory_tracking = 'product'
        if product_obj.type != 'product':
            inventory_tracking = 'none'
        for k, v in mapping.items():
            if k == 'inventory_quantity':
                if inventory_tracking == 'product' and self.env.company.sync_stock_odoo_shopify:
                    data[k] = int(product_obj.qty_available)
                continue
            data[k] = eval('product_obj.{}'.format(v))
        return data


class ProductResCompany(models.Model):
    _inherit = 'res.company'

    def get_product_additional_data(self, product):
        product_type = 'service'
        initialize_inventory = False

        if product.get('inventory_tracking') != 'none':
            product_type = 'product'
            initialize_inventory = True




