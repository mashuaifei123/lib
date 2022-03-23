{
    'name': "Equ",
    'summary': "Equ",
    'description': "just so so",
    'author': "",
    'website': "https://www.odoo.com/page/equ",
    'category': 'Equ',
    'version': '14.0.1',
    'depends': ['base', 'contacts', 'resource'],
    # view和文件定义的action前后关系
    'data': ['security/groups.xml',
             'security/ir.model.access.csv',
              'views/equ_setting.xml',
              'views/equ_base.xml',
             'views/equ_lines.xml'
             ],

    'application': True,
}
