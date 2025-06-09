# -*- coding: utf-8 -*-
# All Rights Reserved

{
    'name': "Sky Jumper CRM",
    'description': """
        Manage Leads
    """,
    'author': 'Mukesh Kumar - TCB Infotech',
    'website': '',
    'category': 'Leads Management',
    'version': "0.0.1",
    'depends': ['base','crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/lead_type_data.xml',
        'data/city_data.xml',
        'views/crm_lead_inherit_views.xml'
        ],
    'assets': {
        'web.assets_backend': [],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}