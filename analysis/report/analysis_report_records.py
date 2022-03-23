import json
from odoo import api, models, _
from odoo.tools import float_round
import pandas as pd
import numpy as np


class ReportRecords(models.AbstractModel):
    _name = 'report.analysis.ana_report_records'
    _description = 'Ana Report'


    @api.model  
    def _get_report_values(self, docids, data=None):
        ccc = docids
        lines =[]
        head_data=[]
        choose_id = self.env['ana.stock.picking.line'].browse(ccc[0])
        anticoagulant = choose_id.iacuc_no_id.anticoagulant_c.display_name
        available_date = choose_id.iacuc_no_id.validity_c
        head_data =[anticoagulant,available_date]
        for line_id in docids:
            line_obj = self.env['ana.stock.picking.line'].browse(line_id)
            line = {
            'iacuc_no_id': line_obj.iacuc_no_id.display_name,
            'prepared_by_1': line_obj.prepared_by_1.display_name,
            'prepared_date_1': line_obj.prepared_date_1,
            'aim_id_1': line_obj.aim_id_1.display_name,
            'ana_picking_type_id_1': line_obj.ana_picking_type_id_1.display_name,
            'use_quantity': line_obj.use_quantity,
            'verifield_by_1': line_obj.verifield_by_1.display_name,
            'verifield_date_1': line_obj.verifield_date_1,
            }   
            lines.append(line)
        #print(lines)
        return{
            'docs': lines,
            'head_data' :head_data
        }


       