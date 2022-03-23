import datetime
from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np


class EquRecord(models.Model):
    _name = 'equrecord'
    _description = 'EquRecord'
    _rec_name = 'registerid'

    state_id = fields.Many2one('equstate', string='状态')
    registerid = fields.Char('编号', required=True)
    registername = fields.Char('名称', required=True)
    registeredition = fields.Char('型号版本', required=True)
    attribute_sort = fields.Selection(
        [('仪器设备', '仪器设备'),
         ('计算机化系统', '计算机化系统'),
         ('办公软件', '办公软件')],
        '属性分类',)
    
    manufacturer_id = fields.Many2one('equmanufacturer', string='制造厂商')
    factorynumber = fields.Char('出厂编号')
    manufacturerphone= fields.Char('厂商联系电话', related='manufacturer_id.phone')
    range_parameters = fields.Char('量程技术参数')
    accuracy_level = fields.Char('准确度等级')
    sopnumber = fields.Char('sop编号')

    equ_check_ids = fields.One2many(
        'equcheck.line', 'equcheck_id', '新验收记录')
    equ_measure_ids = fields.One2many(
        'equmeasure.line', 'equmeasure_id', '新计量记录')
    equ_verification_ids = fields.One2many(
        'equverification.line', 'equverification_id', '新验证记录')
    equ_stoporstart_ids = fields.One2many(
        'equstoporstart.line', 'equstoporstart_id', '新停启记录')
    equ_transfer_ids = fields.One2many(
        'equtransfer.line', 'equtransfer_id', '新移交记录')
    equ_repair_ids = fields.One2many(
        'equrepair.line', 'equrepair_id', '新维修记录')
    equ_scrap_ids = fields.One2many(
        'equscrap.line', 'equscrap_id', '新报废记录')
    equ_asset_ids = fields.One2many(
        'equasset.line', 'equasset_id', '资产回顾')       

    def write(self, vals):  
        if  'equ_verification_ids' in vals:
            sss = vals['equ_verification_ids'][-1][2]['state_id']
            self.state_id = sss
        rent = super(EquRecord, self).write(vals)
        
            #if vals:
            # print(vals)
            # if 'equ_check_ids' in vals:
            #     vals['state_id'] = vals['equ_check_ids'][-1][2]['state_id']
            # if 'equ_measure_ids' in vals:
            #     vals['state_id'] = vals['equ_measure_ids'][-1][2]['state_id']
            # if 'equ_verification_ids' in vals:
            #     vals['state_id'] = vals['equ_verification_ids'][-1][2]['state_id']
            #     self.state_id = vals['equ_verification_ids'][-1][2]['state_id']
            # if 'equ_stoporstart_ids' in vals:
            #     vals['state_id'] = vals['equ_stoporstart_ids'][-1][2]['state_id']
                
            # if 'equ_transfer_ids' in vals:
            #     vals['state_id'] = vals['equ_transfer_ids'][-1][2]['state_id']
            # if 'equ_repair_ids' in vals:
            #     vals['state_id'] = vals['equ_repair_ids'][-1][2]['state_id']
            # if 'equ_scrap_ids' in vals:
            #     vals['state_id'] = vals['equ_scrap_ids'][-1][2]['state_id']
            #self.state_id = vals['equ_verification_ids'][-1][2]['state_id']
        # print(vals) 
        # return rent 
  

#验收
class EquCheckLine(models.Model):
    _name = 'equcheck.line'
    _rec_name = "state_id"
    _description = 'Equcheck Line'

    state_id = fields.Many2one('equstate', string='状态')
    owner_id = fields.Many2one('hr.employee', string='所有者')
    resperson_id = fields.Many2one('hr.employee', string='责任人')
    sysperson_id = fields.Many2one('hr.employee', string='系统管理员')

    sort_id = fields.Many2one('equstate', string='类别')
    department_id = fields.Many2one('hr.department' ,string='所属部门')
    money = fields.Integer('金额')
    receiving_data = fields.Date('收货日期')
    equcheck_id = fields.Many2one(
        'equrecord', 'check', auto_join=True,
        index=True, ondelete='cascade', required=True)


    


#计量
class EquMeasureLine(models.Model):
    _name = 'equmeasure.line'
    _rec_name = "state_id"
    _description = 'EquMeasure Line'

    # needmeasure = fields.Selection(
    #     [('Y', 'yes'),
    #      ('N', 'no'),],
    #     '需要计量',)
    state_id = fields.Many2one('equstate', string='状态')
    measure_id =  fields.Many2one('equmeasure', string='计量频率')
    measure_number = fields.Char('计量证书编号')
    measure_data = fields.Date('计量日期')
    measure_validity= fields.Date('计量有效期')
    measure_range = fields.Selection(
        [('Y', 'Y'),
         ('N', 'N'),
         ('期满', '期满')],
        '计量有效期内',)
    measure_type = fields.Selection(
        [('校准', '校准'),
         ('检定', '检定'),
         ('检测', '检测')],
        '计量证书类型',)
    measure_company = fields.Many2one('equcompany', string='计量单位') 

    equmeasure_id = fields.Many2one(
        'equrecord', 'measure', auto_join=True,
        index=True, ondelete='cascade', required=True)

