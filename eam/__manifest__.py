{
    'name': "eam",
    'summary': "Eam",
    'description': "just so so",
    'author': "",
    'website': "https://www.odoo.com/page/eam",
    'category': 'Order',
    'version': '14.0.1',
    'depends': ['base','contacts','resource', 'stock'],
    # view和文件定义的action前后关系
    'data': [
              'views/post_order.xml',
              'views/daily_data.xml',
             ],

    'application': True,
}