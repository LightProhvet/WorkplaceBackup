import logging
from werkzeug.utils import redirect
from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GoogleAuth(http.Controller):
  
    @http.route('/google_drive/authentication', type='http', auth="public")
    def oauth2_callback(self, **kw):
        """ This route/function is called by Google when user Accept/Refuse the consent of Google """
        if not request.env.user.has_group('base.group_system'):
            _logger.error('Google Drive: non-system user trying to link an Google Drive account.')
            raise Forbidden()

        params = request.env['ir.config_parameter'].sudo()
        authorization_code = kw.get('code', False)
        params.set_param('google_drive_authorization_code', authorization_code)
        #Get refesh token and store in database
        request.env['res.config.settings'].sudo().confirm_setup_token()
        return redirect('/web')
