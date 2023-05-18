# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RegistryAppSales(models.Model):
    _name = 'registry_app.sales'
    _description = 'Sales Registries'
    _inherit = ['mail.thread']

    # name = fields.Char(string='Name', required=True)

    product_id = fields.Many2one('registry_app.product', string=_('Product'), )
    # price = fields.Float()
    price = fields.Float(related='product_id.price', readonly=False)
    quantity = fields.Integer(string=_('Quantity'), default=1)
    registry_app_id = fields.Many2one('registry_app.registry_app')
    client_id = fields.Many2one('registry_app.client', string=_('Client'))
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    active = fields.Boolean(string=_('Active'), default=True)

    @api.onchange('quantity', 'price')
    def _compute_calculated_price(self):
        for record in self:
            record.price = record.quantity * record.product_id.price
