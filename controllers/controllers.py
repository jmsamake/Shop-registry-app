# -*- coding: utf-8 -*-
import base64
import datetime

from odoo import http, fields, _
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
                print('user', user)
                print('user_id', user.id)
                # cooperatives = request.env['registry_app.cooperatives'].search(
                #     [])
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
                # if user.has_group(
                #         'registry_app.registry_app_shop_owner') | user.has_group(
                #     'registry_app.registry_app_user') | user.has_group(
                #     'registry_app.registry_app_cooperative_owner'):
                # values['redirect'] = '/registry_app'
                # return request.redirect(
                #     self._login_redirect(uid, redirect='/registry_app'))
                # redirect to cooperatives on odoo login
                # return request.redirect(
                #     self._login_redirect(uid, redirect='/cooperatives'))
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
        # form_password = kw.get('reg_password')
        # print(request.uid)
        # registry_password = request.env['res.users'].browse(
        #     request.uid).login_pswd
        # print('form_password', form_password)
        # print('registry_password', registry_password)
        # if registry_password == form_password:
        #     return request.redirect('/cooperatives')
        # else:
        #     user = request.env['res.users'].browse(request.uid)
        #     values = {
        #         "user": user,
        #         "error_msg": "Invalid login or password."
        #     }
        #     return request.render('registry_app.registry_app_login_form',
        #                           values)
        user = request.env.user
        print('user', user)
        print('user_id', user.id)
        # cooperatives = request.env['registry_app.cooperatives'].search(
        #     [])
        coop = request.env[
            'registry_app.cooperatives'].sudo().browse(
            user.cooperative_id.id)
        print('coop', coop.id)
        if user.has_group(
                'registry_app.registry_app_shop_owner') | user.has_group(
            'registry_app.registry_app_user'):
            return request.redirect(f'/cooperative/{coop.id}/shops')
        if user.has_group(
                'registry_app.registry_app_cooperative_owner') | user.has_group(
            'registry_app.registry_app_super_admin'):
            return request.redirect('/cooperatives')
        # return request.redirect('/cooperatives')

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
        print(request.env, "Please enter")
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
        print(cooperative_id, "Please")
        user = request.env['res.users'].browse(request.uid)
        # shops = request.env['registry_app.shop'].sudo().search(
        #     [('cooperative_id', '=', cooperative_id),])
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
                               # 'shop_id':shop_id
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
        print('post', post)
        registry_app_shop = request.env['registry_app.shop']
        file = post.get('shop_logo')
        coop_id = int(post.get('cooperative_id'))
        selected_users_string = post.get(
            'selectedUsers[]')  # Get the values from 'selectedUsers[]'
        selected_users = [int(user_id) for user_id in
                          selected_users_string.split(',') if
                          user_id]  # Split and convert to integers
        print('selectedUsers', selected_users)
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
        return request.redirect('cooperatives')


    @http.route('/registries/create', auth='public', website=True,
                csrf=False)
    def create_registry(self, **post):
        print('Creating registry', post)


class RegistryAppProductController(http.Controller):
    @http.route('/reg_products', type='http', auth='user', website=True)
    def get_cooperatives(self):
        user = request.env['res.users'].browse(request.uid)
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        products = request.env['registry_app.product'].sudo().search(
            [('shop_id', '=', shop_id.id)])
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
            'shop_id': shop_id.id
        })
        return request.redirect('/reg_products')


