# -*- coding: utf-8 -*-
import base64
import datetime
import json

from odoo import http, fields, _
from odoo.exceptions import ValidationError
from odoo.http import request
import werkzeug.utils
from werkzeug.utils import redirect
import odoo
import odoo.addons.web.controllers.main as main
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager

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

            try:
                uid = request.session.authenticate(request.session.db,
                                                   request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                user = request.env.user
                coop = request.env[
                    'registry_app.cooperatives'].sudo().browse(
                    user.cooperative_id.id)
                print('coop', coop.id)
                if user.has_group(
                        'registry_app.registry_app_shop_owner') | user.has_group(
                    'registry_app.registry_app_user'):
                    return request.redirect(
                        self._login_redirect(uid,
                                             redirect=f'/cooperative/{coop.id}/shops'))
                if user.has_group(
                        'registry_app.registry_app_cooperative_owner'):
                    return request.redirect(
                        self._login_redirect(uid,
                                             redirect='/cooperatives'))
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

    @http.route('/cooperatives', type='http', auth='user', website=True)
    def get_cooperatives(self):
        user = request.env['res.users'].browse(request.uid)
        cooperatives = request.env['registry_app.cooperatives'].sudo().search(
            ['|', '|', ('user_id', '=', request.uid),
             ('create_uid', '=', request.uid),
             ('shop_ids', 'in', [user.shop_id.id])])
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
        user = request.env['res.users'].browse(request.uid)
        log_user = request.env['res.users'].browse(request.uid)
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True),
             ('cooperative_id', '=', log_user.cooperative_id.id)])
        return request.render('registry_app.cooperative_form_template', {
            'users': users,
            'user':user,
        })

    @http.route('/submit_cooperative', type='http', auth="public", website=True)
    def submit_cooperative(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        cooperatives = request.env['registry_app.cooperatives']
        cooperatives.create({
            'name': kw.get('name'),
            'user_id': kw.get('user_id'),
            'user':user,
        })
        return request.redirect('/cooperatives')

    @http.route('/cooperative/<int:cooperative_id>/shops',
                type='http', auth='public', website=True)
    def show_shop(self, cooperative_id, **kwargs):
        """Fetching the Cooperative_id from the button click and filtering
        shops."""
        user = request.env['res.users'].browse(request.uid)
        shops = request.env['registry_app.shop'].sudo().search(
            ['|', ('id', '=', user.shop_id.id), ('create_uid', '=', user.id)])
        view_id = request.env.ref(
            'registry_app.registry_app_shop_form_view')
        values = {
            'shops': shops,
            'cooperative_id': cooperative_id,
            'view_id': view_id,
            'user': user
        }
        return request.render("registry_app.registry_app_website_shops", values)

    @http.route('/shops/<int:shop_id>/registries', type='http', auth='public',
                website=True)
    def open_registry_website(self, shop_id, **kwargs):
        user = request.env['res.users'].browse(request.uid)
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True),
             ('cooperative_id', '=', user.cooperative_id.id)])
        cooperatives = request.env['registry_app.cooperatives'].search([])
        shop = request.env['registry_app.shop'].search([('id', '=', shop_id)])

        date = request.env['registry_app.registry_app'].get_context_today(). \
            strftime('%d-%m-%Y')
        name = f'Registry Log - {str(date)}'

        product = request.env['registry_app.product'].search(
            [('shop_id', '=', user.shop_id.id)])
        client = request.env['registry_app.client'].search(
            [('shop_id', '=', user.shop_id.id)])
        return request.render('registry_app.registry_app_shop_form_template',
                              {
                               'users': users,
                               'user': user,
                               'cooperatives': cooperatives,
                               'date': date,
                               'name': name,
                               'shop': shop,
                               'product': product,
                               'client': client
                               })


