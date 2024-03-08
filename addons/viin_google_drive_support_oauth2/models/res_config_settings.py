from odoo import fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_drive_client_id = fields.Char(string='Google Drive Client ID', config_parameter='google_drive_client_id')
    google_drive_client_secret = fields.Char(string="Google Drive Client Secret", config_parameter='google_drive_client_secret')
    google_drive_access_token = fields.Char(string='Access Token', config_parameter='google_drive_access_token')
    google_drive_access_token_expiration = fields.Integer(string='Access Token Expiration Timestamp', config_parameter='google_drive_access_token_expiration')

    def _compute_drive_uri(self):
        google_drive_uri = self.env['google.service']._get_google_token_uri('drive', scope=self.env['google.drive.config'].get_google_scope())
        google_drive_uri += '&access_type=offline'
        for config in self:
            config.google_drive_uri = google_drive_uri

    def confirm_setup_token(self):
        params = self.env['ir.config_parameter'].sudo()
        authorization_code = params.get_param('google_drive_authorization_code')
        refresh_token, access_token, expires_in = self.env['google.service'].generate_refresh_token('drive', authorization_code)
        params.set_param('google_drive_refresh_token', refresh_token)
        params.set_param('google_drive_access_token', access_token)
        params.set_param('google_drive_access_token_expiration', expires_in)

    def action_setup_token(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        if get_param('google_drive_client_id') and get_param('google_drive_client_secret'):
            return super(ResConfigSettings,self).action_setup_token()
        else:
            raise UserError(_('Please configure your Google Drive credentials in the general settings to link a Google Drive account!'))

    def authorization_code_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.google_drive_uri,
        }
