# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command


class ResUsers(models.Model):
    _inherit = 'res.users'

    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop',
                              default=False)


class RegistryAppShop(models.Model):
    _name = 'registry_app.shop'
    _description = 'Registry App Shop'

    name = fields.Char(string=_('Name'), required=True)
    user_id = fields.Many2one('res.users', string='Shop Owner',
                              help="If set,the shop is only visible for this user for this user.")
    shop_users_ids = fields.Many2many('res.users', copy=False,
                                      string=_("Users"))
    cooperative_id = fields.Many2one('registry_app.cooperatives',
                                     default=lambda self: self.env.context.get(
                                         'cooperative_id', None),
                                     help="This shop belongs to this particular cooperative")
    shop_logo = fields.Image(string=_("Logo"))
    company_id = fields.Many2one('res.company', string=_('Company'),
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    active = fields.Boolean(string=_('Active'), default=True)

    # user_name = fields.Char(string='User Name',
    #                         help="Provide a user name for login")
    # password = fields.Char(string='Password',
    #                        help="Provide a Password for login")

    def open_registry_shop(self):
        """Open each shops registry interface."""
        self.ensure_one()
        view_id = self.env.ref('registry_app.form').id
        print('view_id', view_id)
        context = self._context.copy()
        return {
            'res_model': 'registry_app.registry_app',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'target': 'current',
            'view_id': view_id,
            'context': {'shop_id': self.id},
        }

    def open_tree_view(self):
        context = {'shop_id': self.id}
        domain = [('shop_id', '=', self.id)]
        name = f'Registries for %s' % self.name
        action = \
            self.env.ref(
                'registry_app.registry_app_action_window').sudo().read()[0]
        action['context'] = context
        action['domain'] = domain
        action['name'] = name
        return action
        # view_id = self.env.ref('registry_app.registry_app_list').id,
        # return {
        #     'name': f'Registries for {self.name}' or 'Registries',
        #     'res_model': 'registry_app.registry_app',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'target': 'current',
        #     'view_id': view_id,
        #     'context': {'shop_id': self.id},
        #     'domain': [('shop_id', '=', self.id)]
        # }

    @api.model
    def create(self, values):
        """Override default Odoo create function and extend."""
        res = super().create(values)
        if res.user_id:
            res.user_id.write({
                'shop_id': res.id
            })
        if res.shop_users_ids:
            for user in res.shop_users_ids:
                user.write({
                    'shop_id': res.id
                })
        cooperative = self.env['registry_app.cooperatives'].browse(
            self._context.get('cooperative_id'))
        values.update({
            'cooperative_id': self._context.get('cooperative_id')
        })
        # cooperative.shop_ids = [(4, 0, res.id)]
        cooperative.write({'shop_ids': [Command.link(res.id)]})
        return res

    def open_settings(self):
        return {
            'res_model': 'registry_app.shop',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'current'
        }

    def write(self, vals):
        """Adding the shop_id to users model"""
        if self.user_id:
            self.user_id.write({
                'shop_id': self.id
            })
        if self.shop_users_ids:
            for user in self.shop_users_ids:
                user.write({
                    'shop_id': self.id
                })
        return super(RegistryAppShop, self).write(vals)



# def login_btn(self):
#     view_id = self.env.ref('registry_app.login_wizard_view').id
#     return {
#         'name': '',
#         'res_model': 'login.wizard',
#         'type': 'ir.actions.act_window',
#         'view_mode': 'form',
#         'target': 'new',
#         'view_id': view_id,
#         'context': {'shop_id': self.id},
#     }

# @api.constrains('password')
# def check_password_strength(self):
#     """password length check"""
#     if self.password:
#         if len(self.password) < 5:
#             raise ValidationError(
#                 'Please provide a password with at least 5 characters')


# class LoginWizard(models.TransientModel):
#     _name = 'login.wizard'
#
#     name = fields.Char(string="Username", )
#     password = fields.Char(string="Password", )
#
#     def login(self):
#         shop_details = self.env['registry_app.shop'].browse(
#             self._context.get('shop_id'))
#         # view_id = self.env.ref('registry_app.form').id
#         context = self._context.copy()
#         if self.name == shop_details.user_name and self.password == shop_details.password:
#             print('successfully logged in')
#             # return {
#             #     'res_model': 'registry_app.registry_app',
#             #     'type': 'ir.actions.act_window',
#             #     'view_mode': 'form',
#             #     'target': 'current',
#             #     'view_id': view_id,
#             #     'context': context,
#             # }
#             action = self.env.ref(
#                 'registry_app.registry_app_past_login_action_window').read()[0]
#             return action
#         else:
#             raise ValidationError(_('Invalid username or password'))
