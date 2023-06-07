/** @odoo-module **/


import { NavBar } from "@web/webclient/navbar/navbar";
import { registry } from "@web/core/registry";
const { fuzzyLookup } = require('@web/core/utils/search');
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ErrorHandler, NotUpdatable } from "@web/core/utils/components";
import core from 'web.core';

// ss
var session = require('web.session');
console.log('session',session)
console.log('NavBar',NavBar)
const systrayRegistry = registry.category("systray");


// Extend the NavBar class
export class CustomNavBar extends NavBar {
    // My custom function
    isRegistryAppUser() {
        console.log(session.is_registry_app_user, 'ok');
        return session.is_registry_app_user;
    }

}

// Update the template and components properties if needed
CustomNavBar.template = "web.NavBar";
CustomNavBar.components = { Dropdown, DropdownItem, NotUpdatable, ErrorHandler };

export default CustomNavBar;
