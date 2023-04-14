# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import werkzeug.utils


class RegistryApp(http.Controller):
    @http.route('/registry_app/registry_app', auth='public')
    def index(self, **kw):
        # return "Hello, world"
        return request.render("registry_app.tmp_sales_data")

    @http.route('/my/cus/login', type='http', auth='user', website=True)
    def list(self, **kw):
        print(kw.get('username'))
        if kw.get('username') == '1' and kw.get('password') == '1':
            view_id = request.env.ref(
                'registry_app.registry_app_shop_action_window')
            return request.redirect(
                '/web?&#min=1&limit=80&view_type=list&model=registry_app.shop&action=%s' % (
                    view_id.id))

    @http.route('/cooperatives', type='http', auth='user', website=True)
    def get_cooperatives(self):
        cooperatives = request.env['registry_app.cooperatives'].sudo().search(
            [('user_id', '=', request.uid)])
        values = {"cooperatives": cooperatives}
        return request.render("registry_app.registry_app_website_cooperatives",
                              values)

    @http.route('/cooperative/<int:cooperative_id>/shops',
                type='http', auth='public', website=True)
    def show_shop(self, cooperative_id, **kwargs):
        """Fetching the Cooperative_id from the button click and filtering
        shops."""
        shops = request.env['registry_app.shop'].sudo().search(
            [('cooperative_id', '=', cooperative_id)])
        values = {
            'shops': shops,
        }
        return request.render("registry_app.registry_app_website_shops", values)

    @http.route('/shops/<int:shop_id>/registries', type='http', auth='public',
                website=True)
    def open_registry_website(self, shop_id, **kwargs):
        print("Opening", shop_id)


class RegistryAppShopController(http.Controller):

    @http.route('/registry_app_shop/form/<int:shop_id>', auth='public', website=True)
    def shop_form(self, shop_id ,**kw):
        users = request.env['res.users'].search([])
        cooperatives = request.env['registry_app.cooperatives'].search([])
        shop = request.env['registry_app.shop'].search([('id','=', shop_id)])

        date = request.env['registry_app.registry_app'].get_context_today()
        print(date)
        name = 'Registry Log - ' + str(date)
        print(name)
        return request.render('registry_app.registry_app_shop_form_template',
                              {'users': users,
                               'cooperatives': cooperatives,
                               'date': date,
                               'name': name,
                               'shop':shop
                               # 'shop_id':shop_id
                               })

    @http.route('/registry_app/shop/create', auth='public', website=True,
                csrf=False)
    def create_shop(self, **post):
        registry_app_shop = request.env['registry_app.registry_app']
        vals = {

            'user_id': post.get('user_id'),
            'shop_users_ids': [(6, 0, post.getlist('shop_users_ids'))],
            'cooperative_id': post.get('cooperative_id'),
            'active': True,
        }
        registry_app_shop.create(vals)
        return request.render('registry_app.shop_thankyou')
