# -*- coding: utf-8 -*-
{
    "name": "EHCS Login Captcha",
    'summary': """
        Add reCAPTCHA in your login page.""",
    'description': """
        CAPTCHA stands for Completely Automated Public Turing Test to Tell Computers and Humans Apart. 
        Its goal is to check if a user is a real person or a bot.
    """,
    'author': "ERP Harbor Consulting Services",
    'website': "http://www.erpharbor.com",
    'version': '12.0.1.0.0',
    "category": "Website",
    'depends': ['website', 'auth_signup'],
    "data": [
        'views/website_config_settings.xml',
        'views/login_templates.xml',
    ],
}
