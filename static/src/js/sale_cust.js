odoo.define('client_act.sale_cust', function (require) {
   'use strict';
   var AbstractAction = require('web.AbstractAction');
   var core = require('web.core');
   var rpc = require('web.rpc');
   var QWeb = core.qweb;
   var SaleCustom = AbstractAction.extend({
   template: 'SaleCust',
       events: {
       },
       init: function(parent, action) {
           this._super(parent, action);
       },
       start: function() {
           var self = this;
           self.load_data();
       },
       load_data: function () {
           var self = this;
                   var self = this;
                   self._rpc({
                       model: 'sale.custom',
                       method: 'get_registry_log',
                       args: [],
                   }).then(function(datas) {
                       console.log(typeof(datas))
                       self.$('.table_view').html(QWeb.render('SaleTable', {
                                  report_lines : datas,
                       }));
                   });
           },
   });
   core.action_registry.add("sale_cust", SaleCustom);
   return SaleCustom;
});
// odoo.define('client_act.sale_cust', function (require) {
//    'use strict';
//    var AbstractAction = require('web.AbstractAction');
//    var core = require('web.core');
//    var rpc = require('web.rpc');
//    var QWeb = core.qweb;
//    var SaleCustom = AbstractAction.extend({
//    // template: 'SaleCust',
//    //     events: {
//    //     },
//        init: function(parent, action) {
//            this._super(parent, action);
//        },
//        start: function() {
//            var self = this;
//            self.load_data();
//            // self.redirect()
//
//        },
//        load_data: function () {
//            var self = this;
//                    var self = this;
//                    self._rpc({
//                        model: 'registry_app.registry_app',
//                        method: 'my_server_action',
//                        args: [[]],
//                    }).then(function(data) {
//                        console.log(data)
//                        // this.action=datas
//                        // self.$('.table_view').html(QWeb.render('SaleTable', {
//                        //            report_lines : datas,
//                        // }));
//                    });
//            },
//    //     redirect: function(){
//    //     window.location.href = '/registry_app/registry_app';
//    //     //     window.location.href = '/web/session/logout?redirect=/registry_app/registry_app';
//    //
//    //
//    //     },
//    });
//    core.action_registry.add("sale_cust", SaleCustom);
//    return SaleCustom;
// });