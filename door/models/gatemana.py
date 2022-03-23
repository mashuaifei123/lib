
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pandas as pd
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
import os
import os.path


class SetRoom(models.Model):
    _name = 'setroom'
    _description = 'SetRoom'
    _rec_name = 'access_control_no'

    room_no = fields.Char('房间号', required=True)
    access_control_no = fields.Char('门禁编号', required=True)
    charge_person_id = fields.Many2one('hr.employee', string='责任人')


class MjRecords(models.Model):
    _name = 'mjrecords'
    _description = 'MjRecords'
    _rec_name = 'applicant_no'

    def _default_applicant(self):
        return self.env.user.employee_id

    applicant_id = fields.Many2one(
        'hr.employee', string='申请人', readonly=True,  default=_default_applicant, store=True)
    applicant_no = fields.Char(
        related='applicant_id.barcode', readonly=True, string='工号',)
    department_id = fields.Char(
        related='applicant_id.department_id.name',  readonly=True, string='所属部门')
    position_id = fields.Char(
        related='applicant_id.job_id.name',  readonly=True, string='职位')

    room_line_ids = fields.One2many(
        'mjrecords.line', 'mjrecord_id', 'MjRecords Lines', copy=True)

    def print_docx(self):
        self.ensure_one()
        room_list = [{'room_no': i.room_no,
                      'access_control_no': i.access_control_no,
                      'charge_person': i.charge_person_id.name
                      }
                     for i in self.room_line_ids.room_id]
        ref = {
            'applicant': self.applicant_id.name,
            'department': self.department_id,
            'job': self.position_id,
            'room_list': room_list
        }
        room_df = pd.DataFrame(room_list)
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "../out/ceshi1.xlsx")
        room_df.to_excel(path)
        return {''
                "type": "ir.actions.act_url",
                'target': 'self',
                'url': '/export_password_word?applicant=%s&department=%s&job=%s&mjrecords_id=%s' % (self.applicant_id.name, self.department_id, self.position_id, self.id),
                }


class MjRecordsLine(models.Model):
    _name = 'mjrecords.line'

    _description = 'MjRecords Line'
    _rec_name = "room_id"

    room_id = fields.Many2one('setroom', '房间号', required=True)
    access_control_no = fields.Char(
        related='room_id.room_no', string='门禁编号',  readonly=True)
    charge_person = fields.Char(
        related='room_id.charge_person_id.name', string='责任人',  readonly=True)
    mjrecord_id = fields.Many2one(
        'mjrecords', 'Records',
        index=True, ondelete='cascade', required=True)
