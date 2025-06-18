# -*- coding: utf-8 -*-
# All Rights Reserved

{
    'name': "Crm Customizations For Amusement Park",
    'description': """
        Manage Leads
    """,
    'author': 'Mukesh Kumar',
    'website': '',
    'category': 'Leads Management',
    'version': "0.0.1",
    'depends': ['base','crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        
        'data/lead_type_data.xml',
        'data/city_data.xml',
        'data/school_type_data.xml',
        'data/designation_data.xml',
        'data/package_info_data.xml',
        
        'views/city_view.xml',
        'views/lead_type_views.xml',
        'views/school_type_views.xml',
        'views/stakeholder_designation_views.xml',
        'views/crm_lead_inherit_view.xml',
        'views/res_partner_inherit_view.xml',
        'views/opportunity_trip_views.xml',
        ],
    'assets': {
        'web.assets_backend': [],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}