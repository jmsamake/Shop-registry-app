/** @odoo-module **/
import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';


$("js-example-basic-multiple").select2(
{
  maximumSelectionLength: 2
});

var rpc = require('web.rpc');
var session = require('web.session');
var userId = session.uid;

var ExampleWidget = Widget.extend({
    template: 'QuickLanguageSystray',
    events: {
        'click #change_lang': '_onClick',
    },
    _onClick: function () {
        var self = this;

        rpc.query({
            model: 'res.users',
            method: 'get_pref',
            args: [
                [userId]
            ],
        }).then(function (data) {
            console.log(data.id)
            self.do_action({
                type: 'ir.actions.act_window',
                name: 'res users',
                res_model: 'res.users',
                view_mode: 'form',
                res_id: userId,
                views: [[data.id, 'form']],
                target: 'new'
            });
        })

        // this.do_action({
        //      type: 'ir.actions.act_window',
        //      name: 'Sale Order',
        //      res_model: 'sale.order',
        //      view_mode: 'form',
        //      views: [[false, 'form']],
        //      target: 'new'
        // });
    },
});
SystrayMenu.Items.push(ExampleWidget);
export default ExampleWidget;