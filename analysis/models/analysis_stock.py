import datetime
from collections import Counter
from inspect import isasyncgenfunction
from ast import literal_eval
from logging import FATAL
from math import fabs
from dateutil.relativedelta import relativedelta
from odoo.osv.query import Query
from uuid import NAMESPACE_OID
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np
import locale
locale.setlocale(locale.LC_ALL, 'en')
locale.setlocale(locale.LC_CTYPE, 'chinese')

class sampleSettings(models.Model):
    _name = 'analysis.sample.settings'
    _description = 'Analysis sample Settings'
    _rec_name = 'name_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # 设定物品属性，用于批量创建不同号的属性相同的物品

    # def _default_seq(self):
    #     return self.env['ir.sequence'].browse(24)

    name = fields.Char(
        'Reference', default='/',
        copy=False, index=True, readonly=True)
    date = fields.Date('选择日期')
    system_id = fields.Char('系统编号', compute='_compute_system_id', store=True)
    start_number = fields.Integer('基质初始号码', default=1, required=True)
    number = fields.Integer('数量',  required=True)
    sample_quantity = fields.Integer('体积μL', default=2, required=True)
    validity = fields.Date('默认有效期', required=True)
    location = fields.Many2one('analysis.ana.position', '可设定默认入库位置')
    anticoagulant_id = fields.Many2one(
        'analysis.anticoagulant', '抗凝/促凝', required=True)
    note_id = fields.Many2one('analysis.note', '备注', required=True)
    animalspecies_id = fields.Many2one(
        'analysis.animalspecies', '动物种属', required=True)
    matrix_id = fields.Many2one('analysis.matrix', '基质类型', required=True)
    matrix_type_id = fields.Many2one(
        'analysis.matrixtype', '基质类别', required=True)
    #gender_id = fields.Many2one('analysis.gender', '性别', required=True)
    #sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence',copy=False,readonly=True,default =_default_seq )
    name_id = fields.Char('基质编号', compute='_compute_name',
                          store=True, ondelete='cascade')
    button_clicked = fields.Boolean(string='Button clicked', default=False)
    judge_date = fields.Boolean()

    @api.onchange('validity')
    def _get_judge_date(self):
        today = fields.Date.today()
        if self.validity:
            if (self.validity - today).days >= 7:
                self.judge_date = True
            else:
                self.judge_date = False

    def create_ana_stock(self):
        # self.ensure_one()
        # 编号最大到999，初始最大99
        submit_date = self.env['analysis.sample']
        name_basic = "{}-{}-{}-{}".format(self.animalspecies_id.animalspecies,
                                          self.matrix_id.matrix,  self.matrix_type_id.matrix_type, self.system_id)
        for i in range(self.start_number, self.start_number+self.number):
            if i < 10:
                name = name_basic + '-00' + str(i)
            elif 10 <= i < 100:
                name = name_basic + '-0' + str(i)
            else:
                name = name_basic + str(i)
            """
            if self.gender_id:
                name = name + '-' +self.gender_id.gender 
            """
            data = [
                {
                    # "sample_id_c" : self.sequence_id.next_by_id(),
                    "animalspecies_c": self.animalspecies_id.id,
                    "anticoagulant_c": self.anticoagulant_id.id,
                    "iacuc_no": name,
                    "matrix_type_c": self.matrix_type_id.id,
                    "note_c": self.note_id.id,
                    'last_quantity_c': self.sample_quantity,
                    'validity_c': self.validity,
                    'location_c': self.location.id,
                    'judge_date_c': self.judge_date
                }
            ]
            submit_date.create(data)
        for record in self:
            record.write({'button_clicked': True})

    @api.depends('date')
    def _compute_system_id(self):
        if self.date:
            self.system_id = self.date.strftime('%Y%m%d')[2:]
        else:
            self.system_id = 0

    @api.depends('system_id', 'animalspecies_id', 'matrix_id', 'matrix_type_id', 'number', 'start_number')
    def _compute_name(self):
        for record in self:
            if record.animalspecies_id and record.matrix_id and record.matrix_type_id and record.system_id:
                if record.start_number < 10:
                    name1 = "{}-{}-{}-{}-00{}".format(record.animalspecies_id.animalspecies, record.matrix_id.matrix,
                                                      record.matrix_type_id.matrix_type, record.system_id, record.start_number)
                elif 10 <= record.start_number < 100:
                    name1 = "{}-{}-{}-{}-0{}".format(record.animalspecies_id.animalspecies, record.matrix_id.matrix,
                                                     record.matrix_type_id.matrix_type, record.system_id, record.start_number)
                else:
                    name1 = "{}-{}-{}-{}-{}".format(record.animalspecies_id.animalspecies, record.matrix_id.matrix,
                                                    record.matrix_type_id.matrix_type, record.system_id, record.start_number)
                if record.number < 10:
                    name2 = "{}-{}-{}-{}-{}".format(record.animalspecies_id.animalspecies, record.matrix_id.matrix,
                                                    record.matrix_type_id.matrix_type, record.system_id, '00'+str(record.number+record.start_number-1))
                elif 10 <= record.number < 100:
                    name2 = "{}-{}-{}-{}-{}".format(record.animalspecies_id.animalspecies, record.matrix_id.matrix,
                                                    record.matrix_type_id.matrix_type, record.system_id, '0'+str(record.number+record.start_number-1))
                else:
                    name2 = "{}-{}-{}-{}-{}".format(record.animalspecies_id.animalspecies, record.matrix_id.matrix,
                                                    record.matrix_type_id.matrix_type, record.system_id, str(record.number+record.start_number-1))
                self.name_id = name1+' ~ '+name2
                """
                if record.gender_id:
                    name1 =  "{}-{}".format(name1, record.gender_id.gender)
                    name2 = "{}-{}".format(name2, record.gender_id.gender)
                    self.name_id = name1+' ~ '+name2  
                """
            else:
                self.name_id = '编号待定'


