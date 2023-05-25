odoo.define('registry_app.main_navbar_hide', function (require) {
  var ajax = require('web.ajax');
  var rpc = require('web.rpc');
  var session = require('web.session');

  console.log('adsad');

  $(document).ready(function () {
    rpc.query({
      model: 'sale.custom',
      method: 'get_user_details',
      domain: [],
      args: [],
    }).then(function (result) {
      console.log('result', result[0]);
      console.log('test');
      var isFromRegistryApp = result[0].is_from_registry_app;
      if (isFromRegistryApp) {
        $('.o_main_navbar').hide();
        // $('.o_connected_user').addClass('registry-app-connected-user'); // Add !important here
        // $('#oe_main_menu_navbar').hide();
      }
    });
  });
});
