import  datetime
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import uuid
import pandas as pd
import numpy as np

class StudyNumber(models.Model):
    _name = 'project.studynumber'
    _description = 'Project studynumber'
    _rec_name = 'study_id'

    study_id = fields.Char('专题编号', required=True)
    studyname = fields.Char('专题名称', required=True)
    author_id = fields.Many2one(
        'hr.employee',
        string='专题负责人', required=True
    )  # 关联员工应用名单
    start_time = fields.Date('D1开始日期', required=True)
    feeding_room = fields.Char('饲养房间', required=True)
    excperiment_ids = fields.One2many(
        'project.experiment', 'studyname_id', '操作')
    company_id = fields.Many2one(
        'res.company', '公司', index=True,
        default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(study_id)', '专题编号必须唯一.'),
    ]


    def study_analysis(self):
        print(self)
        ss = self.env['stock.picking']
        return True


class Actions(models.Model):
    _name = 'project.actions'
    _rec_name = 'actname'
    _description = 'Project actions'

    actname = fields.Char('试验操作', required=True)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(actname)', '试验操作必须唯一.'),
    ]


class Experiment(models.Model):
    """BOM"""
    _name = 'project.experiment'
    _description = 'Project experiment'
    _rec_name = 'studyname_id'

    """默认值输入的不是数据类型， 是模型对象hr.department(1,)
    """

    def _default_department(self):
        return self.env.user.employee_id.department_id

    def _invalidate_cache(self):
        """"清理当前游标缓存"""
        self.invalidate_cache()

    partner_id = fields.Many2one(
        'res.partner', '送货地址')

    studyname_id = fields.Many2one(
        'project.studynumber', string='专题号', required=True)
    study_name = fields.Char(
        string='专题名称', related='studyname_id.studyname', readonly=True, store=False)
    department_id = fields.Many2one(
        'hr.department', string='部门', required=True, default=_default_department)
    description = fields.Html('补充描述', sanitize=True, strip_style=False)
    bom_line_ids = fields.One2many(
        'project.bom.line', 'bom_id', '操作子集', copy=True)
    button_clicked = fields.Boolean(string= 'Button clicked', default=False)



    def create_order(self):
        # 建议先判断是否专题有ＢＯＭ数据
        def parse_ymd(s):
            year_s, mon_s, day_s = s.split('-')
            return datetime(int(year_s), int(mon_s), int(day_s)).strftime('%Y-%m-%d %H:%M:%S')
         #now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            dict1 =[]
            for ss in self:
                if ss.bom_line_ids:
                    for bom_line in ss.bom_line_ids:
                        for data_d in bom_line.date_set.split(','):
                            if bom_line.bom_line_child_ids:
                                for bom_line_child in bom_line.bom_line_child_ids:
                                    data_set = [data_d, bom_line_child.product_id.id, bom_line_child.product_qty]
                                    dict1.append(data_set)
                            else:
                                raise UserError(_('没有写入物料需求'))                           
                else:
                    raise UserError(_('没有写入试验操作'))
            df = pd.DataFrame(dict1)
            date_g = df.groupby([0])

            # 有多少天，循环多少次，写入多少单子
            for key, value in date_g:
                sum_g_2 =  value.groupby([1])[2].sum()
                value.drop_duplicates(subset =[1],inplace= True)
                value.sort_values(1,inplace=True)
                value['sum'] = list(sum_g_2)
                value.drop(2,axis= 1,inplace = True)
                date_dict =value.to_dict('records')
                move_ids_without_package = []
                for num,line in enumerate(date_dict):
                    move_ids_without_package_child = [0,"virtual_"+ str(2000+num),
                                                        {
                                                        "company_id": 1,
                                                        "state": "draft",  # 草稿状态
                                                        "picking_type_id": 2,
                                                        "location_id": 8,
                                                        "location_dest_id": 5,
                                                        "additional": False,
                                                        "product_id": line[1], # 物料名称
                                                        "name":"wuliao2",
                                                        "date": parse_ymd(line[0]),
                                                        "product_uom_qty": line['sum'],# 物料数量
                                                        #"quantity_done": line['sum'], # 物料数量
                                                        "product_uom": 1, # 单位
                                                        "lot_ids": [[6,False,[]]]
                                                        }
                                                    ]
                    move_ids_without_package.append(move_ids_without_package_child)
                ldate = {
                    "is_locked": True,
                    "immediate_transfer": False,
                    "priority": "0",
                    "partner_id": self.partner_id.id, #送给谁，目的地
                    "picking_type_id": 2, #出入库类型
                    "location_id": 8,
                    "location_dest_id": 5,
                    "scheduled_date": parse_ymd(line[0]),  # 时间日期
                    "origin": False,
                    "owner_id": False,
                    "move_ids_without_package": move_ids_without_package,
                    "move_type": "direct",
                    "user_id": self.env.user.id, # 创建人 user_id
                    "company_id": 1, # 公司ID compyan_id
                    "note": False
                }
                print('OK')
                self.env['stock.picking'].create(ldate)
            for record in self:
                record.write({'button_clicked':True})

        except:
            raise UserError(_('出现问题，order没有创建成功'))


    """复杂约束 循环self相当于循环本模型的字典键对值数据
    """
    @api.constrains('studyname_id', 'department_id', 'bom_line_ids',)
    def _check_line(self):
        
        for bom in self:
            for bom_line in bom.bom_line_ids:
                c = self.env['project.bom.line'].search_count(
                    ['&', '&',
                     ('bom_id.studyname_id', '=', bom.studyname_id.id),
                     ('bom_id.department_id', '=', bom.department_id.id),
                     ('action_id', '=', bom_line.action_id.id)
                     ])
                if c > 1:
                    raise models.ValidationError(
                        '实验id + 部门 + 操作 组合必须唯一')


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if 'studyname_id' not in default:
            default['studyname_id'] = 10
        #default.update({'study_name':False})
        return super(Experiment, self).copy(default = default)





