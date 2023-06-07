# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command


class ResUsers(models.Model):
    _inherit = 'res.users'

    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop',
                              default=False)
    cooperative_id = fields.Many2one('registry_app.cooperatives',
                                     string='Registry App Cooperative',
                                     default=False)
    is_from_registry_app = fields.Boolean(
        string='Is User created from Registry App', default=False)


    def get_pref(self):
        if self.env.user:
            domain = [('id', '=', self.env.user.id)]
            action = \
                self.env.ref(
                    'base.view_users_form_simple_modif').sudo().read()[0]
            action['domain'] = domain
            for rec in action:
                print('rec  %', rec)
            return action


class RegistryAppShop(models.Model):
    _name = 'registry_app.shop'
    _description = 'Registry App Shop'
    _inherit = ['mail.thread']

    name = fields.Char(string=_('Name'), required=True,copy=False)
    user_id = fields.Many2one('res.users', string='Shop Owner',copy=False,
                              help="If set,the shop is only visible for this user for this user.")
    shop_users_ids = fields.Many2many('res.users', copy=False,
                                      string=_("Users"))
    cooperative_id = fields.Many2one('registry_app.cooperatives',
                                     default=lambda self: self.env.context.get(
                                         'cooperative_id', None,copy=False),
                                     help="This shop belongs to this particular cooperative")
    shop_logo = fields.Image(string=_("Logo"),copy=False)
    company_id = fields.Many2one('res.company', string=_('Company'),copy=False,
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    active = fields.Boolean(string=_('Active'), default=True)


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
        name = f'Registries for {self.name}'
        action = \
            self.env.ref(
                'registry_app.registry_app_action_window').sudo().read()[0]
        action['context'] = context
        action['domain'] = domain
        action['name'] = name
        return action

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
            self.user_id.update({
                'shop_id': self.id
            })
        if self.shop_users_ids:
            for user in self.shop_users_ids:
                user.update({
                    'shop_id': self.id
                })
        return super(RegistryAppShop, self).write(vals)
