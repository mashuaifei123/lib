/*** Charlie.Huang
 * */
odoo.define('app_web_one2many_multi_add.form_relational_extend_v11', function (require) {
"use strict";

    var ListRenderer = require('web.ListRenderer');
    var ListView = require('web.ListView');
    var registry = require('web.field_registry');
    var relational_fields = require('web.relational_fields');
    var KanbanRenderer = require('web.KanbanRenderer');
    var dialogs = require('web.view_dialogs');
    var core = require('web.core');
    var _t = core._t;

    var MultiListRenderer = ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
        'click .o_field_x2many_list_row_multi_add a': '_onAddMultiRecord',
    }),
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            if (parent.attrs && (parent.attrs.widget === 'multi_select_tree')){
                this.multi_select_tree = true;
            }
        },
        _renderRows: function () {
            var $rows = this._super();
            if (this.addCreateLine && this.multi_select_tree) {
                //var $a = $('<a href="#">').text(_t("Add an item"));
                $rows[$rows.length - 1].find('.o_field_x2many_list_row_add').attr('colspan', 2);
                var $multi_add = $('<a href="#">').text(_t('Multi Add Items'));
                var $td = $('<td>')
                            .attr('colspan', this._getNumberOfCols()-3)
                            .addClass('o_field_x2many_list_row_multi_add')
                            //.append($a)
                            .append($multi_add);

                $rows[$rows.length - 1].append($td);

            }
            return $rows;
    },
        _onAddMultiRecord: function (event) {
            // we don't want the browser to navigate to a the # url
            event.preventDefault();

            // we don't want the click to cause other effects, such as unselecting
            // the row that we are creating, because it counts as a click on a tr
            event.stopPropagation();

            // but we do want to unselect current row
            var self = this;
            this.unselectRow().then(function () {
                self.trigger_up('add_multi_record', {from_multi:true}); // TODO write a test, the deferred was not considered
            });

    },

    });
    //var MultiSlectionListView = ListView.extend({
    //    config: _.extend({}, ListView.prototype.config, {
    //        Renderer: MultiListRenderer,
    //    }),
    //});
    var MultiFieldOne2Many = relational_fields.FieldOne2Many.include({
        custom_events: _.extend({}, relational_fields.FieldOne2Many.prototype.custom_events, {
        add_multi_record: '_onAddMultiRecord',

    }),
        /**
     * Opens a SelectCreateDialog.
     *
     * @override
     * @private
     * @param {OdooEvent|MouseEvent} ev this event comes either from the 'Add
     *   record' link in the list editable renderer, or from the 'Create' button
     *   in the kanban view
     */
    _onAddMultiRecord: function (ev,from_multi) {
        var self = this;
        ev.stopPropagation();
        var res_model = this.attrs.res_model;
            var res_field = this.attrs.res_field;
            var ancestor = self.findAncestor(function(a)
                {
                return a.model instanceof Object
                }
            );
            var domain = self.value.getDomain({fieldName: res_field});

                var params = self.value;
            var dp = ancestor.model._makeDefaultRecord(params.model,{
                    modelName: params.model,
                    fields: params.fields,
                    fieldsInfo: params.fieldsInfo,
                    context: params.context,
                    parentID: self.dataPointID,
                    res_ids: params.res_ids,
                    viewType: params.viewType,
                }).then(function (id) {
                if (ancestor.model && ancestor.model.localData){
                    var context = ancestor.model.localData[id].getContext({fieldName: res_field})
                }else{
                    var context = self.record.getContext({fieldName: res_field});
                }

        new dialogs.SelectCreateDialog(self, {
            res_model: res_model,
            domain: domain,
            context: context,
            title: _t("Add: ") + self.view.fields[res_field].string,
            no_create: true,
            fields_view: self.attrs.views.form,
            on_selected: function (records) {
                    _.each(records, function (record) {
                        var data = {}
                        data[res_field] = {id:record.id}
                        self.trigger_up('edited_list', { id: self.value.id });
                        self._setValue({
                            operation: 'CREATE',
                            position: self.editable,
                            data: data
                        })
                    })
            }
        }).open();
                            //})
            });
    },
        /**
     * Instanciates or updates the adequate renderer.
     *
     * @override
     * @private
     * @returns {Deferred|undefined}
     */
    //_render: function () {
    //    if (!this.view) {
    //        return this._super();
    //    }
    //    if (this.renderer) {
    //        this.currentColInvisibleFields = this._evalColumnInvisibleFields();
    //        this.renderer.updateState(this.value, {'columnInvisibleFields': this.currentColInvisibleFields});
    //        this.pager.updateState({ size: this.value.count });
    //        return $.when();
    //    }
    //    var arch = this.view.arch;
    //    var viewType;
    //    if (arch.tag === 'tree') {
    //        viewType = 'list';
    //        this.currentColInvisibleFields = this._evalColumnInvisibleFields();
    //        this.renderer = new MultiListRenderer(this, this.value, {
    //            arch: arch,
    //            editable: this.mode === 'edit' && arch.attrs.editable,
    //            addCreateLine: !this.isReadonly && this.activeActions.create,
    //            addTrashIcon: !this.isReadonly && this.activeActions.delete,
    //            viewType: viewType,
    //            columnInvisibleFields: this.currentColInvisibleFields,
    //        });
    //    }
    //    if (arch.tag === 'kanban') {
    //        viewType = 'kanban';
    //        var record_options = {
    //            editable: false,
    //            deletable: false,
    //            read_only_mode: this.isReadonly,
    //        };
    //        this.renderer = new KanbanRenderer(this, this.value, {
    //            arch: arch,
    //            record_options: record_options,
    //            viewType: viewType,
    //        });
    //    }
    //    this.$el.addClass('o_field_x2many o_field_x2many_' + viewType);
    //    return this.renderer ? this.renderer.appendTo(this.$el) : this._super();
    //},
    });
    registry
        .add('multi_select_tree', MultiFieldOne2Many)

});