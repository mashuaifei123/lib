import datetime
from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import base64

class EquRecord(models.Model):
    _name = 'equrecord'
    _description = 'EquRecord'
    _rec_name = 'registerid'

    @api.model
    def _default_ids(self):
        default_ids=[]
        print(self)
        default_ids.append((0, 0,{ 'resperson_id_1' : 1,
                                    'locate_id_1' :1,
                                    'owner_id_1' :1,
                                    'sysperson_id_1' :1,
                                    'department_id_1': 1
                                                                       
                                    })) #字典里边填的是默认子表的值，前面0，0都是默认的
        return default_ids

    is_verificate = fields.Boolean(string= '验证状态', default=False,readonly=True)
    is_measure = fields.Boolean(string= '计量状态', default=False,readonly=True)
    state_id = fields.Many2one('equstate', string='状态1')
    registerid = fields.Char('编号', required=True)
    registername = fields.Char('名称', required=True)
    registeredition = fields.Char('型号版本', required=True)
    attribute_sort = fields.Selection(
        [('仪器设备', '仪器设备'),
         ('计算机化系统', '计算机化系统'),
         ('办公软件', '办公软件')],
        '属性分类',)
    assetsid = fields.Char('资产编号', required=True)
    ownership = fields.Selection(
        [('华测', 'huace'),
         ('高新区', 'gaoxinqu'),],
        '资产所有',)
    manufacturer_id = fields.Many2one('equmanufacturer', string='制造厂商')
    factorynumber = fields.Char('出厂编号')
    manufacturerphone= fields.Char('厂商联系电话', related='manufacturer_id.phone')
    range_parameters = fields.Text('量程技术参数')
    accuracy_level = fields.Text('准确度等级')
    # range_parameters = fields.Text('实验室可接受标准')
    acceptable_standards = fields.Text(string="实验室可接受标准")
    note = fields.Text(string="备注")

    #验收记录
    owner_id = fields.Many2one('hr.employee', string='所有者')
    resperson_id = fields.Many2one('hr.employee', string='责任人')
    sysperson_id = fields.Many2one('hr.employee', string='系统管理员')
    department_id = fields.Many2one('hr.department' ,string='所属部门')
    locate_id = fields.Many2one('equplace', string='放置位置')

    sort_id = fields.Many2one('equstate', string='类别')
    money = fields.Integer('金额')
    receiving_data = fields.Date('收货日期')



    # equ_check_ids = fields.One2many(
    #     'equcheck.line', 'equcheck_id', '新验收记录')
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
    equ_pdf_ids = fields.One2many(
        'equrecord.attachment.line', 'equpdf_id', '计量校准证书')
    equ_sop_ids = fields.Many2many(
        'equsop.line', 'equsop_id', 'SOP')   



    def write(self, vals):  
        # 加水印
        if  'equ_pdf_ids' in vals:
            original_data = vals['equ_pdf_ids'][-1][2]['worksheet']
            mark_data = self.env['equpdfmark'].search([]).display_name
            pdf_2 = base64.standard_b64decode(original_data)
            pdf_watermark = base64.standard_b64decode(mark_data)
            pdfFRmodel_b = PdfFileReader(io.BytesIO(pdf_2), strict=False)
            # 读取水印文件  -> pdfFR
            # pdfFR_watermark = PdfFileReader(open(watermark_f, mode='rb'), strict=False) # 单个文件
            pdfFR_watermark = PdfFileReader(io.BytesIO(pdf_watermark), strict=False)  # 读取base64 b 水印文件
            # 合并水印文件到pdf
            # 转换到 -> model b
            pdf_output = PdfFileWriter() # 定义输出文件对象
            page_count = pdfFRmodel_b.getNumPages() # 获得页面数量
            for page_number in range(page_count):
                input_page = pdfFRmodel_b.getPage(page_number)
                input_page.mergePage(pdfFR_watermark.getPage(0))
                pdf_output.addPage(input_page)
            stream = io.BytesIO()
            pdf_output.write(stream)
            data = base64.standard_b64encode(stream.getvalue())
            vals['equ_pdf_ids'][-1][2]['worksheet'] = data

        if  'equ_transfer_ids' in vals:
            self.owner_id = vals['equ_transfer_ids'][-1][2]['owner_id_new']
            self.resperson_id = vals['equ_transfer_ids'][-1][2]['resperson_id_new']
            self.sysperson_id = vals['equ_transfer_ids'][-1][2]['sysperson_id_new']
            self.department_id = vals['equ_transfer_ids'][-1][2]['department_id_new']
            self.locate_id = vals['equ_transfer_ids'][-1][2]['locate_id_new']

        rent = super(EquRecord, self).write(vals)
        return rent


