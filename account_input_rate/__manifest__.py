# -*- coding: utf-8 -*-q
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Input Rate Manually',
    'version': '10.1',
    'category': 'Accounting',
    'summary': 'Manually input currency rate on Invoice and Payment',
    'description': """
    """,
    'author': 'Joenan <joenannr@gmail.com>',
    'depends': ['account_accountant'],
    'data': [
        'views/invoice_views.xml',
        'views/payment_views.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
