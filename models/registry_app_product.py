# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RegistryAppProduct(models.Model):
    _name = 'registry_app.product'
    _description = 'Registry Product'
    _rec_name = 'product_id'
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.template', "Product", required=True,
                                 domain=[('id', '=', 0)],copy=False)
    price = fields.Float(related='product_id.list_price', string='Price',
                         stored=True, default=0, readonly=False)
    cost = fields.Float(related='product_id.standard_price', stored=True,
                        string="Cost", default=0, readonly=False)
    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop',copy=False)

    @api.model
    def create(self, values):
        print('values',values)
        values.update({
            'shop_id':  self.env.user.shop_id.id
        })
        print(values, 'values')
        return super(RegistryAppProduct, self).create(values)
