# 需要查询的字段模型和关联关系
# [专题编号ID, 时间日期, 部门ID, 创建人ID, 物料ID, 物料数量,]
# 一查多 方式一
# ['id', 'date_set', 'id', 'id', 'product_id', 'product_qty']
# self.studyname_id.id , bom_line.date_set, self.department_id.id, self.create_uid.id, bom_line_child.product_id.id, bom_line_child.product_qty

def create_order(self):
    #object_experiment = self.env['project.experiment'].search([('studyname_id','=',self.id)])
    for bom_line in ss.bom_line_ids:
        for data_d in bom_line.date_set.split(','):
            for bom_line_child in bom_line.bom_line_child_ids:
                print([ss.studyname_id.id , data_d, ss.department_id.id, ss.create_uid.id, bom_line_child.product_id.id, bom_line_child.product_qty])

    good_info =[[0,"virtual_6002",
                    {
                    "company_id": 1,
                    "state": "draft",  # 草稿状态
                    "picking_type_id": 2,
                    "location_id": 8,
                    "location_dest_id": 5,
                    "additional": False,
                    "product_id": 2, # 物料名称
                    "name":"wuliao2",
                    "date": "2021-07-23 13:34:38",
                    "quantity_done": 16880, # 物料数量
                    "product_uom": 1, # 单位
                    "lot_ids": [[6,False,[]]]
                    }
                ]]


    ldate = {
        "is_locked": True,
        "immediate_transfer": False,
        "priority": "0",
        "partner_id": False,
        "picking_type_id": 2, #出入库类型
        "location_id": 8,
        "location_dest_id": 5,
        "scheduled_date": "2021-07-23 13:34:38",  # 时间日期
        "origin": False,
        "owner_id": False,
        "move_ids_without_package": good_info,
        "move_type": "direct",
        "user_id": 1, # 创建人 user_id
        "company_id": 1, # 公司ID compyan_id
        "note": False
    }
    self.env['stock.picking'].create(ldate)