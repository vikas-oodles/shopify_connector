{
    'name': 'Shopify Connector',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Module for serial or lot creation',
    'sequence': '55',
    'author': 'vikas kumar',
    'maintainer': 'odoo mates',
    'website': 'odoomate.com',
    'depends': ["base", "sale_management", "stock", "account", "mail", "sale", "purchase", 'mrp'],
    'demo': [],
    'data': [
        'views/res_company.xml',
    ],
    'installable': True,
    'application': True,
    'auto-install': False,

}