class RegistryAppShopController(http.Controller):

    @http.route('/registry_app_shop/<int:cooperative_id>/form', auth='public',
                website=True)
    def shop_form(self, cooperative_id, **kw):
        user = request.env['res.users'].browse(request.uid)
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True),
             ('cooperative_id', '=', user.cooperative_id.id)])
        return request.render(
            'registry_app.registry_app_shop_create_form_template', {
                'users': users,
                'user': user,
                'cooperative_id': cooperative_id
            })

    @http.route('/registry_app/shop/create', auth='public', website=True,
                csrf=False)
    def create_shop(self, **post):
        registry_app_shop = request.env['registry_app.shop']
        file = post.get('shop_logo')
        coop_id = int(post.get('cooperative_id'))
        selected_users_string = post.get(
            'selectedUsers[]')  # Get the values from 'selectedUsers[]'
        selected_users = [int(user_id) for user_id in
                          selected_users_string.split(',') if
                          user_id]  # Split and convert to integers
        vals = {
            'name': post.get('name'),
            'user_id': int(post.get('user_id')) if post.get(
                'user_id') else None,
            'shop_logo': base64.b64encode(file.read()),
            'cooperative_id': coop_id,
            'shop_users_ids': [(6, 0, selected_users)],
            # Assign the values to 'shop_users_ids'
        }
        registry_app_shop.create(vals)
        return request.redirect('/cooperatives')

    @http.route('/registry_app/shop/edit/<int:shop_id>', type='http',
                auth="user", website=True)
    def edit_shop(self, shop_id):
        shop = request.env['registry_app.shop'].sudo().browse(shop_id)
        ss = request.env['registry_app.shop'].search_read(
            [('id', '=', shop_id)])
        users = request.env['res.users'].browse(request.uid)
        all_user = request.env['res.users'].search(
            ['|', '|', ('create_uid', '=', users.id),
             ('user_id', '=', users.id),
             ('cooperative_id', '=', users.cooperative_id.id)])
        values = {
            'shop': shop,
            'users': users,
            'all_user': all_user,
            'cooperative_id':users.cooperative_id.id,
        }
        return request.render('registry_app.registry_app_website_shop_form',
                              values)

    @http.route('/registry_app/shop/update/<int:shop_id>', type='http',
                auth="user", website=True, method=['POST'])
    def update_shop(self, shop_id, **post):
        user = request.env['res.users'].browse(request.uid)
        shop = request.env['registry_app.shop'].sudo().browse(shop_id)
        coop_id = user.cooperative_id.id
        selected_users_string = post.get(
            'selectedUsers[]')  # Get the values from 'selectedUsers[]'
        selected_users = [int(user_id) for user_id in
                          selected_users_string.split(',') if
                          user_id]  # Split and convert to integers
        file = post.get('shop_logo')
        vals = {
            'name': post.get('name'),
            'user_id': int(post.get('user_id')) if post.get(
                'user_id') else None,
            'shop_logo': base64.b64encode(file.read()),
            'cooperative_id': coop_id,
            'shop_users_ids': [(6, 0, selected_users)],
            # Assign the values to 'shop_users_ids'
        }
        shop.write({
            'name': post.get('name'),
            'shop_logo': base64.b64encode(file.read()),
            'user_id': int(post.get('user_id')) if post.get(
                'user_id') else None,
            'shop_users_ids': [(6, 0, selected_users)],
        })
        # Redirect to the shop details page after update
        return request.redirect(f'/cooperative/{coop_id}/shops')

    @http.route('/registries/create', type='http', auth='public', website=True)
    def create_registry(self, **post):
        if post.get('sales_table_data') or post.get('expense_table_data'):
            user = request.env['res.users'].browse(request.uid)
            date = post.get('date')
            date_object = datetime.datetime.strptime(date, '%d-%m-%Y')
            formatted_date = date_object.strftime('%Y-%m-%d')
            state = post.get('state')
            sales_table_data = json.loads(post.get('sales_table_data', '[]'))
            expense_table_data = json.loads(post.get('expense_table_data', '[]'))
            if existing_registry := request.env[
                'registry_app.registry_app'
            ].search([('date', '=', formatted_date)]):
                # Update the existing registry record with associated sales and purchase records
                existing_registry.write({
                    'sale_app_ids': [(0, 0, {
                        'product_id': int(sale['product_sale']) if sale.get(
                            'product_sale') else None,
                        'price': float(sale['price_sale']) if sale.get(
                            'price_sale') else None,
                        'quantity': int(sale['quantity_sale']) if sale.get(
                            'quantity_sale') else None,
                        'client_id': int(sale['client_sale']) if sale.get(
                            'client_sale') else None
                    }) for sale in sales_table_data],
                    'purchase_app_ids': [(0, 0, {
                        'product_id': int(expense['exp_product']) if expense.get(
                            'exp_product') else None,
                        'cost': float(expense['exp_cost']) if expense.get(
                            'exp_cost') else None,
                    }) for expense in expense_table_data],
                    'state': state,
                })
            else:
                # Create the registry record with associated sales and purchase records
                registry_app = request.env['registry_app.registry_app'].create({
                    'date': formatted_date,
                    'shop_id': user.shop_id.id,
                    'sale_app_ids': [(0, 0, {
                        'product_id': int(sale['product_sale']) if sale.get(
                            'product_sale') else None,
                        'price': float(sale['price_sale']) if sale.get(
                            'price_sale') else None,
                        'quantity': int(sale['quantity_sale']) if sale.get(
                            'quantity_sale') else None,
                        'client_id': int(sale['client_sale']) if sale.get(
                            'client_sale') else None
                    }) for sale in sales_table_data],
                    'purchase_app_ids': [(0, 0, {
                        'product_id': int(expense['exp_product']) if expense.get(
                            'exp_product') else None,
                        'cost': float(expense['exp_cost']) if expense.get(
                            'exp_cost') else None,
                    }) for expense in expense_table_data],
                    'state': state,
                })
        return request.redirect('/registry_log')


    @http.route('/registry_log/<int:reg_log_id>/edit', type='http',
                auth='public', website=True)
    def render_edit_registry_form(self, reg_log_id, **post):
        registry_log = request.env['registry_app.registry_app'].browse(
            reg_log_id)
        date = registry_log.date
        formatted_date = date.strftime('%d-%m-%Y')
        user = request.env['res.users'].browse(request.uid)
        products = request.env['registry_app.product'].search([])
        clients = request.env['registry_app.client'].search([])
        return request.render(
            'registry_app.registry_app_shop_edit_form_template', {
                'reg_log': registry_log,
                'user': user,
                'products': products,
                'clients': clients,
                'date': formatted_date,
            })

    @http.route('/registries/edit', type='http', auth='public',
                website=True,method=['POST'])
    def edit_registry(self, **post):
        user = request.env['res.users'].browse(request.uid)
        if post:
            reg_id = int(post.get('reg_log_id'))
            registry = request.env['registry_app.registry_app'].browse(reg_id)
            date = post.get('date')
            date_object = datetime.datetime.strptime(date, '%d-%m-%Y')
            formatted_date = date_object.strftime('%Y-%m-%d')
            state = post.get('state')
            sales_table_data = json.loads(post.get('sales_table_data', '[]'))
            expense_table_data = json.loads(
                post.get('expense_table_data', '[]'))
            # Clear existing sales and expenses
            registry.sale_app_ids.unlink()
            registry.purchase_app_ids.unlink()
            # Update the registry record with edited data
            registry.write({
                'date': formatted_date,
                'sale_app_ids': [(0, 0, {
                    'product_id': int(sale['product_sale']) if sale.get(
                        'product_sale') else None,
                    'price': float(sale['price_sale']) if sale.get(
                        'price_sale') else None,
                    'quantity': int(sale['quantity_sale']) if sale.get(
                        'quantity_sale') else None,
                    'client_id': int(sale['client_sale']) if sale.get(
                        'client_sale') else None
                }) for sale in sales_table_data],
                'purchase_app_ids': [(0, 0, {
                    'product_id': int(expense['exp_product']) if expense.get(
                        'exp_product') else None,
                    'cost': float(expense['exp_cost']) if expense.get(
                        'exp_cost') else None,
                }) for expense in expense_table_data],
                'state': state,
            })
            return request.redirect('/registry_log')

    class RegistryLogController(http.Controller):

        @http.route('/registry_log', type='http', auth='public', website=True)
        def registry_log_page(self, **kw):
            user = request.env['res.users'].browse(request.uid)
            registry_logs = request.env[
                'registry_app.registry_app'].sudo().search([('shop_id','=',user.shop_id.id)])
            return http.request.render(
                'registry_app.registry_app_website_registry_log', {
                    'registry_log': registry_logs,
                    'user':user
                })

