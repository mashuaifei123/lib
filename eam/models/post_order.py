import datetime

from requests.sessions import default_headers
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np
from .post_eam import PostDepartmentEam
from .stock_eam import InsertEam


class PostOrder(models.Model):
    _name = 'postorder'
    _description = 'PostOrder'
    _rec_name = 'orderid'

    # 在product页面添加到货期限和(属于部门,可以不用)
    # 在product页面添加虚拟库存值

    def _default_register(self):
        return self.env.user.employee_id

    orderid = fields.Char('申请单号', required=True)
    orderdepartment = fields.Char('申请部门', required=True)
    poster = fields.Char('申请人')
    post_data = fields.Date('申请日期')
    choose_ids = fields.One2many(
        'postorder.line', 'pick_id', string='选择', copy=True, default=0)
    state = fields.Selection([
        ('已审核', '已审核'),
        ('等待', '等待审核'),
        ('未通过', '未通过'),
    ], string='Status', default="等待", store=True)
    modtime = fields.Date('审核日期')

    def _crete_department_order(self):
        username = '48502'
        password = '123'
        user = '张铭'

        order = PostDepartmentEam()
        order.login(username, password)
        res = self.env['postorder'].search([('state', '=', '等待')])
        orderid_list = [self.env['postorder'].search(
            [('id', '=', i)]).orderid for i in res.ids]
        orderpass_list = order.getPassTime(orderid_list)
        # 每天先审核所有订单 再判断是否申请当天缺失值的订单
        # 已审核，写入审核时间，订单审核状态，涉及物料的应到库日期，物料也写入审核状态方便对比查询
        for i in orderpass_list:
            for j in res.ids:
                record = self.env['postorder'].search([('id', '=', j)])
                if record.orderid == i['apply_id']:
                    record.modtime = i['modtime']
                    record.state = '已审核'
                for re in record.choose_ids:
                    product = self.env['product.template'].search(
                        [('barcode', '=', re.goods)])
                    date = datetime.datetime.strptime(
                        i['modtime'], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=product.day_line)
                    re.redate = date
                    re.state = '已审核'
                    re.lines_department = record.orderdepartment

        # data_list = order.getpostdataframe()#总dict.
        data_df = order.getpostdataframe()  # 总df
        df1 = data_df[data_df['deptName'].str.contains(
            '医学-苏州生物兽医运行部-苏州生物')]  # 截取兽医
        find_order_inf = order.findOrderInf()
        order_line = self.env['postorder.line'].search(
            [('redate', '>', datetime.datetime.now())])
        goods = []
        product_quantity = []
        lines_department = []
        for i in order_line:
            goods.append(i.goods)
            product_quantity.append(i.product_quantity)
            lines_department.append(i.lines_department)
        df_lines = pd.DataFrame(
            {'materialCode': goods, 'product_quantity': product_quantity, 'deptName': lines_department})
        # 生成lines的dataframe，agg相同部门物料的值为虚拟库存。
        df_lines_agg = df_lines.groupby(
            by=['materialCode', 'deptName']).product_quantity.sum().reset_index()
        # 合并df1和lines的df，以code和部门name合并，生成申请数值列renum1，判断renum列与虚拟库存的大小，保留需要申请的信息
        df3 = pd.merge(df1, df_lines_agg, how='left',
                       on=['materialCode', 'deptName'])
        df3.fillna(0, inplace=True)
        df3['reNum1'] = df3.apply(lambda x: int(
            x['reNum'])-x['product_quantity'] if x['product_quantity'] < int(x['reNum']) else 0, axis=1)
        df3 = df3[df3['reNum1'] != 0]
        df3.drop(['reNum'], axis=1, inplace=True)
        df3.rename(columns={'reNum1': 'reNum'}, inplace=True)
        # df3 ： deptName  deptId    materialCode  name num   type lowNum  product_quantity  reNum
        df3_dict = df3.to_dict('records')

        daily_date = []
        for num, i in enumerate(df3_dict):
            daily_info = [0, "virtual_" + str(700+num),
                          {
                'data_department': i['deptName'],
                'good_code': i['materialCode'],
                'good_name': i['name'],
                'min_num': int(i['lowNum']),
                'need_num': int(i['reNum']),
                'now_num': int(i['num']),
                'type': i['type'],
                'virtual_num': int(i['product_quantity'])
            }
            ]
            daily_date.append(daily_info)
        ldate = {
            "today": fields.Date.today(),
            "choose_ids": daily_date
        }
        self.env['dailydata'].create(ldate)

        data_list = []
        for i in df3.groupby('deptName'):
            dict1 = {'deptName': i[0], 'deptId': i[1].iloc[0, 1],
                     'goods_list': i[1].iloc[:, 2:9].to_dict('records')}
            data_list.append(dict1)
        for j in data_list:
            # 只选择兽医部门进行补货
            if j['deptName'] == '医学-苏州生物兽医运行部-苏州生物':
                good_list = []
                for num, jj in enumerate(j['goods_list']):
                    goods = [
                        0, "virtual_" + str(2000+num), {'goods': jj['materialCode'], 'product_quantity': jj['reNum']}]
                    good_list.append(goods)
                self.create({'orderdepartment': j['deptName'], 'poster': user,
                            'orderid': find_order_inf[0], 'post_data': find_order_inf[1], 'choose_ids': good_list})
       # order.AddOrder1(user, data_list, find_order_inf)

    def action_send_email(self):  # 发送邮件通知提醒
        #self.ensure_one()
        mail_to = ','.join(['guozhanbin@cti-cert.com','mashuaifei@cti-cert.com'])
        res = self.env['stock.warehouse.orderpoint'].search([])
        email_list=[]
        for orderpoint in res:
            if orderpoint.qty_to_order > 0:
                data2 = {'物料':orderpoint.product_id.display_name,
                        #   'qty_on_hand':orderpoint.qty_on_hand,
                        #   'product_min':orderpoint.product_min_qty,
                        #   'qty_forecast':orderpoint.qty_forecast,
                          '部门': orderpoint.product_id.department_id.name,
                          '数量':orderpoint.qty_to_order
                }
                email_list.append(data2)
            else:
                pass
        df2 =  pd.DataFrame(email_list)
        table = df2.to_html(index=False,justify='center',col_space=100)
        html = f"""<table border="0" cellpadding="0" cellspacing="0"
    style="padding-top:16px;background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;">
    <tbody>
        <tr>
            <td align="center">
                <table border="0" cellpadding="0" cellspacing="0" width="590"
                    style="padding:16px;background-color: white; color: #454748; border-collapse:separate;">
                    <tbody>
                        <!-- 页眉 -->
                        <tr>
                            <td align="center" style="min-width:590px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="590"
                                    style="min-width:590px;background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                                    <tbody>
                                        <tr>
                                            <td valign="middle"><span style="font-size:10px;">&nbsp;</span><br><span
                                                    style="font-size:20px;font-weight: bold;">库存提醒</span>
                                            </td>
                                            <td valign="middle" align="right"> </td>
                                        </tr>
                                        <tr>
                                            <td colspan="2" style="text-align:center;">
                                                <hr width="100%"
                                                    style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;">
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr><!-- 内容 -->
                        <tr>
                            <td align="center" style="min-width:590px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="590"
                                    style="min-width:590px;background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                                    <tbody>
                                        <tr>
                                            <td valign="top" style="font-size:13px;">
                                                <div> 同事<br><br> 您好！以下是今天的补货清单<br>
                                                    <div >
                                                        {table}
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="text-align:center;">
                                                <hr width="100%"
                                                    style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;">
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr><!-- 页脚 -->
                        <tr>
                            <td align="center" style="min-width:590px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="590"
                                    style="min-width:590px;background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">
                                    <tbody>
                                        <tr>
                                            <td valign="middle" align="left" style="opacity:0.7;"> </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
    </tbody>
</table>"""
        values = {'subject': '库存提醒',
                  'email_from': 'otrs@cti-cert.com',
                  'email_to': mail_to,
                  'body_html': html}
        mail = self.env['mail.mail'].sudo().create(values)
        mail.send(raise_exception=False)
        return None

    def _crete_eam_order(self):
        username = '48502'
        password = '123'
        user = '张铭'
        order = InsertEam()
        order.login(username, password)

        # department = '医学-苏州生物信息资源部-苏州生物'
        res = self.env['stock.warehouse.orderpoint'].search([])
        res_list = []
        email_list=[]
        for orderpoint in res:
            if orderpoint.qty_to_order > 0:
                data = {
                    'department': orderpoint.product_id.department_id.name,
                    'code': orderpoint.product_id.barcode,
                    'number': int(orderpoint.qty_to_order),
                }
                data2 = {'物料':orderpoint.product_id.display_name,
                        #   'qty_on_hand':orderpoint.qty_on_hand,
                        #   'product_min':orderpoint.product_min_qty,
                        #   'qty_forecast':orderpoint.qty_forecast,
                          '部门': orderpoint.product_id.department_id.name,
                          '数量':orderpoint.qty_to_order
                }
                res_list.append(data)
                email_list.append(data2)
            else:
                pass
        df2 =   pd.DataFrame(email_list)
        tbl = df2.to_html(index=False,justify='center',col_space=100)
        print(tbl)
        return tbl
        # df = pd.DataFrame(res_list)
        # data_list = [{"department": k, "code": g["code"].tolist(
        # ), "number":g["number"].tolist()} for k, g in df.groupby("department")]
        # print(data_list)
        # for departmentpoint in data_list:
        #     department_name = departmentpoint['department']
        #     code_list = departmentpoint['code']
        #     number_list = departmentpoint['number']
        #     order.AddOrder(code_list, number_list, department_name, user)

    def _get_mod_state(self):
        res = self.env['postorder'].search([('state', '=', '等待')])
        orderid_list = [self.env['postorder'].search(
            [('id', '=', i)]).orderid for i in res.ids]
        order = InsertEam()
        orderpass_list = order.getPassTime(orderid_list)
        # 已审核，写入审核时间，订单审核状态，涉及物料的应到库日期，物料也写入审核状态方便对比查询
        for i in orderpass_list:
            for j in res.ids:
                record = self.env['postorder'].search([('id', '=', j)])
                if record.orderid == i['apply_id']:
                    record.modtime = i['modtime']
                    record.state = '已审核'
                for re in record.choose_ids:
                    product = self.env['product.template'].search(
                        [('barcode', '=', re.goods)])
                    product.virtual_num = re.product_quantity
                    date = datetime.datetime.strptime(
                        i['modtime'], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=product.day_line)
                    re.redate = date
                    re.state = '已审核'
                    re.lines_department = record.orderdepartment


