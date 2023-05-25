from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    authorization_header = fields.Char("Authorization Header")
    api_sender = fields.Char("API Sender")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'registry_app.authorization_header', self.authorization_header)
        self.env['ir.config_parameter'].set_param(
            'registry_app.api_sender', self.api_sender)
        # self.env['ir.config_parameter'].set_param(
        #     'registry_app.toggle_cron_job', (self.toggle_cron_job)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            authorization_header=params.get_param(
                'registry_app.authorization_header'),
            api_sender=params.get_param('registry_app.api_sender'),
            # toggle_cron_job=bool(
            #     params.get_param('registry_app.toggle_cron_job',
            #                      default='False'))
        )
        return res

