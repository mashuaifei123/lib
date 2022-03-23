{
    'name': "Project_Bom",
    'summary': "Project and boms",
    'description': "just so so",
    'author': "",
    'website': "https://www.odoo.com/page/project",
    'category': 'Project BOM',
    'version': '14.0.1',
    'depends': ['base','contacts','resource'],
    # view和文件定义的action前后关系
    'data': [
            'security/groups.xml',
            
            'views/project_experiments.xml',
            'views/project.xml',
             'views/project_experiments_css.xml',
             'views/project_action.xml',
             #'views/project_requirement.xml',
             'report/project_report.xml',
             'report/project_templates.xml',
             'views/bom_line.xml',
             'views/templates.xml',
             #'views/my_message_wizard.xml'  
             ],

    'application': True,
}