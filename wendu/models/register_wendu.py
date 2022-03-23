import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np

class Wendu(models.Model):
    _name = 'wendu'
    _description = 'Wendu'
    _rec_name = 'person_name'

    def _default_register(self):
        return self.env.user.employee_id

    person_name =fields.Many2one('hr.employee', '姓名', readonly=True, default=_default_register)
    temperature = fields.Float('体温℃',required=True)

    @api.constrains('temperature')
    def _check_release_date(self):
        for record in self:
            if  not (35 < record.temperature < 37.5)  :
                raise models.ValidationError('体温必须小于37.5℃，大于35℃')




