# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RegistryAppCooperatives(models.Model):
    _name = 'registry_app.cooperatives'
    _description = 'Cooperatives'

    name = fields.Char(string='Name', required=True,
                       help='Name of the Cooperative')
    shop_ids = fields.Many2many('registry_app.shop', copy=False, string="Shops",
                                help='List of shops that comes under this cooperatives')
    user_id = fields.Many2one('res.users', string='Cooperative Admin',
                              help="Set the admin user for this cooperative")
    active = fields.Boolean(string='Active', default=True)

    def goto_registry_shop(self):
        """Open all shops interface."""
        self.ensure_one()
        view_id = self.env.ref(
            'registry_app.registry_app_shop_view_kanban').id
        print('view_id', view_id)
        context = self._context.copy()
        return {
            'name': _('Shops'),
            'res_model': 'registry_app.shop',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban',
            'target': 'current',
            'view_id': view_id,
            'context': {'cooperative_id': self.id},
        }


class SaleCustom(models.Model):
    _name = 'sale.custom'

    @api.model
    def get_sale_order(self):
        ret_list = []
        req = (
            """select ra.name,ra.total_sales,ra.total_purchase,pd.name as sale_product,
rs.quantity,rc.partner_id,rsp.name as partner_name,pdp.name as purchase_product
from registry_app_registry_app as ra
inner join registry_app_sales as rs on ra.id = rs.registry_app_id
inner join product_template as pd on pd.id = rs.product_id
inner join registry_app_client as rc on rc.id = rs.client_id
inner join res_partner as rsp on rsp.id = rc.partner_id
inner join registry_app_purchase as rp on ra.id = rp.registry_app_id
inner join product_template as pdp on pdp.id = rp.product_id"""
        )
        self.env.cr.execute(req)
        for rec in self.env.cr.dictfetchall():
            ret_list.append(rec)
        print(ret_list)
        return ret_list

    @api.model
    def get_registry_log(self):
        ret_list = []
        registry_log = self.env['registry_app.registry_app'].search([])
        for rec in registry_log:
            sale_list = []
            purchase_list = []
            sale_list.clear()
            purchase_list.clear()
            for item in rec.sale_app_ids:
                sale_list.append((item.product_id.display_name, item.price, item.quantity, item.client_id.name))
            for exp in rec.purchase_app_ids:
                purchase_list.append((exp.product_id.display_name, exp.cost))
            print(sale_list, "sale_list")
            print(purchase_list, "purchase_list")
            reg_dict = {
                'name': rec.name,
                'sale_app_ids':sale_list,
                'purchase_app_ids': rec.purchase_app_ids,

            }
            ret_list.append(reg_dict)
        print(ret_list)
        return ret_list

