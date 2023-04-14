/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
const { Component} = owl;
console.log("owl",owl);
export class SwitchLanguageMenu extends Component {
    async setup() {
        var session = require('web.session');
        var self = this;
        var rpc = require('web.rpc');
        var languages =await  rpc.query({
            model: 'res.lang',
            method: 'search_read',
            args: [[],['name', 'code']],
        }).then(function (res) {
            return res;
        });
        console.log(languages,"languages");
        self.languages = languages;
        self.currentLanguage = session.user_context.lang;
        }

    async logIntoLanguage(language) {
        var self = this;
        var session = require('web.session');
        var rpc = require('web.rpc');
        let is_changed=await rpc.query({
            model: 'res.users',
            method: 'write',
            args: [session.uid, {'lang':language['code']}],
        }).then(function (result) {
            return result;
            //
        });
        if(is_changed){
            window.location.reload();
        }
        };
}
SwitchLanguageMenu.template = "registry_app.SwitchLanguageMenu";
SwitchLanguageMenu.toggleDelay = 1000;
SwitchLanguageMenu.components = { Dropdown, DropdownItem };
const systrayItem = {
    Component: SwitchLanguageMenu,
    isDisplayed(env) {
        return Object.keys([]);
    },
};
registry.category("systray").add("SwitchLanguageMenu", systrayItem, { sequence: 2 })