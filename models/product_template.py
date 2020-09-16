from odoo import models, fields, api, _
from .shopify_api import Product


def get_basic_shopify_product_mapping():
    mapping = {
        'title': 'name',
        'body_html': 'description_sale',
        'price': 'list_price',
        'sku': 'qty_available',


    }
    return mapping


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_product_id = fields.Char(default='')
    sync_with_shopify = fields.Boolean(string='Enable Shopify Sync', default=True)

    @api.model
    def create(self, vals):
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
        print(data)
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
            # if k == 'variants':
            #     if inventory_tracking == 'product' and self.env.company.sync_stock_odoo_shopify:
            #         data[k]['sku'] = int(product_obj.qty_available)
            #     continue
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
        data = {'shopify_product_id': product.get('id')}
        return data, initialize_inventory

    def create_product(self):
        product_obj = self.get_product_instance()
        print("product: ", product_obj)
        if not product_obj:
            return
        product_list = product_obj.get_products_list()
        print(product_list)
        for product in product_list:
            if not self.check_existing_product(product.get('id')):
                mapping = get_basic_shopify_product_mapping()
                product_dict = {}

                for k, v in mapping.items():
                    if k != 'inventory_quantity':
                        # if product.get(k) == 'variants':
                        #     print("product.get(k): ", product.get(k))
                        #     for a, b in product.get(k):
                        #         product_dict[v] = product.get(k)[v]

                        # if k == 'variants':
                        #     print("mapping[k]:", mapping[k])
                        #     for a, b in mapping[k].items():
                        #         # 'sku': 'pricelist_item_count'
                        #         print("product_dict[k][b]: ", product_dict[k][b])
                        #         print("product.get(k)[0].get(a): ", product.get(k)[0].get(a))
                        #         product_dict[k][b] = product.get(k)[0].get(a)
                        if k == 'price':
                            print(product.get('variants')[0])
                            price = product.get('variants')[0]['price']
                            product_dict[v] = price
                        elif k == 'sku':
                            sku = product.get('variants')[0]['sku']
                            product_dict[v] = float(sku)
                        else:
                            product_dict[v] = product.get(k)
                        # product_dict[v] = product.get(k)

                        print(product_dict)  # only to check
                        print(product)  # only to check

                additional_data, initialize_inventory = self.get_product_additional_data(product)
                product_dict.update(additional_data)
                print(product_dict)  # only to check
                obj = self.env['product.template'].create(product_dict)
        del product_obj

    def get_product_instance(self):
        api_data = self.get_api_data()
        print("Api_data: ", api_data)
        product = Product(*api_data)
        print("Product: ", product)
        return product

    def check_existing_product(self, product_id: int):
        products = self.env['product.template'].search_count([('shopify_product_id', '=', product_id)])
        if products > 0:
            return True
        return False
