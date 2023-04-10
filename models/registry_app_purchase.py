# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class RegistryAppPurchase(models.Model):
    _name = 'registry_app.purchase'
    _description = 'Purchase Registries'

    # name = fields.Char(string='Name', required=True)
    product_id = fields.Many2one('product.template', string=_('Product'), )
    cost = fields.Float()
    registry_app_id = fields.Many2one('registry_app.registry_app')
    client_id = fields.Many2one('registry_app.client', string=_('Client'))
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    active = fields.Boolean(string=_('Active'), default=True)


