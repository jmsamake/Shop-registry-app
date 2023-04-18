/** @odoo-module **/
// import { Component } from "@odoo/owl";
const { Component } = owl;
console.log("test")
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
// import { patch } from "@web/core/utils/patch";
import { patch } from 'web.utils';
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var _t = core._t;

//patching the menu items
patch(DropdownItem.prototype, "menu_lock", {
    //onclick function of menu item
    async onClick(ev) {
        var _super = this._super;
        ev.preventDefault()
        var session = require('web.session');
        var userId = session.uid;
        console.log(this.props)
        // var currentMenu = this.props.dataset.section
        var currentMenu = this.props.payload.id
        console.log(currentMenu,'menu')
        //rpc query to get values about password lock from res.users
        await rpc.query({
            model: 'res.users',
            method: 'menu_lock_search',
            args: [
                [userId]
            ],
        }).then(function(data) {
            //checking the current menu in menus to lock
            var menu = data.multi_lock_ids.filter(obj => {
                return parseInt(obj.id) === parseInt(currentMenu)
            })
            //if current menu is lock menu
            if (menu.length != 0 && menu[0].id && menu[0].password) {
                //Open dialog box to login
                var dialog = new Dialog(this, {
                    title: "Menu Security PIN",
                    $content: $(QWeb.render('menuLockPopup', {
                        role: 'alert',
                    })),
                    size: 'medium',
                    buttons: [{
                            text: _t("confirm"),
                            classes: 'btn-primary check_password',
                            click: false,
                        },
                        {
                            text: _t("Cancel"),
                            close: true
                        },
                    ],
                });
                cosole.log('asdsadsa')
                dialog.opened().then(() => {
                    //dialog box confirm button function
                    dialog.buttons[0].click = function(event) {
                        var current_pwd = $('#password').val()
                        //if password matches
                        if (current_pwd == menu[0].password) {
                            dialog.close();
                            _super(ev);
                        } else {
                            $('#wrong_password_alert').show();
                        }
                    };
                });
                dialog.open();
            } else {
                _super(ev);
            }
        })
    }
});