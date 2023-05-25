# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RegistryAppUsers(models.Model):
    _name = 'registry_app.users'
    _description = 'Registry User'
    _inherit = ['mail.thread']

    # name = fields.Char(required=True, string=_("Name"))
    user_id = fields.Many2one('res.users', delegate=True, ondelete='cascade',
                              string=_("User ID"),copy=False)
    name = fields.Char(required=True, string=_("Name"),copy=False)
    login = fields.Char(related='user_id.login', store=True, readonly=False,
                        string='Email', required=True,copy=False)
    cooperative_id = fields.Many2one('registry_app.cooperatives',copy=False,
                                     string='Registry App Cooperatives',
                                     default=False)
    password = fields.Char(related='user_id.password', store=False,copy=False,
                           readonly=False, string='Password', required=True)
    registry_user_group = fields.Selection(
        [('registry_app_cooperative_owner', 'Cooperative Owner'),
         ('registry_app_shop_owner', 'Shop Owner'),
         ('registry_app_user', 'Registry App User'),
         ], required=True,copy=False)

    @api.model
    def create(self, vals):
        logged_user = self.env.user
        if logged_user.has_group('registry_app.registry_app_shop_owner'):
            vals['registry_user_group'] = 'registry_app_user'
        elif logged_user.has_group(
                'registry_app.registry_app_cooperative_owner'):
            print('reg coop')
            vals['registry_user_group'] = 'registry_app_shop_owner'
        print(vals['registry_user_group'], 'DDDD')
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
        if log_user.cooperative_id:
            domain = [('id', '=', log_user.cooperative_id.id)]
        else:
            domain = [('user_id', '=', log_user.id)]
        coop_id = self.env['registry_app.cooperatives'].search(domain).id
        if not logged_user.has_group(
                'registry_app.registry_app_super_admin') and not coop_id:
            raise ValidationError(
                f"{logged_user.name}, doesn't belong to any cooperatives. "
                f"Make sure they are in a cooperative.")

        print('coop_id', coop_id)
        user_data = {
            'name': vals['name'],
            'login': vals['login'],
            'password': vals['password'],
            'email': vals['login'],
            'groups_id': [(4, group_id), (4, group_internal_user)],
            'is_from_registry_app': True,
            'cooperative_id': coop_id,
            # 'shop_id': coop_id,
        }
        new_user = self.env['res.users'].sudo().create(user_data)
        vals['user_id'] = new_user.id
        vals['cooperative_id'] = coop_id
        print(vals,'vals')
        return super(RegistryAppUsers, self).create(vals)
