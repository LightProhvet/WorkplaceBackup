from requests import post
import json

use_json=False
req = False
if use_json:
    application = 'application/json'
else:
    application = 'application/xml'
try:
    if self.debug_logger is not None:  # isinstance(self.debug_logger, Logger):
        self.debug_logger(request_xml, 'itella_request')
    if not api_key:
        raise UserError("API key missing, cannot send message. Check API Password under delivery carrier")
    headers = {'Content-Type': application,  # TODO: OR 'application/json' - _send_request param?
                 'Authorization': api_key}
    if secret:
        headers['X-Gateway-Secret'] = secret
    _logger.info(f"\n\n\n posting with header: {headers}\n\n url: {url} \n and content: {request_xml}")
    req = post(
        url,
        data=request_xml,
        headers=headers
    )
    _logger.info(f"\n\n i actually have data: {req.content}")
    req.raise_for_status()
    response_text = req.content
    if self.debug_logger is not None and not raw:
        self.debug_logger(response_text, 'itella_response')
except IOError:
    if not req or not req.content:
        raise UserError("Itella Server not found. Check your connectivity.")
    else:
        raise UserError(req.content)
_logger.info(f"\n\n and response: {response_text}")
if raw:
    return response_text
else:
    xml = False
    if xml:
        return etree.fromstring(response_text.decode(encoding="utf-8"))
    else:
        return json.loads(response_text)