class ProductProduct(models.Model):
    _inherit = "product.template"

    m_type = fields.Char('型号')
    m_article_number = fields.Char('货号')
    m_material_code = fields.Char('物料编码')
    m_unit = fields.Char('单位')


class BomLine(models.Model):
    """操作"""
    _name = 'project.bom.line'
    _rec_name = "action_id"
    _description = 'Project Bom Line'

    def _get_uuid(self):
        return uuid.uuid4()
    date_set = fields.Char(string='日期', required=True)

    action_id = fields.Many2one(
        'project.actions', string='实验操作', required=True)
    bom_line_child_ids = fields.One2many(
        'project.bom.line.child', 'action_id_id', '物料子集', copy=True)
    bom_id = fields.Many2one(
        'project.experiment', '父级',
        index=True, ondelete='cascade', required=True)
    uuid = fields.Char(string='uuid', default=_get_uuid)


class BomLineChild(models.Model):
    """日期"""
    _name = 'project.bom.line.child'
    _rec_name = "product_id"
    _description = 'Project Bom Line Child'

    action_id_id = fields.Many2one(
        'project.bom.line', 'Parent Line BoM', index=True, ondelete='cascade', required=True)
    product_id = fields.Many2one('product.template', 'Product', required=True)
    product_qty = fields.Float(
        '数量', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_type = fields.Char(
        string='型号', related='product_id.m_type', readonly=True)
    product_article_number = fields.Char(
        string='货号', related='product_id.m_article_number', readonly=True)
    product_material_code = fields.Char(
        string='物料编码', related='product_id.m_material_code', readonly=True)
    product_unit = fields.Char(
        string='单位', related='product_id.m_unit', readonly=True)

    coefficient = fields.Float('Coefficient of losses', default=1.0)
    _sql_constraints = [
        ('product_qty', 'check (product_qty >=0)',
         '数量必须是正数！'),
    ]


class Requirement(models.Model):
    _name = 'project.requirement'
    _rec_name = "applicant"
    _description = 'Project Requirement'

    def _default_department(self):
        return self.env.user.employee_id.department_id

    def _default_applicant(self):
        return self.env.user.employee_id

    applicant = fields.Many2one(
        'hr.employee', '申请人', readonly=True,  default=_default_applicant)
    department_id = fields.Many2one(
        'hr.department', string='部门',  readonly=True, default=_default_department)

    require_line_ids = fields.One2many(
        'project.requirement.line', 'requirement_id', 'Requirement Lines', copy=True)

    
class RequirementLine(models.Model):
    _name = 'project.requirement.line'
    _rec_name = "require_product_id"
    _description = 'Project Requirement Line'

    require_product_id = fields.Many2one('product.template', 'Product', required=True)
    product_quantity = fields.Float(
        '数量', default=1.0,
        digits='Product Unit of Measure', required=True)
    
    requirement_id = fields.Many2one(
        'project.requirement', 'Requirement',
        index=True, ondelete='cascade', required=True)



   

    
