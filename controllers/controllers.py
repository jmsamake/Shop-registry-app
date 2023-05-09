# -*- coding: utf-8 -*-
import base64
import datetime

from odoo import http, fields, _
from odoo.http import request
import werkzeug.utils
from werkzeug.utils import redirect
import odoo
import odoo.addons.web.controllers.main as main

# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error',
                          'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name',
                          'partner_id',
                          'password', 'confirm_password', 'city', 'country_id',
                          'lang'}


class Home(main.Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        print('request', request.params)

        main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = {k: v for k, v in request.params.items() if
                  k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        print('vales', values)

        if request.httprequest.method == 'POST':
            old_uid = request.uid

            print('redirect', redirect)
            try:
                uid = request.session.authenticate(request.session.db,
                                                   request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                user = request.env.user
                user = request.env.user
                if user.has_group(
                        'registry_app.registry_app_shop_owner') | user.has_group(
                        'registry_app.registry_app_user') | user.has_group(
                        'registry_app.registry_app_cooperative_owner'):

                    # values['redirect'] = '/registry_app'
                    return request.redirect(
                        self._login_redirect(uid, redirect='/registry_app'))
                else:
                    return request.redirect(
                        self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                values['error'] = (
                    _("Wrong login/password")
                    if e.args == odoo.exceptions.AccessDenied().args
                    else e.args[0]
                )
        elif 'error' in request.params and request.params.get(
                'error') == 'access':
            values['error'] = _(
                'Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response


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
        user = request.env['res.users'].browse(request.uid)
        cooperatives = request.env['registry_app.cooperatives'].sudo().search(
            ['|', '|', ('user_id', '=', request.uid),
             ('create_uid', '=', request.uid),
             ('shop_ids', 'in', [user.shop_id.id])])
        print('cooperatives', cooperatives)
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
        view_id = request.env.ref(
            'registry_app.registry_app_shop_form_view')
        values = {
            'shops': shops,
            'cooperative_id': cooperative_id,
            'view_id': view_id
        }
        return request.render("registry_app.registry_app_website_shops", values)

    @http.route('/shops/<int:shop_id>/registries', type='http', auth='public',
                website=True)
    def open_registry_website(self, shop_id, **kwargs):
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True)])
        cooperatives = request.env['registry_app.cooperatives'].search([])
        shop = request.env['registry_app.shop'].search([('id', '=', shop_id)])

        date = request.env['registry_app.registry_app'].get_context_today(). \
            strftime('%d-%m-%Y')
        name = f'Registry Log - {str(date)}'
        user = request.env['res.users'].browse(request.uid)
        product = request.env['registry_app.product'].search(
            [('shop_id', '=', user.shop_id.id)])
        client = request.env['registry_app.client'].search(
            [('shop_id', '=', user.shop_id.id)])
        return request.render('registry_app.registry_app_shop_form_template',
                              {'users': users,
                               'cooperatives': cooperatives,
                               'date': date,
                               'name': name,
                               'shop': shop,
                               # 'shop_id':shop_id
                               'product': product,
                               'client': client
                               })


class RegistryAppShopController(http.Controller):

    @http.route('/registry_app_shop/<int:cooperative_id>/form', auth='public',
                website=True)
    def shop_form(self, cooperative_id, **kw):
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True)])
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
        print('sdsd', type(post.get('shop_logo')))
        file = post.get('shop_logo')
        coop_id = int(post.get('cooperative_id'))
        selct = post.get('users[]')
        vals = {
            'name': post.get('name'),
            'user_id': int(post.get('user_id')),
            'shop_logo': base64.b64encode(file.read()),
            # 'shop_users_ids': [(6, 0, post.getlist('shop_users_ids'))],
            'cooperative_id': coop_id,
            # 'active': True,
        }
        registry_app_shop.create(vals)
        return request.redirect(f'/registry_app_shop/{coop_id}/form')

    @http.route('/registries/create', auth='public', website=True,
                csrf=False)
    def create_registry(self, **post):
        print('Creating registry', post)
        # registry_app_shop = request.env['registry_app.shop']
        # print('Creating', post)
        # print('sdsd', type(post.get('shop_logo')))
        # file = post.get('shop_logo')
        # coop_id = int(post.get('cooperative_id'))
        # selct = post.get('users[]')
        # print('Selct', selct)
        # pass
        # vals = {
        #     'name': post.get('name'),
        #     'user_id': int(post.get('user_id')),
        #     'shop_logo': base64.b64encode(file.read()),
        #     # 'shop_users_ids': [(6, 0, post.getlist('shop_users_ids'))],
        #     'cooperative_id': coop_id,
        #     # 'active': True,
        # }
        # registry_app_shop.create(vals)
        # return request.redirect(f'/registry_app_shop/{coop_id}/form')


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
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True)])
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
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True)])
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
        timestamp_str = f'{kw.get("broadcast_date")}'
        dt_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M")
        print('dt_obj', dt_obj)
        now = datetime.datetime.now()
        print(now, 'now')
        broadcast_sms.create({
            'name': kw.get('name'),
            'broadcast_date': dt_obj,
            'clients_ids': kw.get('clients'),
            'message': kw.get('message'),
        })
        return request.redirect('/reg_sms')

    @http.route('/registry_app', type='http', auth='user', website=True)
    def open_registry_app(self):
        # cooperatives = request.env['registry_app.cooperatives'].sudo().search(
        #     [('user_id', '=', request.uid)])
        return request.render(
            "registry_app.registry_app_login_form")

    @http.route('/test_action', type='http', auth='user', website=True)
    def test_act(self):
        view_id = request.env.ref(
            'registry_app.registry_app_shop_form_view')
        print(view_id)
        return request.redirect(
            f'/web?&#min=1&limit=80&view_type=form&active_id=1&model=registry_app.shop'
        )

    @http.route('/reg_app/reporting', type='http', auth='user', website=True)
    def reg_reporting(self):
        print('sdsd')
        action_name = 'Sale Custom'
        action = request.env['ir.actions.client'].sudo().search(
            [('name', '=', action_name)], limit=1)
        print(action)
        if action:
            action_id = action.id
            menu_id = request.env['ir.ui.menu'].sudo().search(
                [('name', '=', 'Reg Reporting')],
                limit=1).id
            if menu_id:
                return request.redirect(
                    '/web#action=%s&menu_id=%s' % (action_id, menu_id))

    @http.route('/reg_app/registries', type='http', auth='user', website=True)
    def reg_registries(self):
        view_id = request.env.ref(
            'registry_app.registry_app_past_login_action_window')
        print(view_id, 'df')
        if view_id:
            return request.redirect(
                '/web?&#min=1&limit=80&view_type=list&model=registry_app.shop&action=%s' % (
                    view_id.id))

    @http.route('/reg_app/users', type='http', auth='user', )
    def reg_users(self):
        view_id = request.env.ref(
            'registry_app.registry_app_users_web_action_window')
        if view_id:
            return request.redirect(
                '/web?&#min=1&limit=80&view_type=list&model=registry_app.shop&action=%s' % (
                    view_id.id))
