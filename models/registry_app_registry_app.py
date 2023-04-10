# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class RegistryApp(models.Model):
    _name = 'registry_app.registry_app'
    _description = 'Registry App'
    _inherit = ['mail.thread']

    name = fields.Char(string=_('Name'), required=True, tracking=True)
    shop_id = fields.Many2one('registry_app.shop')
    sale_app_ids = fields.One2many('registry_app.sales', 'registry_app_id')
    purchase_app_ids = fields.One2many('registry_app.purchase',
                                       'registry_app_id')
    total_sales = fields.Float(string=_('Total Sales'),
                               compute='_compute_registry_sale_total',
                               store=True)
    total_purchase = fields.Float(string=_('Total Purchase'),
                                  compute='_compute_registry_purchase_total',
                                  store=True)
    description = fields.Text()
    state = fields.Selection(selection=[
        ('opened', _('Opened')),
        ('validated', _('Validated')),
        ('closed', _('Closed')),
        ('cancelled', _('Cancelled')),
        # ('archived', 'Archived'),
    ], string="State",
        default='opened')
    registry_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                       string=_('Salesperson'),
                                       default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged user Company")
    active = fields.Boolean(string=_('Active'), default=True)

    def close_input(self):
        print('entereed')
        self.state = 'closed'

    def validate(self):
        self.state = 'validated'

    def send_sms(self):
        # my_sms = self.env['sms.composer'].create({'numbers': '+916282717330',
        #                                           'body': 'New lead has been created in Odoo'})
        # print('my_sms', my_sms)
        # my_sms.action_send_sms()
        view_id = self.env.ref('registry_app.view_sms_broadcast_form').id

        return {
            'res_model': 'regsmsbroadcast',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id,
            # 'context': {'shop_id': self.id},
        }

    def cancel(self):
        self.state = 'cancelled'

    def reset(self):
        self.state = 'opened'

    # def write(self, vals):
    #     res = super(RegistryApp, self).write(vals)
    #     if vals.get('active'):
    #         for record in self:
    #             if record.active and record.state != 'archived':
    #                 record.state = 'archived'
    #     return res

    # @api.constrains('active')
    # def _check_state(self):
    #     print('active', self.active)
    #     if not self.active:
    #         self.state = 'archived'

    # @api.model
    # def send_sms(self, message, partner_ids=None):
    #     sms_template = self.env.ref('base_sms_demo.sms_template',
    #                                 raise_if_not_found=False)
    #     sms_template.with_context(default_model='res.partner').send_sms(
    #         partner_ids, message=message)

    # computing total cost for showing in tree view
    @api.depends('purchase_app_ids')
    def _compute_registry_purchase_total(self):
        self.total_purchase = sum(self.purchase_app_ids.mapped('cost'))

    # computing total price for showing in tree view
    @api.depends('sale_app_ids')
    def _compute_registry_sale_total(self):
        self.total_sales = sum(self.sale_app_ids.mapped('price'))

    @api.model
    def create(self, values):
        """Override default Odoo create function and extend."""
        print('context', self._context.get('shop_id'))
        values.update({
            'shop_id': self._context.get('shop_id')
        })
        print(values, 'values')
        return super(RegistryApp, self).create(values)

    # def my_server_action(self):
    #     action_values = self.env.ref('product.product_template_action').read()[0]
    #
    #     return action_values
