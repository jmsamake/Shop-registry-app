from odoo import models, fields, api, _
import datetime
import requests
import json


class SmsBroadcast(models.Model):
    _name = 'regsmsbroadcast'
    _rec_name = 'name'
    _description = 'SMS Notification'
    _inherit = ['mail.thread']

    name = fields.Char(string=_("SMS Notification"), required=True)
    broadcast_date = fields.Datetime(string="Broadcast Date")

    clients_ids = fields.Many2many('registry_app.client', string=_('Clients'),
                                   required=True)
    message = fields.Text(string=_("Message"), required=True)
    active = fields.Boolean(string=_("Active"), default=True)
    msg_sent = fields.Boolean(string=_("SMS send?"), default=False, copy=False,
                              readonly=True)

    sender_type = fields.Char(string=_("Type structure"))
    sender_id = fields.Integer(string=_("Sender ID"))
    state = fields.Selection([
        ('draft', _('Draft')),
        ('send', _('Send')),
        ('failed', _('Failed'))
    ], string=_('SMS Status'), default='draft', readonly=True, copy=False)
    shop_id = fields.Many2one('registry_app.shop', string='Registry App Shop')

    @api.model
    def create(self, values):
        values.update({
            'shop_id': self.env.user.shop_id.id
        })
        print(values, 'values')
        return super(SmsBroadcast, self).create(values)

    def action_sms_send(self):
        access_token = self.get_access_token()
        authorization = 'Bearer {access_token}'.format(
            access_token=access_token)
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json',
        }

        sender = '2230000'
        if '+' in sender:
            sender = sender.replace('+', '')
        url = 'https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B{dev_phone_number}/requests'.format(
            dev_phone_number=sender)
        message = self.message
        for client in self.clients_ids:
            vals = {}
            # recipient = client.mobile
            # recipient = '+22375108040'
            recipient = client.phone
            if '+' in recipient:
                recipient = recipient.replace('+', '')
            data = {
                "outboundSMSMessageRequest": {
                    "address": "tel:+%s" % recipient.replace(" ", ""),
                    "senderAddress": "tel:+%s" % sender,
                    "senderName": "DS Store",
                    "outboundSMSTextMessage": {
                        "message": message
                    }
                }
            }
            response = requests.post(url, headers=headers,
                                     data=json.dumps(data))

            vals.update({
                'body': message,
                'number': recipient.replace(" ", ""),
                'partner_id': client.id,
                'error_code': response,
                'response': response.text,
            })
            if response.status_code == 201:
                self.state = 'send'
            else:
                self.state = 'failed'

    def get_access_token(self):
        authentication_url = 'https://api.orange.com/oauth/v3/token'
        authorization_header = 'Basic U05STFo3YUJ4NkcyQTFDeFlsZjVMMjBMbFE4Qzg4MXE6MkhyRGFtcnF6TTdsQjZSTQ=='
        headers = {
            'Authorization': authorization_header,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        data = {
            'grant_type': 'client_credentials'
        }

        response = requests.post(authentication_url, headers=headers, data=data)
        access_token = response.json().get('access_token', False)
        return access_token

    def send_broadcast_sms(self):
        now = datetime.datetime.now()
        # check if broadcast_date is equal to current time
        broadcast_records = self.search(
            [('broadcast_date', '<=', now), ('state', '=', 'draft')])
        print('broadcast_records', broadcast_records)
        for record in broadcast_records:
            # send SMS to clients_ids
            record.action_sms_send()
            # set msg_sent field to True
            record.msg_sent = True
        all_broadcast_records = self.search([])
        for record in all_broadcast_records:
            if record.state == 'send':
                record.msg_sent = True
