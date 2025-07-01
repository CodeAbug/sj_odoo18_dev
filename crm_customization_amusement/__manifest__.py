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
    'depends': ['base','crm','sale_crm','crm_sms','crm_iap_enrich'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        
        'data/lead_type_data.xml',
        'data/city_data.xml',
        'data/school_type_data.xml',
        'data/designation_data.xml',
        # 'data/package_info_data.xml',
        'reports/trip_report.xml',
        
        'views/city_view.xml',
        'views/lead_type_views.xml',
        'views/school_type_views.xml',
        'views/stakeholder_designation_views.xml',
        'views/crm_lead_inherit_view.xml',
        'views/res_partner_inherit_view.xml',
        'views/opportunity_trip_views.xml',
        'views/crm_stage_view_inherit.xml',
        'views/sale_order_view_inherit.xml',
        'views/crm_lead_inherited_views_inherit.xml',
        
        
        
        
        ],
    'assets': {
        'web.assets_backend': [
            # 'crm_customization_amusement/static/src/js/custom_save.js',
            #                     'crm_customization_amusement/static/src/xml/enable_edit_button.xml'
                                ],
        
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}