class Sample(models.Model):
    _name = 'analysis.sample'
    _description = 'Analysis sample'
    _rec_name = 'iacuc_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_quantity(self):
        return self.env.user.employee_id

    def _compute_date(self):
        today = fields.Date.today()
        res = self.env['analysis.sample'].search([])
        for record in res:
            if record.validity_c:
                if (record.validity_c - today).days >= 7:
                    record.write({"judge_date_c": True})
                else:
                    record.write({"judge_date_c": False})

    iacuc_no = fields.Char('基质编号')
    animalspecies_c = fields.Many2one('analysis.animalspecies', '动物种属')
    matrix_type_c = fields.Many2one('analysis.matrixtype', '基质类别')
    note_c = fields.Many2one('analysis.note', '备注')
    anticoagulant_c = fields.Many2one('analysis.anticoagulant', '抗凝剂')
    validity_c = fields.Date('默认有效期')
    last_quantity_c = fields.Integer(
        '剩余体积μL')
    location_c = fields.Many2one('analysis.ana.position', '可设定默认入库位置')
    state = fields.Selection([
        ('草稿', 'Draft'),
        ('等待', 'Waiting'),
        ('不在库', 'Borrowed'),
        ('在库', 'Available'),
        ('失效', 'Closed')
    ], string='Status', default="在库", store=True)
    judge_date_c = fields.Boolean(string='大于七天')

    _sql_constraints = [
        ('iacuc_no_unique', 'unique(iacuc_no)', '库存中已经存在该基质编号了！')]

    def make_available(self):
        self.ensure_one()
        self.state = '在库'

    def make_borrowed(self):
        self.ensure_one()
        self.state = '不在库'

    def make_lost(self):
        self.state = '失效'
        self.last_quantity_c = 0


class AnaRentStage(models.Model):
    _name = 'ana.rent.stage'
    _description = "Ana Stage"
    _order = 'sequence,name'

    name = fields.Char()
    sequence = fields.Integer()
    fold = fields.Boolean()
    sample_state = fields.Selection(
        [('草稿', 'Draft'),
         ('在库', 'Available'),
         ('不在库', 'Borrowed'),
         ('完成', 'Closed')],
        'State', default="在库")
    number = fields.Integer(
        '数量', default=0, compute='_get_picking_type_number')
    is_favorite = fields.Boolean(defalt=True)

    def _get_picking_type_number(self):
        for record in self:
            record.number = record.env['ana.stock.picking'].search_count(
                [('stage_id', '=', record.id)])

    # 先定义返回方法
    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
        date1 = fields.Date.today()
        if self.id == 3:
            number_id = 2
        elif self.id == 2:
            number_id = 1
        else:
            number_id = 0
        if number_id > 0:
            context = {
                'search_default_stage_id': [self.id],
                'default_ana_picking_type_id': number_id,
                'search_default_prepared_date': date1
            }
        else:
            context = {
                'search_default_stage_id': [self.id],
                'search_default_prepared_date': date1
            }
        # 拼接context，字符形式context的格式检验不支持空格换行，[]等格式
        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action

    def go_(self):
        return self._get_action('analysis.action_go_')


