from odoo import models, fields, api, _


class RegistryAppClient(models.Model):
    _name = 'registry_app.client'
    _description = 'TPE Member'
    _inherit = ['mail.thread']

    client_number = fields.Char(string=_('Client Number'))
    name = fields.Char(string=_('Name'), required=True, copy=False)
    partner_id = fields.Many2one('res.partner', delegate=True,
                                 string=_('Partner'),copy=False,
                                 ondelete='cascade', domain=[('id', '=', 0)])
    phone = fields.Char(string=_('Phone'),copy=False)
    email = fields.Char(string=_('Email'),copy=False)
    street = fields.Char(string=_('Street'), copy=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company",copy=False)
    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop',copy=False)
    active = fields.Boolean(string=_('Active'), default=True)

    def send_sms(self):
        view_id = self.env.ref('registry_app.view_sms_broadcast_form').id,
        return {
            'res_model': 'regsmsbroadcast',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id,
        }

    def open_broadcastsms(self):
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx.pop('default_journal_id', None)
        ctx['active_ids'] = self.ids
        print(ctx, 'selffffff', self.ids)
        sms_wizard = self.env['regsmsbroadcast'].create({
            'name': 'Sms Broadcast',
            'clients_ids': [(6, 0, self.ids)],
            'message': 'Enter your SMS message here',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'regsmsbroadcast',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'res_id': sms_wizard.id,
        }

    @api.model
    def create(self, values):
        """Override default Odoo create function and extend."""
        res_partner = self.env['res.partner']

        new_partner = res_partner.create({
            'name': values['name'],
            'phone': values['phone'],
            'email': values['email'],
            'street': values['street'],
        })
        print(new_partner, 'new_partner')
        print('shop_id', self.env.user.shop_id)
        # values['shop_id'] = shop_id
        values.update({
            'shop_id': self.env.user.shop_id.id,
            'partner_id': new_partner.id
        })
        print(values, 'values')
        return super(RegistryAppClient, self).create(values)