#验证
class EquVerificationLine(models.Model):
    _name = 'equverification.line'
    _rec_name = "state_id"
    _description = 'EquVerification Line'

    state_id = fields.Many2one('equstate', string='状态')
    performance_verification= fields.Selection(
        [('Y', 'yes'),
         ('N', 'no'),],
        '性能验证确认')
    verification = fields.Char('验证内容', required=True)
    verification_id = fields.Many2one('equcompany', string='验证单位')
    verification_data = fields.Date('验证日期')
    verification_validity= fields.Date('验证有效期')
    verification_id = fields.Many2one('hr.employee', string='验证人')
    verification_range = fields.Selection(
        [('Y', 'yes'),
         ('N', 'no'),
         ('期满', 'out')],
        '在验证有效期内',)
    equverification_id = fields.Many2one(
        'equrecord', 'verification', auto_join=True,
        index=True, ondelete='cascade', required=True)

#停启
class EquStopOrStartLine(models.Model):
    _name = 'equstoporstart.line'
    _rec_name = "state_id"
    _description = 'EquStopOrStart Line'

    state_id = fields.Many2one('equstate', string='状态')
    place_id = fields.Many2one('equplace', string='放置地点')
    start_data = fields.Date('启用日期')
    stop_data = fields.Date('停用日期')  

    equstoporstart_id = fields.Many2one(
        'equrecord', 'stoporstart', auto_join=True,
        index=True, ondelete='cascade', required=True) 

#移交
class EquTransferLine(models.Model):
    _name = 'equtransfer.line'
    _rec_name = "state_id"
    _description = 'EquTransfer Line'

    state_id = fields.Many2one('equstate', string='状态')
    owner_id = fields.Many2one('hr.employee', string='所有者')
    resperson_id = fields.Many2one('hr.employee', string='责任人')
    sysperson_id = fields.Many2one('hr.employee', string='系统管理员')
    department_id = fields.Many2one('hr.department' ,string='所属部门') 
    remove_data = fields.Date('移交日期')

    equtransfer_id = fields.Many2one(
        'equrecord', 'transfer', auto_join=True,
        index=True, ondelete='cascade', required=True) 


#维修
class EquRepairLine(models.Model):
    _name = 'equrepair.line'
    _rec_name = "state_id"
    _description = 'EquRepair Line'

    state_id = fields.Many2one('equstate', string='状态')
    owner_id = fields.Many2one('hr.employee', string='申请人')
    repair_start_data = fields.Date('申请日期')
    record_id = fields.Many2one('hr.employee', string='记录人')
    repair_data = fields.Date('维修日期')

    equrepair_id = fields.Many2one(
        'equrecord', 'repair', auto_join=True,
        index=True, ondelete='cascade', required=True) 
#报废
class EquScrapLine(models.Model):
    _name = 'equscrap.line'
    _rec_name = "state_id"
    _description = 'EquScrap Line'

    state_id = fields.Many2one('equstate', string='状态')
    scrap_data = fields.Date('报废日期')

    equscrap_id = fields.Many2one(
        'equrecord', 'scrap', auto_join=True,
        index=True, ondelete='cascade', required=True) 


#资产回顾
class EquAssetLine(models.Model):
    _name = 'equasset.line'
    _rec_name = "assetsid"
    _description = 'EquAsset Line'

    assetsid = fields.Char('资产编号', required=True)
    ownership = fields.Selection(
        [('华测', 'huace'),
         ('高新区', 'gaoxinqu'),],
        '资产所有',)
    lastreview_data = fields.Date('上次回顾日期')
    nextreview_data = fields.Date('下次回顾日期')
    review_frequency_id = fields.Many2one('equreview', string='回顾频率')
    filename = fields.Char('文件号')

    equasset_id = fields.Many2one(
        'equrecord', 'asset', auto_join=True,
        index=True, ondelete='cascade', required=True) 

#note
class EquScrapLine(models.Model):
    _name = 'equnote.line'
    _description = 'EquNote Line'

    acceptable_standards = fields.Text(string="实验室可接受标准")
    note = fields.Text(string="备注")

    equrecord_id = fields.Many2one(
        'equrecord', 'Records',
        index=True, ondelete='cascade', required=True)



