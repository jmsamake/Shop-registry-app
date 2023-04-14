from odoo import models, fields, api, _


class RegistryAppClient(models.Model):
    _name = 'registry_app.client'
    _description = 'TPE Member'

    client_number = fields.Char(string=_('Client Number'))
    # name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', delegate=True, string=_('Name'),
                                 ondelete='cascade', required=True,
                                 domain=[('id', '=', 0)])
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False,
                        string=_('Phone'))
    email = fields.Char(related='partner_id.email', store=True, readonly=False,
                        string=_('Email'))
    street = fields.Char(related='partner_id.street', store=True,
                         string=_('Street'), readonly=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
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