class AnaPicking(models.Model):
    _name = "ana.stock.picking"
    _description = "Ana Picking"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_applicant(self):
        return self.env.user.employee_id

    def _default_name(self):
        return self.ana_picking_type_id

    @api.model
    def _default_rent_stage(self):
        Stage = self.env['ana.rent.stage']
        return Stage.search([], limit=1)

    @api.model
    def _group_expand_stages(self, stages, domain, order):
        return stages.search([], order=order)


    name = fields.Char('操作ID', default='/', copy=False, index=True, readonly=True)
    operaid = fields.Char('基质编号')
    prepared_by = fields.Many2one(
        'hr.employee', '操作人', readonly=True,  default=_default_applicant, store=True)
    check_person = fields.Boolean(
        string='Check person', compute='_check_person')
    prepared_date = fields.Date(
        '操作日期', default=fields.Date.today(), index=True)
    verifield_by = fields.Many2one(
        'res.users', '审核人', readonly=True)  
    verifield_date = fields.Date('审核日期')
    ana_picking_type_id = fields.Many2one(
        'ana.stock.picking.type', '选择操作', required=True)
    check_pciking_type = fields.Boolean(
        string='Picking Type', compute='_check_pciking_type')
    aim_id = fields.Many2one('ana.stock.picking.aim', '用途', required=True)
    stage_id = fields.Many2one(
        'ana.rent.stage', string='状态',
        default=_default_rent_stage,
        group_expand='_group_expand_stages'
    )
    appoint_peo_id = fields.Many2one(
        'res.users', string='指定审核人', required=True)

    storage_position_id = fields.Many2one('analysis.ana.position', string='位置')
    color = fields.Integer()
    choose_ids = fields.One2many(
        'ana.stock.picking.line', 'pick_id', string='选择', copy=True, default=0)

    def make_available(self):
        for record in self.choose_ids:
            if len(self.env['ana.stock.picking.line'].search([('iacuc_no_id', '=', record.iacuc_no_id.iacuc_no)])) == 1:
                # 第一次存不做操作
                # len =1 存
                # len =2 存 取
                # len =3 存 取 存
                record.use_quantity = 0
            else:
                # 上一笔取的使用量 再一次改写， = 上次取的值-本次存的值
                # 后来发现有可能触发一个bug，当连续创建两条取的line
                last_out_record = self.env['ana.stock.picking.line'].search(
                    [('iacuc_no_id', '=', record.iacuc_no_id.iacuc_no)])[-2]
                last_out_record.use_quantity = last_out_record.use_quantity - record.product_quantity
                record.use_quantity = 0

        self.write({'stage_id': 2, 'verifield_by': self.env.user.id,
                   'verifield_date': self.write_date})
        for record in self.choose_ids:
            record.iacuc_no_id.state = self.stage_id.sample_state
            record.iacuc_no_id.last_quantity_c = record.last_quantity
            record.iacuc_no_id.location_c = record.storage_position_id
            record.verifield_by_1 = self.verifield_by
            record.verifield_date_1 = self.verifield_date
            record.check_ver = True
        self.env.user.name

    def make_borrowed(self):
        self.write({'stage_id': 3, 'verifield_by': self.env.user.id,
                   'verifield_date': self.write_date})
        for record in self.choose_ids:
            record.use_quantity = record.product_quantity
            record.iacuc_no_id.state = self.stage_id.sample_state
            record.iacuc_no_id.last_quantity_c = 0
            record.iacuc_no_id.location_c = False
            record.verifield_by_1 = self.verifield_by.id
            record.verifield_date_1 = self.verifield_date
            record.check_ver = True

    @api.onchange('ana_picking_type_id', 'choose_ids')
    def _onchange_iacuc_no_id(self):
        aptid = self.env.context.get('deault_ana_picking_type_id', False)
        if aptid:
            self.ana_picking_type_id = aptid
        # self.with_context({'anapicking_type_id':self.ana_picking_type_id.display_name})

    def _compute__type(self):
        self.hide_picking_type = self.env.context.get(
            'default_stage_id', False)

    def jump_to_page_prizeexchange(self):  
        # self.env.ref是获取xml的id
        user_points = self.env['my.points'].search(
            [('user_id.id', '=', self.env.uid)]).points  # 当前用户积分
        if user_points >= self.points:
            view_id = self.env.ref('project.project_cti_prizeexchange_form').id
            return {
                'name': _('奖品兑换'),  # 可以写一些描述性的语言作为视图标题
                'type': 'ir.actions.act_window',  # 动作类型，默认为ir.actions.act_window
                'view_type': 'form',  # 跳转时打开的视图类型
                'view_mode': 'form',  # 列出跳转过去允许使用的视图模式
                # 给定的参数传递
                'context': {'prize_id': self.id, 'points': self.points},
                'limit': 80,  # 如果是tree，指定一页所能显示的行数
                'target': 'new',  # 有两个参数，current是在当前视图打开，new是弹出一个窗口打开
                'auto_refresh': 0,  # 为1时在视图中添加一个刷新功能
                'auto_search': True,  # 加载默认视图后，自动搜索
                'multi': False,  # 视图中有个更多按钮时，若multi设为True, 按钮显示在tree视图，否则显示在form视图
                'res_model': 'cti.prizeexchange',  # 参考的模型名称
                # 'res_id': 'views_form', # 加载指定id的视图，但只在view_type为form时生效，若没有这个参数则会新建一条记录
                'view_id': view_id,  # 指定视图的id，如果一个模块只有一个视图的时候可以忽略不计，但建议最好写入
                # 是一个(view_id,view_type) 的元组对列表，默认打开第一组的动作视图
                'views': [(view_id, 'form')],
                # 对视图面板进行一些设置，如{'form': {'action_button': True, options="{'create':False, 'create_edit':False, 'no_quick_create':True, 'no_open':True }"}}即对form视图进行的一些设置，action_buttons为True时调出编辑保存按钮，options’: {‘mode’: ‘edit’}时则打开时对默认状态为编辑状态
                "flags": {'form': {'action_button': True, }}
            }
        else:
            raise ValidationError('Error! 没有这么多积分用于兑换')


    @api.depends('ana_picking_type_id')
    def _check_pciking_type(self):
        if self.ana_picking_type_id.display_name == '取':
            self.check_pciking_type = False
        else:
            self.check_pciking_type = True

    @api.depends('prepared_by')
    def _check_person(self):
        if self.prepared_by.name == self.env.user.name:
            self.check_person = True
        else:
            self.check_person = False

    @api.model
    def create(self, vals):
        defaults = self.default_get(['name', 'ana_picking_type_id'])
        picking_type = self.env['ana.stock.picking.type'].browse(
            vals.get('ana_picking_type_id', defaults.get('ana_picking_type_id')))
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('ana_picking_type_id', defaults.get('ana_picking_type_id')):
            if picking_type.sequence_id:
                vals['name'] = picking_type.sequence_id.next_by_id()
        if picking_type.display_name == '取':
            # vals['stage_id']=1
            for i in vals['choose_ids']:
                #i[2]['animalspecies_c_id']= self.env['analysis.sample'].browse(i[2]['iacuc_no_id']).sample_quantity_c
                i[2]['last_quantity'] = 0
                i[2]['use_quantity'] = i[2]['product_quantity']
        else:
            for i in vals['choose_ids']:
                #i[2]['animalspecies_c_id']= self.env['analysis.sample'].browse(i[2]['iacuc_no_id']).sample_quantity_c
                i[2]['last_quantity'] = i[2]['product_quantity']
                if self.env['analysis.sample'].browse(i[2]['iacuc_no_id']).state == '草稿':
                    i[2]['use_quantity'] = 0
                else:
                    # 最后的切片是在索引lines的记录，如果有草稿状态，会先有一条满状态的体积，如果没有草稿状态，就不需要截取-2位
                    before_quantity = self.env['ana.stock.picking.line'].search(
                        [('iacuc_no_id', '=', i[2]['iacuc_no_id'])])[-1].product_quantity
                    i[2]['use_quantity'] = before_quantity - \
                        i[2]['product_quantity']

        # 新建的时候，无论如何都是待审核
        vals['stage_id'] = 1
        # 写入line
        for i in vals['choose_ids']:
            i[2]['prepared_by_1'] = vals['prepared_by']
            i[2]['ana_picking_type_id_1'] = vals['ana_picking_type_id']
            i[2]['aim_id_1'] = vals['aim_id']
            i[2]['prepared_date_1'] = vals['prepared_date']

        rent = super(AnaPicking, self).create(vals)
        if rent.stage_id.sample_state:
            if picking_type.display_name == '取':
                for record in rent.choose_ids:
                    record.iacuc_no_id.state = '等待'
            else:
                for record in rent.choose_ids:
                    record.iacuc_no_id.state = rent.stage_id.sample_state

        return rent

    def write(self, vals):
        rent = super(AnaPicking, self).write(vals)
        if self.stage_id.sample_state:
            for record in self.choose_ids:
                record.iacuc_no_id.state = self.stage_id.sample_state

        return rent

    def my_function(self):
        print('2223333')
        return {
            'warning': {
                'title': '提示',
                'message': '知道啦！'
            }
        }

    def _default_choose1(self):
        return self.env['ana.stock.picking.type'].browse(1)

    def _default_choose2(self):
        return self.env['ana.stock.picking.type'].browse(2)


