# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RegistryAppCooperatives(models.Model):
    _name = 'registry_app.cooperatives'
    _description = 'Cooperatives'
    _inherit = ['mail.thread']

    name = fields.Char(string=_('Name'), required=True,
                       help=_('Name of the Cooperative'))
    shop_ids = fields.Many2many('registry_app.shop', copy=False,
                                string=_('Shops'),
                                help=_(
                                    'List of shops that comes under this cooperatives'))
    user_id = fields.Many2one('res.users', string=_('Cooperative Admin'),
                              help=_('Set the admin user for this cooperative'), copy=False)
    active = fields.Boolean(string=_('Active'), default=True)

    def goto_registry_shop(self):
        self.id
        print(self.id, '=====self======')
        print(self.env.user.cooperative_id, '======coop_id=====')
        """Open all shops interface."""
        view_id = self.env.ref(
            'registry_app.registry_app_shop_action_window').id
        action = self.env.ref(
            'registry_app.registry_app_shop_action_window').sudo().read()[0]
        action['target'] = 'current'
        action['view_mode'] = 'tree,kanban,form'
        action['context'] = {'cooperative_id': self.id}
        action['domain'] = [('cooperative_id', '=', self.id)]
        return action

    @api.model
    def create(self, values):
        """Override create function and Adding the cooperative_id to users
        model."""
        res = super().create(values)
        if res.user_id:
            print(res.user_id, 'userid')
            reg_user = self.env['registry_app.users'].search(
                [('user_id', '=', self.user_id.id)])
            print(reg_user, 'reg_user')
            res.user_id.write({
                'cooperative_id': res.id
            })
            reg_user.write({
                'cooperative_id': res.id
            })
        return res

    def write(self, vals):
        """Override write function and Adding the cooperative_id to users
        model"""
        if self.user_id:
            reg_user = self.env['registry_app.users'].search(
                [('user_id', '=', self.user_id.id)])
            print('Writing', reg_user)
            reg_user.write({
                'cooperative_id': self.id
            })
            self.user_id.write({
                'cooperative_id': self.id
            })
        return super(RegistryAppCooperatives, self).write(vals)


class SaleCustom(models.Model):
    _name = 'sale.custom'

    @api.model
    def get_registry_log(self):
        ret_list = []
        registry_log = self.env['registry_app.registry_app'].search(
            [('shop_id', '=', self.env.user.shop_id.id)])
        for rec in registry_log:
            print(rec)
            sale_list = []
            purchase_list = []
            sale_list.clear()
            purchase_list.clear()
            for item in rec.sale_app_ids:
                sale_list.append((item.product_id.display_name, item.price,
                                  item.quantity, item.client_id.name))
            for exp in rec.purchase_app_ids:
                purchase_list.append((exp.product_id.display_name, exp.cost))
            print(sale_list, "sale_list")
            print(purchase_list, "purchase_list")
            reg_dict = {
                'name': rec.name,
                'sale_app_ids': sale_list,
                'purchase_app_ids': purchase_list,
                'total_sales': rec.total_sales,
                'total_purchase': rec.total_purchase,
                'shop_owner': rec.registry_user_id.name,
                'shop': rec.shop_id.name
            }
            ret_list.append(reg_dict)
        print(ret_list)
        return ret_list

    @api.model
    def get_user_details(self):
        result = self.env['res.users'].browse(self.env.user.id).is_from_registry_app
        print('result',result)
        return [{'is_from_registry_app' : result}]
