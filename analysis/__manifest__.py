{
    'name': "Analysis",
    'summary': "Analysis",
    'description': "just so so",
    'author': "",
    'website': "https://www.odoo.com/page/analysis",
    'category': 'Analysis',
    'version': '14.0.1',
    'depends': ['base','contacts','resource'],
    # view和文件定义的action前后关系
    'data': [  'security/groups.xml',
               'views/analysis_settings.xml',
               'views/base_settings.xml',
               'views/analysis_stock.xml',
               'views/my_web_assent.xml',
               'views/analysis_move.xml',
               'views/analysis_move_line.xml',
               'data/analysis_state.xml',
               'report/report_paperformat_ana_2612.xml',
               'report/report_paperformat_ana_records.xml',
               'report/analysis_report_ana_sample.xml',
               'report/analysis_Report_Sample.xml',
               'report/analysis_report_records.xml',
               'views/add_button.xml'
             ],
    # 'qweb':[
    #        'static/src/xml/tree_button.xml'],
    'application': True,
}