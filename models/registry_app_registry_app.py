# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

from odoo.exceptions import ValidationError


class RegistryApp(models.Model):
    _name = 'registry_app.registry_app'
    _description = 'Registry App'
    _inherit = ['mail.thread']

    name = fields.Char(string=_('Name'), required=True, tracking=True,
                       readonly=True, copy=False,
                       default=lambda self: 'Registry Log - ' +
                                            fields.Date.context_today(
                                                self).strftime('%d-%m-%Y'))
    date = fields.Date(string=_('Date'), default=fields.Date.context_today,
                       readonly=True, copy=False, required=True)
    shop_id = fields.Many2one('registry_app.shop',copy=False)
    sale_app_ids = fields.One2many('registry_app.sales', 'registry_app_id',copy=False)
    purchase_app_ids = fields.One2many('registry_app.purchase',
                                       'registry_app_id',copy=False)
    total_sales = fields.Float(string=_('Total Sales'),copy=False,
                               compute='_compute_registry_sale_total',
                               store=True)
    total_purchase = fields.Float(string=_('Total Purchase'),copy=False,
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
        default='opened',copy=False)
    registry_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                       string=_('Salesperson'),
                                       default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',copy=False,
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged user Company")
    active = fields.Boolean(string=_('Active'), default=True)

    def close_input(self):
        print('entereed')
        self.state = 'closed'

    def validate(self):
        self.state = 'validated'

    def send_sms(self):
        # my_sms = self.env['sms.composer'].create({'numbers':
        # '+916282717330', 'body': 'New lead has been created in Odoo'})
        # print('my_sms', my_sms) my_sms.action_send_sms()
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
        print('usr shop',self.env.user.shop_id)
        values.update({
            'shop_id': self.env.user.shop_id.id
        })
        print(values, 'values')
        return super(RegistryApp, self).create(values)

    @api.constrains('date')
    def _check_unique_per_day(self):
        """Restrict One record per day"""
        for record in self:
            domain = [
                ('date', '=', record.date),
                ('id', '!=', record.id),
                ('shop_id', '=', record.shop_id.id),
            ]
            count = self.search_count(domain)
            if count > 0:
                raise ValidationError('Only one record allowed per day.')

    def get_context_today(self):
        print('get_context_date')
        print(fields.Date.context_today(self))
        return fields.Date.context_today(self)

    @api.model
    def _set_status_to_closed(self):
        registry_apps = self.env['registry_app.registry_app'].search([
            ('state', 'not in', ['closed', 'cancelled'])
        ])
        end_of_day = fields.Datetime.now().replace(hour=23, minute=59,
                                                   second=59)
        print('set_status_to_closed' , end_of_day)

        for log in registry_apps:
            # if log.date <= end_of_day:
            log.state = 'closed'

    def _cron_set_status_to_closed(self):
        self._set_status_to_closed()