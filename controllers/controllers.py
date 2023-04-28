# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import werkzeug.utils


class RegistryApp(http.Controller):
    #     @http.route('/registry_app/registry_app', auth='public')
    #     def index(self, **kw):
    #         # return "Hello, world"
    #         return request.render("registry_app.tmp_sales_data")

    @http.route('/my/cus/login', type='http', auth='user', website=True)
    def list(self, **kw):
        print('KW : ', kw)
        # print(kw.get('username'))
        # if kw.get('username') == '1' and kw.get('password') == '1':
        #     view_id = request.env.ref(
        #         'registry_app.registry_app_shop_action_window')
        #     return request.redirect(
        #         '/web?&#min=1&limit=80&view_type=list&model=registry_app.shop&action=%s' % (
        #             view_id.id))

    @http.route('/registry_app', type='http', auth='user', website=True)
    def list(self, **kw):
        print('KW : ', kw)
        user = request.env['res.users'].browse(request.uid)
        values = {
            "user": user,
        }
        return request.render("registry_app.registry_app_login_form",
                              values)

    @http.route('/reg_app/login', type='http', auth='user', website=True)
    def list(self, **kw):
        form_password = kw.get('reg_password')
        print(request.uid)
        registry_password = request.env['res.users'].browse(
            request.uid).login_pswd

        print('form_password', form_password)
        print('registry_password', registry_password)
        # return request.redirect('/cooperatives')
        # if registry_password is None:
        #     print('bibe')
        #     return request.redirect('/cooperatives')
        if registry_password == form_password:
            return request.redirect('/cooperatives')

    @http.route('/cooperatives', type='http', auth='user', website=True)
    def get_cooperatives(self):
        cooperatives = request.env['registry_app.cooperatives'].sudo().search(
            [('user_id', '=', request.uid)])
        user = request.env['res.users'].browse(request.uid)
        shop_logo = user.shop_id.shop_logo
        values = {
            "cooperatives": cooperatives,
            "user": user,
            "shop_logo": shop_logo
        }
        return request.render("registry_app.registry_app_website_cooperatives",
                              values)

    @http.route('/cooperatives/form', type='http', auth="public", website=True)
    def cooperative_form(self, **kw):
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True)])
        return request.render('registry_app.cooperative_form_template', {
            'users': users
        })

    @http.route('/submit_cooperative', type='http', auth="public", website=True)
    def submit_cooperative(self, **kw):
        print(request.env, "Please enter")
        cooperatives = request.env['registry_app.cooperatives']
        cooperatives.create({
            'name': kw.get('name'),
            'user_id': kw.get('user_id')
        })
        return request.redirect('/cooperatives')

    @http.route('/cooperative/<int:cooperative_id>/shops',
                type='http', auth='public', website=True)
    def show_shop(self, cooperative_id, **kwargs):
        """Fetching the Cooperative_id from the button click and filtering
        shops."""
        shops = request.env['registry_app.shop'].sudo().search(
            [('cooperative_id', '=', cooperative_id)])
        values = {
            'shops': shops,
            'cooperative_id': cooperative_id,
        }
        return request.render("registry_app.registry_app_website_shops", values)

    @http.route('/shops/<int:shop_id>/registries', type='http', auth='public',
                website=True)
    def open_registry_website(self, shop_id, **kwargs):
        print("Opening", shop_id)
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True)])
        cooperatives = request.env['registry_app.cooperatives'].search([])
        shop = request.env['registry_app.shop'].search([('id', '=', shop_id)])

        date = request.env['registry_app.registry_app'].get_context_today()
        print(date)
        name = 'Registry Log - ' + str(date)
        print(name)
        return request.render('registry_app.registry_app_shop_form_template',
                              {'users': users,
                               'cooperatives': cooperatives,
                               'date': date,
                               'name': name,
                               'shop': shop
                               # 'shop_id':shop_id
                               })


