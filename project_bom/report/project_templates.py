import json
from odoo import api, models, _
from odoo.tools import float_round
import pandas as pd
import numpy as np


class Report01(models.AbstractModel):
    _name = 'report.project_bom.project_templates'
    _description = 'Report'

    def _get_lines_data(self,id):
        self.env.cr.execute ("""SELECT hd.name as apartment,
                                        pa.actname as project_actions_name,
                                        pbl.date_set as date_set,
                                        pt.name as product_template_name,
                                        pblc.product_qty as project_bom_line_product_qty,
                                        pt.list_price as product_template_list_price

                                        FROM project_studynumber as ps
                                        left join project_experiment as pe on ps.id = pe.studyname_id
                                        left join hr_department as hd on pe.department_id = hd.id
                                        left join project_bom_line as pbl on pe.id = pbl.bom_id
                                        left join project_actions as pa on pbl.action_id = pa.id
                                        left join project_bom_line_child as pblc on pbl.id = pblc.action_id_id
                                        left join product_template as pt on pblc.product_id = pt.id
	                                     where ps.id = %s"""% id)
        return self.env.cr.dictfetchall()
    

    def _add_judge_data(self,data_set):
        """
        部门A 解剖 2020-05-11 AG 2.0 1.0 1 
                             AE 4.0 1.0 4 
                  2020-05-13 AG 2.0 1.0 3 
                             AE 4.0 1.0 4 
                  2020-05-14 AG 2.0 1.0 3 
                             AE 4.0 1.0 4 
                  2020-05-15 AG 2.0 1.0 3 
                             AE 4.0 1.0 4 
             采血 2020-05-11 AD 6.0 2.0 2   
        """
        df = pd.DataFrame(data_set)
        df['days'] = df['date_set'].map(lambda x: int(x.count(',')+1))
        df['project_bom_line_product_qty'] = df['project_bom_line_product_qty']/df['days']
        df.drop('days', inplace=True,axis=1 )
        df=  df['date_set'].str.split(",", expand =True).stack().reset_index(level = 0).set_index('level_0').rename(columns ={0:'date'}).join(df.drop('date_set',axis =1 ))
        df = df[['apartment','project_actions_name', 'date','product_template_name', 'project_bom_line_product_qty','product_template_list_price']]
        df = df.sort_values(['apartment','project_actions_name','date'])
        apartment = [list(df['apartment'])[0]]
        project_actions_name=[list(df['project_actions_name'])[0]]
        data =[list(df['date'])[0]]
        for i in range(df.shape[0]-1):
            if list(df['apartment'])[i+1]!= list(df['apartment'])[i]:
                apartment.append(list(df['apartment'])[i+1])
            else:
                apartment.append(np.nan)
            if list(df['project_actions_name'])[i+1]!= list(df['project_actions_name'])[i]:
                project_actions_name.append(list(df['project_actions_name'])[i+1])
            else:
                project_actions_name.append(np.nan)
            if list(df['date'])[i+1]!= list(df['date'])[i]:
                data.append(list(df['date'])[i+1])
            else:
                data.append(np.nan)
        df['apartment'] = apartment
        df['project_actions_name'] = project_actions_name
        df['date'] = data
        df['level'] = [7-i for i in df.count(axis=1)]
        df = df.fillna('')

        return df.to_dict('records')


    def print_data(self,para):
        sum = 0
        for pd in para:
            pd['line_total'] = pd['project_bom_line_product_qty'] *pd['product_template_list_price']
            sum += pd['line_total']
        data =  [para,sum,'pdf',{"currency" :self.env['res.currency'].browse([7])}]
        return data


    @api.model  
    def _get_report_values(self, docids, data=None):
        ccc = docids

        #docids 列表 如[1]
        head_data_dict = self.env['project.studynumber'].browse([docids[0]]) #模型对象
        studynumber_id = head_data_dict.id #int
        data  = self._get_lines_data(studynumber_id)
        data1 = self._add_judge_data(data)
  
        return{
            'head_data':head_data_dict,
            'lines_data': self.print_data(data1),
             
        }







    def _get_data2(self,id):
        lines = []
        object_studynumber = self.env['project.studynumber'].browse(id)
        object_experience = object_studynumber.excperiment_ids
        object_bomlines = object_experience.bom_line_ids
        object_action = object_bomlines.action_id
        object_product = object_bomlines.product_id

        bomlineids = object_bomlines.ids # list [6,7,8,9]
        for bomline_id in bomlineids:
            line = {

            }

        print('c')



       