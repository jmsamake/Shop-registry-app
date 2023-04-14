# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class RegistryAppUsers(models.Model):
    _name = 'registry_app.users'
    _description = 'Registry User'

    # name = fields.Char(string='Name', required=True)
    user_id = fields.Many2one('res.users', delegate=True, ondelete='cascade',
                              required=True, string=_("Name"))
    login = fields.Char(related='user_id.login', store=True, readonly=False,
                        string='Email', required=True)
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
                                     domain="[('parent_id','=',False)]" ,related='user_id.menus_to_lock')
    # multi_lock_ids = fields.One2many('menu.password', 'password_id', string=" ")

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