class RegistryAppProductController(http.Controller):
    @http.route('/reg_products', type='http', auth='user', website=True)
    def get_cooperatives(self):
        user = request.env['res.users'].browse(request.uid)
        products = request.env['registry_app.product'].sudo().search(
            [('shop_id', '=', user.shop_id.id)])
        values = {"products": products,
                  'user': user
                  }
        return request.render("registry_app.registry_app_website_products",
                              values)

    @http.route('/reg_products/form', type='http', auth="public", website=True)
    def cooperative_form(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True),
             ('cooperative_id', '=', user.cooperative_id.id)])
        values={
            'user':user
        }
        return request.render(
            'registry_app.website_reg_products_form_template',values)

    @http.route('/submit_products', type='http', auth="public", website=True)
    def submit_cooperative(self, **kw):
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        products = request.env['registry_app.product']
        products.create({
            'name':  kw.get('name'),
            'price': kw.get('price'),
            'cost': kw.get('cost'),
            'shop_id': shop_id.id
        })
        return request.redirect('/reg_products')

    @http.route('/reg_products/edit/<int:product_id>', type='http', auth='user',
                website=True)
    def product_edit(self, product_id=None, **post):
        user = request.env['res.users'].browse(request.uid)
        product = request.env['registry_app.product'].sudo().browse(product_id)
        return request.render(
            "registry_app.website_reg_products_edit_template", {
                'product': product,
                'user': user,
            })

    @http.route('/update_reg_product', type='http', auth='user', methods=['POST'],
                website=True)
    def update_product(self, **post):
        product_id = int(post.get('product_id'))
        product = request.env['registry_app.product'].sudo().browse(product_id)
        product.write({
            'name': post.get('name'),
            'price': post.get('price'),
            'cost': post.get('cost'),
        })
        return request.redirect(
            '/reg_products')  # Redirect to the products listing page