class EquCheckLine(models.Model):
    _name = 'equrecord.attachment.line'
    _rec_name = "name1"
    _description = 'Equrecord Attachment Line'

    time1 = fields.Date('上传日期' )
    name1 = fields.Char('字段1', required=True)
    name2 = fields.Char('字段2', required=True)
    worksheet = fields.Binary('PDF')
    equpdf_id = fields.Many2one(
        'equrecord', 'pdf', auto_join=True,
        index=True, ondelete='cascade', required=True)
    
    

    
  
# 属性
# class EquCheckLine(models.Model):
#     _name = 'equcheck.line'
#     _rec_name = "state_id"
#     _description = 'Equcheck Line'

#     state_id = fields.Many2one('equstate', string='状态')
#     owner_id = fields.Many2one('hr.employee', string='所有者')
#     resperson_id = fields.Many2one('hr.employee', string='责任人')
#     sysperson_id = fields.Many2one('hr.employee', string='系统管理员')

#     sort_id = fields.Many2one('equstate', string='类别')
#     department_id = fields.Many2one('hr.department' ,string='所属部门')
#     money = fields.Integer('金额')
#     receiving_data = fields.Date('收货日期')
#     equcheck_id = fields.Many2one(
#         'equrecord', 'check', auto_join=True,
#         index=True, ondelete='cascade', required=True)


#计量
class EquMeasureLine(models.Model):
    _name = 'equmeasure.line'
    _rec_name = "measure_data"
    _description = 'EquMeasure Line'

    # needmeasure = fields.Selection(
    #     [('Y', 'yes'),
    #      ('N', 'no'),],
    #     '需要计量',)
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
    _rec_name = "verification_data"
    _description = 'EquVerification Line'

    performance_verification= fields.Selection(
        [('Y', '是'),
         ('N', '否'),],
        '性能验证确认')
    verification = fields.Char('验证内容', required=True)
    verification_comp = fields.Many2one('equcompany', string='验证单位')
    verification_data = fields.Date('验证日期')
    verification_validity= fields.Date('验证有效期')
    verification_id = fields.Many2one('hr.employee', string='验证人')
    verification_range = fields.Selection(
        [('Y', '是'),
         ('N', '否'),
         ('期满', '期满')],
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
    _rec_name = "remove_data"
    _description = 'EquTransfer Line'

    resperson_id_1 = fields.Many2one('hr.employee', string='原责任人',readonly=True)
    locate_id_1 = fields.Many2one('equplace', string='原位置',readonly=True)
    owner_id_1 = fields.Many2one('hr.employee', string='原所有者',readonly=True)
    sysperson_id_1 = fields.Many2one('hr.employee', string='原系统管理员',readonly=True)
    department_id_1 = fields.Many2one('hr.department' ,string='原所属部门',readonly=True) 

    owner_id_new = fields.Many2one('hr.employee', string='新所有者')
    locate_id_new = fields.Many2one('equplace', string='新位置')
    resperson_id_new = fields.Many2one('hr.employee', string='新责任人')
    sysperson_id_new = fields.Many2one('hr.employee', string='系统管理员')
    department_id_new = fields.Many2one('hr.department' ,string='新所属部门') 

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
    _rec_name = "lastreview_data"
    _description = 'EquAsset Line'


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



    equrecord_id = fields.Many2one(
        'equrecord', 'Records',
        index=True, ondelete='cascade', required=True)

#sop
class EquSopLine(models.Model):
    _name = 'equsop.line'
    _description = 'EquSop Line'

    sopnumber = fields.Char('sop编号')
    sopname = fields.Char('sop名称')

#验证文件
class EquFileLine(models.Model):
    _name = 'equfile.line'
    _description = 'EquFile Line'

    sopnumber = fields.Char('sop编号')
    equsop_id = fields.Many2one(
        'equrecord', 'Records',
        index=True, ondelete='cascade', required=True)
