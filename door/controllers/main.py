
from odoo import http
from odoo.http import request
import base64
from odoo.http import content_disposition, Controller, request, route
import os
import os.path
from io import BytesIO
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
import os
import io


class ExportPasswordWord(http.Controller):

    @http.route('/export_password_word', auth='user', type='http')
    def export_password_pdf(self, **data):

        mjrecords = request.env['mjrecords'].sudo().search(
            [('id', '=', data['mjrecords_id'])])
        room_list = [{'room_no': i.room_no,
                      'access_control_no': i.access_control_no,
                      'charge_person': i.charge_person_id.name
                      }
                     for i in mjrecords.room_line_ids.room_id]
        my_path = os.path.abspath(os.path.dirname(__file__))
        word_template_path = os.path.join(
            my_path, r'BTC-COM-0005-2.0 门禁使用申请表 2.0 2022-01-21生效.docx')  # word模板路径
        docx = Document(word_template_path)
        dt0 = docx.tables[0]
        ''' word 写入 位置信息 '''
        Word_Table_applicant = (0, 6)  # 申请人
        Word_Table_department = (0, 9)  # 所属部门
        Word_Table_job = (0, 14)  # 职位
        # 房间写入(4,0)(4,1),(4,2)开始 到41
        # 第二列(4,4)(4,5)(4,6)到39 判断房间数写入
        table_header_list = [data['applicant'], data['department'], data['job']]
        for a, b in zip([Word_Table_applicant, Word_Table_department, Word_Table_job], table_header_list):  # 获取列数据写入word_table0
            dt0.cell(*a).text = str(b)

        if 35<len(room_list)<68:
            room_list_2 = room_list[35:]
            room_list = room_list[:35]
        
        for a, b in zip([(i+4, 1)for i in range(len(room_list))], [i['room_no'] for i in room_list]):
            dt0.cell(*a).text = str(b)
        for a, b in zip([(i+4, 2)for i in range(len(room_list))], [i['access_control_no'] for i in room_list]):
            dt0.cell(*a).text = str(b)
        for a, b in zip([(i+4, 3)for i in range(len(room_list))], [i['charge_person'] for i in room_list]):
            dt0.cell(*a).text = str(b)
        #docx.save(r'C:\asda.docx')

        fp = io.BytesIO()
        docx.save(fp)
        fp.seek(0)
        data = fp.read()
        # print(data)
        fp.close()


        filename = '测试.docx'
        httpheaders = [('Content-Type', 'application/docx'), ('Content-Length', len(
            data)), ('Content-Disposition', content_disposition(filename))]
        return request.make_response(data, headers=httpheaders)