class RegistryAppClientsController(http.Controller):
    @http.route('/reg_clients', type='http', auth='user', website=True)
    def get_cooperatives(self):
        user = request.env['res.users'].browse(request.uid)
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        clients = request.env['registry_app.client'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        values = {"clients": clients,
                  'user': user
                  }
        return request.render("registry_app.registry_app_website_client",
                              values)

    @http.route('/clients/form', type='http', auth="public", website=True)
    def client_form(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        users = request.env['res.users'].search(
            [('is_from_registry_app', '=', True),
             ('cooperative_id', '=', user.cooperative_id.id)])
        values = {
            'user':user
        }
        return request.render('registry_app.website_reg_client_form_template',values )

    @http.route('/submit_clients', type='http', auth="public", website=True)
    def submit_client(self, **kw):
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        values = {
            'name': kw.get('name'),
            'client_number': kw.get('client_number'),
            'phone': kw.get('phone'),
            'email': kw.get('email'),
            'street': kw.get('street'),
            'shop_id': shop_id
        }
        request.env['registry_app.client'].create(values)
        return request.redirect('/reg_clients')

    @http.route('/clients/edit/<int:client_id>', type='http', auth="public",
                website=True)
    def edit_client(self, client_id, **kwargs):
        client = request.env['registry_app.client'].sudo().browse(client_id)
        return request.render('registry_app.website_edit_client_template',
                              {'client': client})

    @http.route('/update_client', type='http', auth="public", website=True,
                methods=['POST'])
    def update_client(self, **kwargs):
        client_id = int(kwargs.get('client_id'))
        client = request.env['registry_app.client'].sudo().browse(client_id)
        client.write({
            'name': kwargs.get('name'),
            'client_number': kwargs.get('client_number'),
            'phone': kwargs.get('phone'),
            'email': kwargs.get('email'),
            'street': kwargs.get('street'),
        })
        return request.redirect('/reg_clients')


    @http.route('/user/edit/<int:user_id>', type='http', auth="user",
                website=True)
    def user_edit(self, user_id):
        user = request.env['registry_app.users'].sudo().browse(user_id)
        values = {
            'user': user,
        }
        return request.render('registry_app.registry_app_website_users_edit',
                              values)


    @http.route('/update_user', type='http', auth="user",
                website=True, methods=['POST'])
    def update_user(self, user_id, **post):
        user = request.env['registry_app.users'].sudo().browse(int(user_id))
        user.write(post)
        return request.redirect('/reg_app/users')


class RegistryAppSmsController(http.Controller):
    @http.route('/reg_sms', type='http', auth='user', website=True)
    def get_regsms(self):
        user = request.env['res.users'].browse(request.uid)
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        sms_broadcasts = request.env['regsmsbroadcast'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        values = {"sms_broadcasts": sms_broadcasts,
                  'user': user
                  }
        return request.render("registry_app.registry_app_website_sms_broadcast",
                              values)

    @http.route('/sms_broadcast/form', type='http', auth="public", website=True)
    def regsms_form(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        clients = request.env['registry_app.client'].search([])
        values = {'clients': clients,
                  'user':user
                  }

        return request.render(
            'registry_app.website_sms_broadcast_form_template', values)

    @http.route('/submit_sms_broadcast', type='http', auth="public",
                website=True)
    def submit_regsms(self, **kw):
        shop_id = request.env.user.shop_id
        broadcast_sms = request.env['regsmsbroadcast']
        timestamp_str = kw.get("broadcast_date")
        dt_obj = None
        if timestamp_str:
            dt_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M")
        now = datetime.datetime.now()
        print(now, 'now')
        selected_clients_string = kw.get(
            'selectedClients')  # Get the values from 'selectedUsers[]'
        selected_clients = [int(client_id) for client_id in
                            selected_clients_string.split(',') if
                            client_id]
        print('selected_clients', selected_clients)
        # Create the record
        send_sms_action = broadcast_sms.create({
            'name': kw.get('name'),
            'broadcast_date': dt_obj,
            'clients_ids': [(6, 0, selected_clients)],
            # Updated field name and value format
            'message': kw.get('message'),
        })
        print('send_sms_', send_sms_action)
        # Check the value of the clicked button
        submit_button = kw.get('submit_button')
        if submit_button == 'send_sms':
            # Call your custom function
            send_sms_action.action_sms_send()
        return request.redirect('/reg_sms')


    # Update SMS
    @http.route('/sms/edit/<int:sms_broadcast_id>', type='http', auth="user",
                website=True)
    def registry_app_website_sms_broadcast_edit(self, sms_broadcast_id,
                                                **kwargs):
        sms_broadcast = request.env['regsmsbroadcast'].sudo().browse(
            sms_broadcast_id)
        user = request.env['res.users'].browse(request.uid)
        clients = request.env['registry_app.client'].sudo().search(
            [('shop_id', '=', user.shop_id.id)])
        return http.request.render(
            'registry_app.registry_app_website_sms_broadcast_edit', {
                'sms_broadcast': sms_broadcast,
                'clients': clients,
                'user':user
            })

    @http.route('/update_sms_broadcast', type='http', auth="user", website=True)
    def update_sms_broadcast(self, **post):
        user = request.env['res.users'].browse(request.uid)
        sms_broadcast_id = int(post.get('sms_broadcast_id'))
        sms_broadcast = request.env['regsmsbroadcast'].sudo().browse(sms_broadcast_id)
        clients = request.env['registry_app.client'].sudo().search(
            [('shop_id', '=', user.shop_id.id)])
        timestamp_str = post.get("broadcast_date")
        dt_obj = None
        if timestamp_str:
            dt_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M")
            print('dt_obj', dt_obj)
        now = datetime.datetime.now()
        selected_clients_string = post.get(
            'selectedClients')  # Get the values from 'selectedUsers[]'
        selected_clients = [int(client_id) for client_id in
                            selected_clients_string.split(',') if
                            client_id]
        # update the record
        sms_broadcast.write({
            'name': post.get('name'),
            'broadcast_date': dt_obj,
            'clients_ids': [(6, 0, selected_clients)],
            'message': post.get('message'),
        })

        # Check the value of the clicked button
        submit_button = post.get('submit_button')
        if submit_button == 'send_sms':
            # Call your custom function
            sms_broadcast.action_sms_send()



    @http.route('/report_data', type='http', auth="public",
                website=True)
    def report_data(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        shops = request.env['registry_app.shop'].sudo().search(
            [('cooperative_id', '=', user.cooperative_id.id), ])
        users = request.env['res.users'].search(
            ['|', '|', ('create_uid', '=', request.uid),
             ('user_id', '=', request.uid),
             ('cooperative_id', '=', user.cooperative_id.id)])
        domain = []
        if kw.get('select_shops'):
            domain.append(('shop_id', '=', int(kw.get('select_shops'))))
        if kw.get('registry_log_date'):
            domain.append(('date', '<=', kw.get('registry_log_date')))
        if kw.get('registry_log_status'):
            domain.append(('state', '=', str(kw.get('registry_log_status'))))
        ret_list = []
        registry_logs = request.env['registry_app.registry_app'].search(domain)
        for rec in registry_logs:
            sale_list = []
            purchase_list = []
            sale_list.clear()
            purchase_list.clear()
            sale_list.extend(
                (
                    item.product_id.display_name,
                    item.price,
                    item.quantity,
                    item.client_id.name,
                )
                for item in rec.sale_app_ids
            )
            purchase_list.extend(
                (exp.product_id.display_name, exp.cost)
                for exp in rec.purchase_app_ids
            )
            reg_dict = {
                'name': rec.name,
                'sale_app_ids': sale_list,
                'purchase_app_ids': purchase_list,
                'total_sales': rec.total_sales,
                'total_purchase': rec.total_purchase,
                'shop_owner': rec.registry_user_id.name,
                'shop': rec.shop_id.name,
                'state': rec.state
            }
            ret_list.append(reg_dict)
        vals = {
            'datas': ret_list,
            'user': user,
            'users': users,
            'shops': shops,
        }
        return http.request.render('registry_app.registry_report_template',
                                   vals)


    @http.route('/reg_app/reporting', type='http', auth='user', website=True)
    def reg_reporting(self):
        data = request.env['sale.custom'].get_registry_log()
        user = request.env['res.users'].browse(request.uid)
        shops = request.env['registry_app.shop'].sudo().search(
            [('cooperative_id', '=', user.cooperative_id.id),])

        users = request.env['res.users'].search(['|','|',('create_uid', '=', request.uid),('user_id', '=', request.uid),('cooperative_id', '=', user.cooperative_id.id)])
        vals = {
            'datas': data,
            'user': user,
            'users':users,
            'shops':shops,
        }
        return http.request.render('registry_app.registry_report_template',vals )


    @http.route('/reg_app/users', type='http', auth='user', website=True )
    def reg_users(self):
        user = request.env['res.users'].browse(request.uid)
        users = request.env['registry_app.users'].search(
            ['|', '|', ('create_uid', '=', user.id),
             ('user_id', '=', user.id),
             ('cooperative_id', '=', user.cooperative_id.id)])
        return request.render("registry_app.registry_app_website_users",
                              {
                               "users": users,
                               'user':user
                               })

    @http.route('/users/form', type='http', auth='user', website=True)
    def reg_users_form(self):
        user = request.env['res.users'].browse(request.uid)
        values = {
            'user':user
        }
        return request.render("registry_app.website_reg_user_form_template",values )

    @http.route('/submit_users', type='http', auth='user', )
    def reg_users_create(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        if user.shop_id.cooperative_id is None or user.cooperative_id is None:
            vals ={"error_msg": "You doesn't belong to any cooperatives. Make sure you are in a cooperative.Before creating users"}
            return request.render("registry_app.website_reg_user_form_template",vals)
        values = {
            'name': kw.get('name'),
            'login': kw.get('email'),
            'password': kw.get('password'),
            'email': kw.get('email'),
        }
        request.env['registry_app.users'].sudo().create(values)
        return request.redirect("/reg_app/users")

