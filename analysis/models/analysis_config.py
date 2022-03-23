import datetime
from inspect import isasyncgenfunction
from uuid import NAMESPACE_OID
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np

class Ana_position(models.Model):
    _name = 'analysis.ana.position'
    _description = 'Analysis Position '
    _parent_store = True
    _parent_name = "parent_id" 
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('位置', required=True)
    complete_name = fields.Char("完整位置", compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one(
        'analysis.ana.position',
        string='父位置',
        ondelete='restrict',
        index=True
    )
    child_ids = fields.One2many(
        'analysis.ana.position', 'parent_id',
        string='子位置')
    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! 不能创建递归的位置.')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id :
                location.complete_name = '%s/%s' % (location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name


    # def name_get(self):
    #     result=[]
    #     def recursive(xxxx,name):
    #         if  xxxx.parent_id:
    #             name1 = xxxx.parent_id.name +'_'+ name
    #             print(name1)
    #             return recursive(xxxx.parent_id,name1)
    #         else:
    #             return name
    #     for record in self:
    #         if not record.child_ids:
    #             name = recursive(record,record.name)
    #             result.append((record.id,name))
    #     return result

class AnimalSpecies(models.Model):
    _name = 'analysis.animalspecies'
    _description = 'Analysis AnimalSpecies'
    _rec_name = 'animalspecies'

    animalspecies = fields.Char('动物种属', required=True)


class Matrix(models.Model):
    _name = 'analysis.matrix'
    _description = 'Analysis Matrix'
    _rec_name = 'matrix'

    matrix = fields.Char('基质类型', required=True)


class MatrixType(models.Model):
    _name = 'analysis.matrixtype'
    _description = 'Analysis MatrixType'
    _rec_name = 'matrix_type'

    matrix_type = fields.Char('基质类别', required=True)


# class Gender(models.Model):
#     _name = 'analysis.gender'
#     _description = 'Analysis Gender'
#     _rec_name = 'gender'

#     gender = fields.Char('性别', required=True)


class Anticoagulant(models.Model):
    _name = 'analysis.anticoagulant'
    _description = 'Analysis Anticoagulant'
    _rec_name = 'anticoagulant'

    anticoagulant = fields.Char('抗凝/促凝', required=True)


class Note(models.Model):
    _name = 'analysis.note'
    _description = 'Analysis Note'
    _rec_name = 'note'

    note= fields.Char('备注', required=True)


class AnaPickingType(models.Model):
    _name = "ana.stock.picking.type"
    _description = "Ana Picking Type"
    _rec_name = 'operation_name'

    operation_name = fields.Char('Operation Type', required=True)
    sequence = fields.Integer(
        'Sequence', help="Used to order the 'All Operations' kanban view")
    sequence_code = fields.Char('Code', required=True)
    code = fields.Selection(
        [('incoming', 'Receipt'), ('outgoing', 'Delivery'),('choose', 'Choose')], 'Type of Operation', required=True)
    sequence_id = fields.Many2one(
        'ir.sequence', 'Reference Sequence',
        copy=False)


class AnaPickingAim(models.Model):
    _name = "ana.stock.picking.aim"
    _description = "Ana Picking aim"
    _rec_name = 'aim'

    aim = fields.Char('Operation Aim', required=True)





