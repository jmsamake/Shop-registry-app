# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RegistryAppProduct(models.Model):
    _name = 'registry_app.product'
    _description = 'Registry Product'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.template', "Product", required=True,
                                 domain=[('id', '=', 0)])
    price = fields.Float(related='product_id.list_price', string='Price',
                         stored=True, default=0, readonly=False)
    cost = fields.Float(related='product_id.standard_price', stored=True,
                        string="Cost", default=0, readonly=False)

    # @api.model
    # def create(self, vals):
    #     # Create a new record in the products.product model
    #     product_vals = {
    #         'name': vals.get('name'),
    #         'price': vals.get('price'),
    #         'description': vals.get('description')
    #     }
    #     product = self.env['product.product'].create(product_vals)
    #
    #     # Create a new record in the registry_app.product model
    #     vals['product_id'] = product.id
    #     return super(RegistryAppProduct, self).create(vals)
