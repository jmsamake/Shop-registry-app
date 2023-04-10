from odoo import models, fields,api,_


class RegistryAppClient(models.Model):
    _name = 'registry_app.client'
    _description = 'TPE Member'

    client_number = fields.Char(string=_('Client Number'), )
    # name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', delegate=True,
                                 ondelete='cascade', required=True)
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False,string=_('Phone'))
    email = fields.Char(related='partner_id.email', store=True, readonly=False,string=_('Email'))
    street = fields.Char(related='partner_id.street', store=True,string=_('Street'),
                         readonly=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 readonly=True, help="Logged in user Company")
    active = fields.Boolean(string=_('Active'), default=True)


# class SaleCustom(models.Model):
#     _name = 'sale.custom'
#
#     @api.model
#     def get_sale_order(self):
#         ret_list = []
#         req = (
#             "SELECT sale_order.name, rp.name AS customer, sale_order.amount_total, sale_order.state "
#             "FROM sale_order "
#             "Join res_partner rp ON (sale_order.partner_id=rp.id)")
#         self.env.cr.execute(req)
#         for rec in self.env.cr.dictfetchall():
#             ret_list.append(rec)
#         return ret_list