class PostOrderLine(models.Model):
    _name = 'postorder.line'
    _rec_name = "goods"
    _description = 'PostOrder Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    goods = fields.Char('物料', required=True, store=True)
    product_quantity = fields.Float(
        '数量', digits='Unit of Measure', required=True)
    redate = fields.Date('预计到货日期', required=True)
    state = fields.Char('是否审核')
    lines_department = fields.Char('申请部门', required=True)
    pick_id = fields.Many2one('postorder', 'Requirement', auto_join=True,
                              index=True, ondelete='cascade', required=True)


class DailyData(models.Model):
    _name = 'dailydata'
    _description = 'DailyData'
    _rec_name = 'today'

    today = fields.Date('今日', default=fields.Date.today())
    choose_ids = fields.One2many(
        'dailydataline', 'pick_id', string='选择', copy=True, default=0)


class DailyData(models.Model):
    _name = 'dailydataline'
    _description = 'DailyData Line'
    _rec_name = 'data_department'

    data_department = fields.Char('部门', required=True)
    good_name = fields.Char('物料名称', required=True)
    good_code = fields.Char('物料编码', required=True)
    min_num = fields.Integer('最低存储量', required=True)
    now_num = fields.Integer('现有库存', required=True)
    virtual_num = fields.Integer('虚拟库存', required=True)
    need_num = fields.Integer('应补数量', required=True)
    type = fields.Char('型号', required=True)
    pick_id = fields.Many2one('dailydata', 'Requirement', auto_join=True,
                              index=True, ondelete='cascade', required=True)
