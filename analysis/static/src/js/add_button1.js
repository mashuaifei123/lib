odoo.define('analysis.ana.stock.picking.add.button1', function (require) {
    "use strict";
	var ajax = require('web.ajax');
    let ListController = require('web.ListController');

    ListController.include({
        renderButtons: function ($node) {
            let $buttons = this._super.apply(this, arguments);
            let tree_model = this.modelName;
            let context = this.initialState.context.add_button;
            // 只在模型的tree视图中出现
            if (context && tree_model === 'ana.stock.picking') {
                let but2 = "<button type=\"button\" t-if=\"widget.modelName == 'ana.stock.picking'\" class=\"btn btn-primary\"  context=\"{'default_ana_picking_type_id':1}\">存入</button>";
                let button2 = $(but2).click(this.proxy('add_button_form1'));
                // this.$buttons.prepend(button2);   //放在前面
                this.$buttons.append(button2);   // 放在后面
            }
            return $buttons;
        },
        // 按钮功能：弹出取的form视图
        add_button_form1: function () {
            let action = {
                name: '存入',
                type: 'ir.actions.act_window',
                res_model: 'ana.stock.picking',
                view_mode: 'form',
                view_type: 'form',
                target: 'current',
                views: [[false,'form']],
                context: {'deault_ana_picking_type_id': 1}

            };
            let self = this;
            this.do_action(action, {
                on_close: function () {
                    self.trigger_up('reload');
                }
            });
        },
        // 按钮功能，调用一个ana.stock.picking模块中的函数
        course_test_button_fuc: function () {
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model: 'ana.stock.picking',
                method: '_default_choose2',
                args: [],
                kwargs: {}
            }).then(function (url) {

            });
        },
    });

});
