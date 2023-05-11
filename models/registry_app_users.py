# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RegistryAppUsers(models.Model):
    _name = 'registry_app.users'
    _description = 'Registry User'

    # name = fields.Char(required=True, string=_("Name"))
    user_id = fields.Many2one('res.users', delegate=True, ondelete='cascade',
                              string=_("User ID"))
    name = fields.Char(required=True, string=_("Name"))
    login = fields.Char(related='user_id.login', store=True, readonly=False,
                        string='Email', required=True)
    cooperative_id = fields.Many2one('registry_app.cooperatives',
                                     string='Registry App Cooperatives',
                                     default=False)
    password = fields.Char(related='user_id.password', store=True,
                           readonly=False, string='Password', required=True)
    # password_lock = fields.Selection(
    #     [('single_password', 'Enable Password Lock'),
    #      # ('multi_password', 'Multi Password Lock')
    #      ])
    password_lock = fields.Selection(related='user_id.password_lock',
                                     store=True, readonly=False,
                                     string='App Lock')
    login_pswd = fields.Char(related='user_id.login_pswd', store=True,
                             readonly=False, string='Registry App Password')
    menus_to_lock = fields.Many2many('ir.ui.menu', string="Menus to lock",
                                     domain="[('parent_id','=',False)]",
                                     related='user_id.menus_to_lock',
                                     readonly=False, )
    registry_user_group = fields.Selection(
        [('registry_app_cooperative_owner', 'Cooperative Owner'),
         ('registry_app_shop_owner', 'Shop Owner'),
         ('registry_app_user', 'Registry App User'),
         ], required=True)

    # multi_lock_ids = fields.One2many('menu.password','password_id',string="")
    @api.model
    def create(self, vals):
        group_id = self.env.ref(
            'registry_app.' + vals['registry_user_group']).id
        group_internal_user = self.env.ref('base.group_user').id
        log_user = self.env['res.users'].browse(self.env.user.id)
        domain = []
        print('asd', log_user.shop_id.cooperative_id)
        if log_user.shop_id.cooperative_id:
            print('if')
            domain = ['|', ('user_id', '=', log_user.id),
                      ('id', '=', log_user.shop_id.cooperative_id.id)]
        else:
            print("else")
            domain = [('user_id', '=', log_user.id)]
        print('domain', domain)
        coop_id = self.env['registry_app.cooperatives'].search(domain).id
        print('coop_id', coop_id)
        user_data = {
            'name': vals['name'],
            'login': vals['login'],
            'password': vals['password'],
            'email': vals['login'],
            'password_lock': vals['password_lock'],
            'login_pswd': vals['login_pswd'],
            'menus_to_lock': vals['menus_to_lock'],
            'groups_id': [(4, group_id), (4, group_internal_user)],
            'is_from_registry_app': True,
            'cooperative_id': coop_id
        }
        new_user = self.env['res.users'].sudo().create(user_data)
        vals['user_id'] = new_user.id
        vals['cooperative_id'] = coop_id
        return super(RegistryAppUsers, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     # Create a new record in the res.users model
    #     user_vals = {
    #         'name': vals.get('name'),
    #         'login': vals.get('email'),
    #         'password': vals.get('password'),
    #     }
    #     user = self.env['res.users'].create(user_vals)
    #
    #     # Create a new record in the registry_app.users model
    #     vals['user_id'] = user.id
    #     return super(RegistryAppUsers, self).create(vals)
