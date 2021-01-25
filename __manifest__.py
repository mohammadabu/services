# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Managed Services',
    'depends': [
        'analytic',
        'base_setup',
        'mail',
        'portal',
        'rating',
        'resource',
        'web',
        'web_tour',
        'digest',
    ],
    'description': "",
    'data': [
        'security/services_security.xml',
        'security/ir.model.access.csv',
        'report/services_report_views.xml',
        'views/analytic_views.xml',
        'views/digest_views.xml',
        'views/rating_views.xml',
        'views/services_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/mail_activity_views.xml',
        'views/services_assets.xml',
        'views/services_portal_templates.xml',
        'views/services_rating_templates.xml',
        'data/digest_data.xml',
        'data/services_mail_template_data.xml',
        'data/services_data.xml',
    ],
    'test': [
    ],
}
