import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np



class EquState(models.Model):
    _name = 'equstate'
    _description = 'EquState'
    _rec_name = 'state'

    state = fields.Char('状态', required=True)

class EquSort(models.Model):
    _name = 'equsort'
    _description = 'EquSort'
    _rec_name = 'sort'

    sort = fields.Char('类别', required=True)


class EquPlace(models.Model):
    _name = 'equplace'
    _description = 'EquPlace'
    _rec_name = 'storeplace'

    storeplace = fields.Char('地点', required=True)


class EquManufacturer(models.Model):
    _name = 'equmanufacturer'
    _description = 'EquManufacturer'
    _rec_name = 'manufacturer'

    manufacturer = fields.Char('制造厂商', required=True)
    phone = fields.Char('厂商电话')

class EquCompany(models.Model):
    _name = 'equcompany'
    _description = 'EquCompany'
    _rec_name = 'Company'

    Company = fields.Char('验证单位', required=True)

class EquMeasure(models.Model):
    _name = 'equmeasure'
    _description = 'EquMeasure'
    _rec_name = 'frequency'

    frequency = fields.Char('计量频率', required=True)

class EquReview(models.Model):
    _name = 'equreview'
    _description = 'EquReview'
    _rec_name = 'review_frequency'

    review_frequency = fields.Char('回顾频率', required=True)

class EquPdfMark(models.Model):
    _name = 'equpdfmark'
    _description = 'EquPdfMark'
    _rec_name = 'mark'

    mark  = fields.Binary('PDF')