class RegistryAppClientsController(http.Controller):
    @http.route('/reg_clients', type='http', auth='user', website=True)
    def get_cooperatives(self):
        user = request.env['res.users'].browse(request.uid)
        shop_id = request.env['res.users'].browse(request.uid).shop_id
        clients = request.env['registry_app.client'].sudo().search(
            [('shop_id', '=', shop_id.id)])
        print('found',clients)
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
        print(kw, "KW")
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
        print(kw, "KW")
        shop_id = request.env.user.shop_id
        broadcast_sms = request.env['regsmsbroadcast']
        timestamp_str = kw.get("broadcast_date")
        dt_obj = None
        if timestamp_str:
            dt_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M")
            print('dt_obj', dt_obj)
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
        print(submit_button, 'submit')

        if submit_button == 'send_sms':
            # Call your custom function
            send_sms_action.action_sms_send()

        return request.redirect('/reg_sms')

    @http.route('/registry_app', type='http', auth='user', website=True)
    def open_registry_app(self):
        user = request.env['res.users'].browse(request.uid)
        # cooperatives = request.env['registry_app.cooperatives'].sudo().search(
        #     [('user_id', '=', request.uid)])
        values = {
            'user':user
        }
        return request.render(
            "registry_app.registry_app_login_form",values)

    @http.route('/test_action', type='http', auth='user', website=True)
    def test_act(self):
        view_id = request.env.ref(
            'registry_app.registry_app_shop_form_view')
        print(view_id)
        return request.redirect(
            f'/web?&#min=1&limit=80&view_type=form&active_id=1&model=registry_app.shop'
        )

    @http.route('/reg_app/user', type='http', auth='user', website=True)
    def reg_web_users   (self):
        view_id = request.env.ref(
            'registry_app.registry_app_users_web_action_window')
        print(view_id, 'df')
        if view_id:
            return request.redirect(
                '/web?&#min=1&limit=80&view_type=list&model=registry_app.users&action=%s' % (
                    view_id.id))

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

        print(kw)
        domain = []
        if kw.get('select_shops'):
            domain.append(('shop_id', '=', int(kw.get('select_shops'))))
        if kw.get('registry_log_date'):
            domain.append(('date', '<=', kw.get('registry_log_date')))
        # if kw.get('select_users'):
        #     domain.append(kw.get('select_users'))
        if kw.get('registry_log_status'):
            domain.append(('state', '=', str(kw.get('registry_log_status'))))
        print(domain, 'jjhg')

        ret_list = []
        registry_logs = request.env['registry_app.registry_app'].search(domain)
        print('registry_logs', registry_logs)
        for rec in registry_logs:
            print(rec)
            sale_list = []
            purchase_list = []
            sale_list.clear()
            purchase_list.clear()
            for item in rec.sale_app_ids:
                sale_list.append((item.product_id.display_name, item.price,
                                  item.quantity, item.client_id.name))
            for exp in rec.purchase_app_ids:
                purchase_list.append((exp.product_id.display_name, exp.cost))
            print(sale_list, "sale_list")
            print(purchase_list, "purchase_list")
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

        print(ret_list, "ret_list")
        vals = {
            'datas': ret_list,
            'user': user,
            'users': users,
            'shops': shops,
        }
        # return ret_list
        return http.request.render('registry_app.registry_report_template',
                                   vals)


    @http.route('/reg_app/reporting', type='http', auth='user', website=True)
    def reg_reporting(self):
        print('sdsd')
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
        print(data,'data')
        return http.request.render('registry_app.registry_report_template',vals )


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
        # shop_id = request.env['res.users'].browse(request.uid).shop_id
        user = request.env['res.users'].browse(request.uid)
        users = request.env['registry_app.users'].search(
            ['|', '|', ('create_uid', '=', user.id),
             ('user_id', '=', user.id),
             ('cooperative_id', '=', user.cooperative_id.id)])
        print('users', users)
        # values = {"users": users}
        return request.render("registry_app.registry_app_website_users",
                              {"users": users,
                               'user':user
                               })

    @http.route('/users/form', type='http', auth='user', )
    def reg_users_form(self):
        user = request.env['res.users'].browse(request.uid)
        values = {
            'user':user
        }
        return request.render("registry_app.website_reg_user_form_template",values )

    @http.route('/submit_users', type='http', auth='user', )
    def reg_users_create(self, **kw):
        user = request.env['res.users'].browse(request.uid)
        print('co',user.cooperative_id )
        print('coo', user.shop_id.cooperative_id )
        if user.shop_id.cooperative_id is None or user.cooperative_id is None:
            print('sds')
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

    # Print reports
    @http.route('/report/new/', methods=['POST', 'GET'], csrf=False,
                type='http', auth="user", website=True)
    def print_id(self, **kw):
        print('asd')
        # pdf, _ = request.env.ref(
        #     'Model_Name.Action_Name').sudo().render_qweb_pdf(
        #     [int(purchase_id)])
        # pdfhttpheaders = [('Content-Type', 'application/pdf'),
        #                   ('Content-Length', len(pdf)),
        #                   ('Content-Disposition', 'catalogue' + '.pdf;')]
        # return request.make_response(pdf, headers=pdfhttpheaders)


class RegistryAppPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        rtn = super(RegistryAppPortal, self)._prepare_home_portal_values(
            counters)
        print(f'rtn: {rtn}')
        rtn['registry_log_count'] = request.env[
            'registry_app.registry_app'].search_count([])
        return rtn
        # values = super()._prepare_home_portal_values(counters)

    @http.route(['/my/registry_log'], type='http', auth='user', website=True)
    def registry_app_list_view(self, **kw):
        registry_log = request.env['registry_app.registry_app'].search([])
        vals = {
            'registry_log': registry_log,
            'page_name': 'registry_log_list_view'
        }
        return request.render('registry_app.registry_app_list_view_portal',
                              vals)

    @http.route([
        '/my/registry_log/<model("registry_app.registry_app"):registry_app_id>'],
        type='http', auth='user', website=True)
    def registry_app_form_view(self, registry_app_id, **kw):
        print('hello')
        return 'Hello'
