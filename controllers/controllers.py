# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug.utils


class RegistryApp(http.Controller):
    @http.route('/registry_app/registry_app', auth='public')
    def index(self, **kw):
        # return "Hello, world"
        return request.render("registry_app.tmp_sales_data")

    @http.route('/my/cus/login',type='http', auth='user', website=True)
    def list(self, **kw):
        print(kw.get('username'))
        if kw.get('username') == '1' and kw.get('password') == '1':

            view_id = request.env.ref('registry_app.registry_app_shop_action_window')
            return request.redirect(
                '/web?&#min=1&limit=80&view_type=list&model=registry_app.shop&action=%s' % (
                    view_id.id))
        # return http.request.render('registry_app.listing', {
        #     'root': '/registry_app/registry_app',
        #     'objects': http.request.env['registry_app.registry_app'].search([]),
        # })

#     @http.route('/registry_app/registry_app/objects/<model("registry_app.registry_app"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('registry_app.object', {
#             'object': obj
#         })