class RegistryAppShopController(http.Controller):

    @http.route('/registry_app_shop/<int:cooperative_id>/form', auth='public',
                website=True)
    def shop_form(self, cooperative_id, **kw):
        users = request.env['res.users'].search([('is_from_registry_app','=',True)])
        return request.render(
            'registry_app.registry_app_shop_create_form_template', {
                'users': users,
                'cooperative_id': cooperative_id
            })

    @http.route('/registry_app/shop/create', auth='public', website=True,
                csrf=False)
    def create_shop(self, **post):
        registry_app_shop = request.env['registry_app.shop']
        print('Creating', post)
        coop_id = int(post.get('cooperative_id'))
        vals = {
            'name': post.get('name'),
            'user_id': int(post.get('user_id')),
            # 'shop_users_ids': [(6, 0, post.getlist('shop_users_ids'))],
            'cooperative_id': coop_id,
            'active': True,
        }
        registry_app_shop.create(vals)
        return request.redirect(f'/registry_app_shop/{coop_id}/form')


class RegistryAppProductController(http.Controller):
    @http.route('/reg_products', type='http', auth='user', website=True)
    def get_cooperatives(self):
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        products = request.env['registry_app.product'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        values = {"products": products}
        return request.render("registry_app.registry_app_website_products",
                              values)

    @http.route('/reg_products/form', type='http', auth="public", website=True)
    def cooperative_form(self, **kw):
        users = request.env['res.users'].search([('is_from_registry_app','=',True)])
        return request.render(
            'registry_app.website_reg_products_form_template', )

    @http.route('/submit_products', type='http', auth="public", website=True)
    def submit_cooperative(self, **kw):
        print(kw, "KW")
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        product_template = request.env['product.template']
        new_product_template = product_template.create({
            'name': kw.get('name'),
            'list_price': kw.get('price'),
            'standard_price': kw.get('cost'),
        })
        print(new_product_template, 'npt')
        products = request.env['registry_app.product']
        products.create({
            'product_id': new_product_template.id,
            'price': kw.get('price'),
            'cost': kw.get('cost'),
        })
        return request.redirect('/reg_products')


class RegistryAppClientsController(http.Controller):
    @http.route('/reg_clients', type='http', auth='user', website=True)
    def get_cooperatives(self):
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        clients = request.env['registry_app.client'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        values = {"clients": clients}
        return request.render("registry_app.registry_app_website_client",
                              values)

    @http.route('/clients/form', type='http', auth="public", website=True)
    def client_form(self, **kw):
        users = request.env['res.users'].search([('is_from_registry_app','=',True)])
        return request.render('registry_app.website_reg_client_form_template', )

    @http.route('/submit_clients', type='http', auth="public", website=True)
    def submit_client(self, **kw):
        print(kw, "KW")
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        partner_id = request.env['res.partner']
        new_partner_id = partner_id.create({
            'name': kw.get('name'),
            'phone': kw.get('phone'),
            'email': kw.get('email'),
            'street': kw.get('street'),
        })
        print(new_partner_id, 'npt')
        clients = request.env['registry_app.client']
        clients.create({
            'partner_id': new_partner_id.id,
            'client_number': kw.get('client_number'),
            'phone': kw.get('phone'),
            'email': kw.get('email'),
            'street': kw.get('street'),
        })
        return request.redirect('/reg_clients')


class RegistryAppSmsController(http.Controller):
    @http.route('/reg_sms', type='http', auth='user', website=True)
    def get_regsms(self):
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        sms_broadcasts = request.env['regsmsbroadcast'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        values = {"sms_broadcasts": sms_broadcasts}
        return request.render("registry_app.registry_app_website_sms_broadcast",
                              values)

    @http.route('/sms_broadcast/form', type='http', auth="public", website=True)
    def regsms_form(self, **kw):
        clients = request.env['registry_app.client'].search([])
        values = {'clients': clients}
        return request.render(
            'registry_app.website_sms_broadcast_form_template', values)

    @http.route('/submit_sms_broadcast', type='http', auth="public",
                website=True)
    def submit_regsms(self, **kw):
        print(kw, "KW")
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        broadcast_sms = request.env['regsmsbroadcast']

        # broadcast_sms.create({
        #     'name': kw.get('name'),
        #     'broadcast_date': kw.get('broadcast_date'),
        #     'clients_ids': kw.get('clients'),
        #     'message': kw.get('message'),
        # })
        return request.redirect('/reg_sms')

    @http.route('/registry_app', type='http', auth='user', website=True)
    def open_registry_app(self):
        # cooperatives = request.env['registry_app.cooperatives'].sudo().search(
        #     [('user_id', '=', request.uid)])
        return request.render(
            "registry_app.registry_app_login_form")
