# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        # because frontend session_info uses this key and is embedded in
        # the view source
        print('info',info)
        user = request.env['res.users'].browse(request.session.uid)
        info["is_registry_app_user"] = user.is_from_registry_app
        print('is_registry_app_user',info["is_registry_app_user"])
        return info
