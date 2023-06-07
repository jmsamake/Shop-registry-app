# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class RegistryAppProduct(models.Model):
    _name = 'registry_app.product'
    _description = 'Registry Product'
    _rec_name = 'product_id'
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.template', "Product", required=True,
                                copy=False)
    name = fields.Char(string='Name', store=True,readonly=False)
    price = fields.Float(string='Price', default=0, readonly=False)
    cost = fields.Float(string="Cost", default=0, readonly=False)
    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop',copy=False)

    @api.model
    def create(self, values):
        print('values',values)
        product_template = self.env['product.template']
        new_product = product_template.create({
            'name': values['name'],
            'list_price': values['price'],
            'standard_price': values['cost'],
        })
        print(new_product, 'new_product')
        values.update({
            'shop_id':  self.env.user.shop_id.id,
            'product_id': new_product.id
        })
        print(values, 'values updated')
        return super(RegistryAppProduct, self).create(values)

    @api.model
    def write(self, values):
        print (values, 'values')
        product_values = {
            'name': values.get('name'),
            'list_price': values.get('price'),
            'standard_price': values.get('cost')
        }
        self.product_id.write(product_values)
        return super(RegistryAppProduct, self).write(values)

    def unlink(self):
        self.product_id.unlink()
        return super(RegistryAppProduct, self).unlink()
