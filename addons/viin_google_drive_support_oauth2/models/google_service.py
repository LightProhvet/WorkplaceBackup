import requests
import time
from werkzeug import urls

from odoo import api, models, _

TIMEOUT = 20

GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'


class GoogleService(models.AbstractModel):
    _inherit = 'google.service'

    @api.model
    def _get_google_token_uri(self, service, scope):
        if service != 'drive':
            return super(GoogleService, self)._get_google_token_uri(service, scope)

        get_param = self.env['ir.config_parameter'].sudo().get_param
        base_url = get_param('web.base.url')
        redirect_uri = urls.url_join(base_url, '/google_drive/authentication')
        encoded_params = urls.url_encode({
            'scope': scope,
            'redirect_uri': redirect_uri,
            'client_id': get_param('google_%s_client_id' % service),
            'response_type': 'code',
        })
        return '%s?%s' % (GOOGLE_AUTH_ENDPOINT, encoded_params)

    @api.model
    def generate_refresh_token(self, service, authorization_code):
        if service != 'drive':
            return super(GoogleService, self).generate_refresh_token(service, authorization_code)

        Parameters = self.env['ir.config_parameter'].sudo()
        client_id = Parameters.get_param('google_%s_client_id' % service)
        client_secret = Parameters.get_param('google_%s_client_secret' % service)
        base_url = Parameters.get_param('web.base.url')
        redirect_uri = urls.url_join(base_url, '/google_drive/authentication')

        # Get the Refresh Token From Google And store it in ir.config_parameter
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = {
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': "authorization_code"
        }
        try:
            req = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            content = req.json()
        except IOError:
            error_msg = _("Something went wrong during your token generation. Maybe your Authorization Code is invalid or already expired")
            raise self.env['res.config.settings'].get_config_warning(error_msg)

        return content.get('refresh_token', ''), content.get('access_token', ''), int(time.time()) + content.get('expires_in', 0)
