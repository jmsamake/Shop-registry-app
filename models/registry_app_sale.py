# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RegistryAppSales(models.Model):
    _name = 'registry_app.sales'
    _description = 'Sales Registries'
    _inherit = ['mail.thread']

    # name = fields.Char(string='Name', required=True)
    product_id = fields.Many2one('registry_app.product', string=_('Product'),copy=False,domain=lambda self: [('shop_id', '=', self.env.user.shop_id.id)])
    price = fields.Float(related='product_id.price', readonly=False,copy=False)
    quantity = fields.Integer(string=_('Quantity'), default=1,copy=False)
    registry_app_id = fields.Many2one('registry_app.registry_app',copy=False)
    client_id = fields.Many2one('registry_app.client', string=_('Client'),copy=False, domain=lambda self: [('shop_id', '=', self.env.user.shop_id.id)])
    company_id = fields.Many2one('res.company', string='Company',copy=False,
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    active = fields.Boolean(string=_('Active'), default=True)

    @api.onchange('quantity', 'price')
    def _compute_calculated_price(self):
        for record in self:
            record.price = record.quantity * record.product_id.price