class AnaPickingLine(models.Model):
    _name = 'ana.stock.picking.line'
    _rec_name = "iacuc_no_id"
    _description = 'Ana Stock Picking Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.onchange('product_quantity')
    def _default_max(self):

        if self.pick_id.ana_picking_type_id.display_name == '取':
            self.last_quantity = 0
        else:

            self.last_quantity = self.product_quantity

    iacuc_no_id = fields.Many2one(
        'analysis.sample', string='基质编号', required=True)
    product_quantity = fields.Integer(
        '存/取体积μL',
        digits='Unit of Measure', required=True)
    last_quantity = fields.Integer(
        '剩余体积μL', default=0,
        digits='Unit of Measure', readonly=True, store=True)

    #animalspecies_c_id = fields.Integer('容器最大体积μL',default=0,readonly =True,store = True)
    pick_id = fields.Many2one(
        'ana.stock.picking', 'Requirement', auto_join=True,
        index=True, ondelete='cascade', required=True)
    use_quantity = fields.Integer(
        '使用体积μL', default=0, readonly=True, store=True)

    prepared_by_1 = fields.Many2one('hr.employee', '操作人', readonly=True)

    verifield_by_1 = fields.Many2one('res.users', '审核人', readonly=True)
    check_ver = fields.Boolean(string='Picking Type')
    ana_picking_type_id_1 = ana_picking_type_id = fields.Many2one(
        'ana.stock.picking.type', '操作', readonly=True)
    verifield_date_1 = fields.Date('审核日期', readonly=True)
    prepared_date_1 = fields.Date('申请日期', readonly=True)
    aim_id_1 = fields.Many2one('ana.stock.picking.aim', '用途', required=True)
    storage_position_id = fields.Many2one(
        'analysis.ana.position', required=True, string='存取位置')

    @api.onchange('iacuc_no_id')
    def _onchange_iacuc_no_id(self):

        if self.pick_id.ana_picking_type_id.display_name == '取':
            self.product_quantity = self.iacuc_no_id.last_quantity_c
            self.storage_position_id = self.iacuc_no_id.location_c
        else:
            self.product_quantity = 0
        self.storage_position_id = self.iacuc_no_id.location_c
        #self.animalspecies_c_id = self.iacuc_no_id.sample_quantity_c

        # 筛选重复选择 并提醒.
        #self.animalspecies_c_id = self.iacuc_no_id.sample_quantity_c
        # 查询当前已经选择的id  删除最后一个多余没用id
        up_iacuc_no_id_ids = [
            x.iacuc_no_id.id for x in self.pick_id.choose_ids][:-1]
        Counts_1 = dict(Counter(up_iacuc_no_id_ids))
        if len(Counts_1) > 1:  # 当提交的数据大于1的时候统计
            duplicateContent = [
                key for key, value in Counts_1.items() if value > 1]  # 找出里面重复的内容
            if duplicateContent:  # 如果有重复项 返回报警信息
                idGetName = [self.pick_id.choose_ids.iacuc_no_id.browse(
                    [i]).iacuc_no for i in duplicateContent]
                return {'warning': {'title': 'Warning!', 'message': _(f'已选内容 / {idGetName[0]} / 有重复项请删除后尝试')}}
        # print(self.context_get('anapicking_type_id'))
        if self.pick_id.ana_picking_type_id.display_name == '取':
            if self.pick_id.choose_ids.iacuc_no_id.ids:  # 过滤筛选 返回domain 选择
                return {'domain': {'iacuc_no_id': ['&', ('id', 'not in', self.pick_id.choose_ids.iacuc_no_id.ids), ('state', 'in', ['在库'])]}}
            # 没有命中if 返回 在库
            return {'domain': {'iacuc_no_id': [('state', 'in', ['在库'])]}}

        if self.pick_id.ana_picking_type_id.display_name == '存':
            if self.pick_id.choose_ids.iacuc_no_id.ids:  # 过滤筛选 返回domain 选择
                return {'domain': {'iacuc_no_id': ['&', ('id', 'not in', self.pick_id.choose_ids.iacuc_no_id.ids),
                                                   ('state', 'in', ['不在库', '草稿'])]}}
            # 没有命中if 返回 不在库
            return {'domain': {'iacuc_no_id': [('state', 'in', ['不在库', '草稿'])]}}
