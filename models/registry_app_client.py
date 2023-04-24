from odoo import models, fields, api, _


class RegistryAppClient(models.Model):
    _name = 'registry_app.client'
    _description = 'TPE Member'

    client_number = fields.Char(string=_('Client Number'))
    # name = fields.Char(related='partner_id.name', string='Name', readonly=False,
    #                    required=True)
    partner_id = fields.Many2one('res.partner', delegate=True, string=_('Name'),
                                 ondelete='cascade', domain=[('id', '=', 0)])
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False,
                        string=_('Phone'))
    email = fields.Char(related='partner_id.email', store=True, readonly=False,
                        string=_('Email'))
    street = fields.Char(related='partner_id.street', store=True,
                         string=_('Street'), readonly=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop')
    active = fields.Boolean(string=_('Active'), default=True)

    def send_sms(self):
        # view_id = self.env.ref('registry_app.view_sms_broadcast_form').id
        # action = self.env.ref('registry_app.sms_broadcast').read()[0]
        # action['target'] = 'new'
        # action['view_mode'] = 'form'
        # return action
        view_id = self.env.ref('registry_app.view_sms_broadcast_form').id,
        return {
            'res_model': 'regsmsbroadcast',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id,
        }

    @api.model
    def create(self, values):
        """Override default Odoo create function and extend."""
        # shop_id = self.env['registry_app.shop'].search(
        #     ['|',('create_uid', '=', self.env.user.id),
        #      ('id', '=', self.env.user.shop_id),
        #      ], limit=1).id
        print('shop_id', self.env.user.shop_id)
        # values['shop_id'] = shop_id
        values.update({
            'shop_id': self.env.user.shop_id.id
        })
        print(values, 'values')
        return super(RegistryAppClient, self).create(values)
