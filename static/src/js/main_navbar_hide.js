odoo.define('registry_app.main_navbar_hide', function (require) {
  var ajax = require('web.ajax');
  var rpc = require('web.rpc');

  function checkHideNavbar() {
    rpc.query({
      model: 'sale.custom',
      method: 'get_user_details',
      domain: [],
      args: [],
    }).then(function (result) {
      var isFromRegistryApp = result[0].is_from_registry_app;
      if (!isFromRegistryApp) {
        $('#oe_main_menu_navbar').show();
        $('#oe_main_menu_navbar').css("z-index", "1040");
      }
    });
  }


    // Run the function initially
    checkHideNavbar();

    // Run the function periodically
    // setInterval(checkHideNavbar, 1000); // Run every second (adjust the interval as needed)
});
