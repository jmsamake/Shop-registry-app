# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class RegistryAppPurchase(models.Model):
    _name = 'registry_app.purchase'
    _description = 'Purchase Registries'
    _inherit = ['mail.thread']

    # name = fields.Char(string='Name', required=True)
    product_id = fields.Many2one('registry_app.product', string=_('Product'),copy=False )
    cost = fields.Float(related='product_id.cost', readonly=False,copy=False)
    registry_app_id = fields.Many2one('registry_app.registry_app',copy=False)
    client_id = fields.Many2one('registry_app.client', string=_('Client'),copy=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company",copy=False)
    active = fields.Boolean(string=_('Active'), default=True)
