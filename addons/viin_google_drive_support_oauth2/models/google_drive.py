import time
import requests

from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import RedirectWarning, UserError

from odoo.addons.google_account.models.google_service import GOOGLE_TOKEN_ENDPOINT, TIMEOUT

class GoogleDrive(models.Model):
    _inherit = 'google.drive.config'

    def _module_deprecated(self):
        # Over write function _module_deprecated to avoid deprecated
        get_param = self.env['ir.config_parameter'].sudo().get_param
        if not get_param('google_drive_client_id') or not get_param('google_drive_client_secret'):
            raise ValidationError(_("Please configure your Google Drive credentials in the general settings to link a Google Drive account!"))
        return False
    
    @api.model
    def get_access_token(self, scope=None):
        Config = self.env['ir.config_parameter'].sudo()
        google_drive_refresh_token = Config.get_param('google_drive_refresh_token')
        access_token = Config.get_param('google_drive_access_token')
        token_expiration = int(Config.get_param('google_drive_access_token_expiration'))         
        now_timestamp = int(time.time())
        user_is_admin = self.env.is_admin()
        if not google_drive_refresh_token:
            if user_is_admin:
                dummy, action_id = self.env['ir.model.data'].get_object_reference('base_setup', 'action_general_configuration')
                msg = _("There is no refresh code set for Google Drive. You can set it up from the configuration panel.")
                raise RedirectWarning(msg, action_id, _('Go to the configuration panel'))
            else:
                raise UserError(_("Google Drive is not yet configured. Please contact your administrator."))
            
        # Check if access token is not existed or expired
        # If access token is existed but not expired, continue using existed access token
        # If access token is not existed or expired, send request to achieve a new access token thanks to refresh token
        if token_expiration and access_token and token_expiration > now_timestamp:
            return access_token
        
        google_drive_client_id = Config.get_param('google_drive_client_id')
        google_drive_client_secret = Config.get_param('google_drive_client_secret')
        #For Getting New Access Token With help of old Refresh Token
        data = {
            'client_id': google_drive_client_id,
            'refresh_token': google_drive_refresh_token,
            'client_secret': google_drive_client_secret,
            'grant_type': "refresh_token",
            'scope': scope or 'https://www.googleapis.com/auth/drive'
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            req = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
        except requests.HTTPError:
            if user_is_admin:
                dummy, action_id = self.env['ir.model.data'].get_object_reference('base_setup', 'action_general_configuration')
                msg = _("Something went wrong during the token generation. Please request again an authorization code .")
                raise RedirectWarning(msg, action_id, _('Go to the configuration panel'))
            else:
                raise UserError(_("Google Drive is not yet configured. Please contact your administrator."))     
        access_token = req.json().get('access_token')
        expiration_time = int(time.time()) + req.json().get('expires_in', 0)
        Config.set_param('google_drive_access_token', access_token)
        Config.set_param('google_drive_access_token_expiration', expiration_time)   
        return access_token        
