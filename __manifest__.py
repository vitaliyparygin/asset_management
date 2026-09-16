# -*- coding: utf-8 -*-
{
    'name': 'Asset Management - Equipment Issue Tracking',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track company equipment (laptops, phones, tools) issued to employees, '
               'with full issue/return history and a printable issue act.',
    
    'author': 'vitaliy.parygin',
    'website': 'https://taf-ua.com/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'wizard/asset_issue_wizard_views.xml',
        'views/asset_type_views.xml',
        'views/asset_search_views.xml',
        'views/asset_views.xml',
        'views/asset_issue_views.xml',
        'views/asset_menus.xml',
        'report/asset_issue_report.xml',
        'report/asset_issue_report_templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
