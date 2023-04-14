
"""res users inherit"""

from odoo import api, fields, models


class UserInherit(models.Model):
    """inherited the res_users model."""
    _inherit = 'res.users'

    password_lock = fields.Selection(
        [('single_password', 'Enable Password Lock'),
         # ('multi_password', 'Multi Password Lock')
         ])
    login_pswd = fields.Char('Login Password')
    menus_to_lock = fields.Many2many('ir.ui.menu', string="Menus to lock",
                                     domain="[('parent_id','=',False)]")
    multi_lock_ids = fields.One2many('menu.password', 'password_id', string=" ")

    @api.model
    def menu_lock_search(self, args):
        """method to returning values though args"""
        user = self.env['res.users'].browse(args[0])
        return {
            'multi_lock_ids': [{
                'id': menu.menus_id.id,
                'password': menu.password
            } for menu in user.multi_lock_ids]
        }

    @api.onchange('menus_to_lock')
    def create_multi_menus(self):
        """method to add fields from single password option to one-to-many of
         multi password with same password in onchange of the field"""
        if self.password_lock == 'single_password':
            new_lines = [(5, 0, 0)]
            for rec in self.menus_to_lock:
                new_lines.append(
                    (0, 0, {'menus_id': rec._origin.id,
                            'password': self.login_pswd,
                            }))
            self.write({'multi_lock_ids': new_lines})


class MenuPassword(models.Model):
    """Inverse model for one to many field"""
    _name = 'menu.password'
    _description = 'Menus and Corresponding Locks for multiple password lock ' \
                   'conditions'

    menus_id = fields.Many2one('ir.ui.menu', string="Menus",
                               domain="[('parent_id','=',False)]")
    password = fields.Char('Login Password')
    password_id = fields.Many2one('res.users')
