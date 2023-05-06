import logging
import requests

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from typing import Optional

logger = logging.getLogger(__name__)


class EmailBackend(BaseEmailBackend):
    """
    A custom email backend for postmark.
    """

    endpoint = 'https://api.postmarkapp.com/email/batch'

    @staticmethod
    def format_payload(email_message: EmailMultiAlternatives):
        payload = {
            'From': email_message.from_email,
            'To': ','.join(email_message.recipients()),
        }

        if email_message.cc:
            payload['Cc'] = ','.join(email_message.cc)

        if email_message.bcc:
            payload['Bcc'] = ','.join(email_message.bcc)

        if email_message.subject:
            payload['Subject'] = str(email_message.subject)  # Force lazy translations

        if email_message.alternatives:
            html_content = None

            for content, mime_type in email_message.alternatives:
                if mime_type != 'text/html':
                    raise NotImplementedError("Only email alternatives with MIME Type 'text/html' are supported")
                html_content = content

            if html_content:
                payload['HtmlBody'] = html_content

        if email_message.body:
            payload['TextBody'] = email_message.body

        if email_message.reply_to:
            payload['ReplyTo'] = ','.join(email_message.reply_to)

        if email_message.extra_headers:
            payload['Headers'] = email_message.extra_headers

        payload.update({
            'TrackOpens': False,
            'TrackLinks': 'None',
            'MessageStream': 'outbound',
        })

        return payload

    def send_messages(self, email_messages):
        if len(email_messages) > 500:
            raise NotImplementedError("Only 500 emails can be send simultaneous")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Postmark-Server-Token': settings.POSTMARK_API_TOKEN,
        }

        payload = [self.format_payload(msg) for msg in email_messages]

        response = requests.post(self.endpoint, json=payload, headers=headers)

        if response.status_code == 401:
            raise PermissionError("API Token is unauthorized")

        if response.status_code == 422:
            raise ValueError("Payload contained malformed messages(s)")

        data = response.json()

        return len([msg for msg in data if msg['ErrorCode'] == 0])


PostmarkError = tuple[int, str]


class PostmarkTemplate:
    """
    Postmark API for sending emails with templates.
    """

    endpoint_url = 'https://api.postmarkapp.com'

    _headers = {
        'Accept': 'application/json',
        'X-Postmark-Server-Token': settings.POSTMARK_API_TOKEN,
    }

    @staticmethod
    def _prepare_message(sender: str, recipient: str, template_alias: str, template_model: dict,
                         message_stream: str) -> dict:

        template_model.update({
            'product_url': 'https://klubhaus.farafmb.de',
            'product_name': 'Klubhaus',
            'company_name': 'Fachschaftsrat Maschinenbau',
            'company_address': 'Universitätsplatz 2, 39106 Magdeburg',
        })

        message = {
            'From': sender,
            'To': recipient,
            'TemplateAlias': template_alias,
            'TemplateModel': template_model,
            'TrackOpens': False,
            'TrackLinks': 'None',
            'MessageStream': message_stream,
        }

        return message

    @staticmethod
    def _validate_response(response: requests.Response) -> None:
        if response.status_code == 422:
            data = response.json()
            code = data['ErrorCode']
            msg = data['Message']
            logger.error(f"Postmark API responded with an error: [{code}] {msg}")
            raise ValueError("Payload contains malformed json or incorrect fields.")

    @staticmethod
    def _validate_payload(data: dict) -> Optional[tuple]:
        if data['Message'] == 'OK':
            return

        error = data['ErrorCode'], data['Message']

        logger.warning("Received Postmark API error: %i, %s", error)

        return error

    def send_message(self, recipient: str, template_alias: str, template_model: dict,
                     sender: str = settings.DEFAULT_FROM_EMAIL) -> Optional[PostmarkError]:

        endpoint_url = self.endpoint_url + '/email/withTemplate/'

        payload = self._prepare_message(sender, recipient, template_alias, template_model, 'outbound')

        response = requests.post(endpoint_url, headers=self._headers, json=payload)
        self._validate_response(response)

        data = response.json()

        error = self._validate_payload(data)

        return error if error else None

    def send_message_batch(self, recipients: list[str], template_models: list[dict], template_alias: str,
                           sender: str = settings.DEFAULT_FROM_EMAIL) -> dict[str, PostmarkError]:

        if len(recipients) != len(template_models):
            raise ValueError("lists of recipients and payloads must be the same length")

        endpoint_url = self.endpoint_url + '/email/batchWithTemplate/'

        headers = self._headers
        headers['Content-Type'] = 'application/json'

        messages = []
        for recipient, template_model in zip(recipients, template_models):
            message = self._prepare_message(sender, recipient, template_alias, template_model, 'broadcast')
            messages.append(message)

        payload = {
            'Messages': messages,
        }

        response = requests.post(endpoint_url, headers=headers, json=payload)
        self._validate_response(response)

        data: list[dict] = response.json()

        errors = {}
        for index, msg in enumerate(data):
            error = self._validate_payload(msg)

            if error:
                recipient = recipients[index]
                errors[recipient] = error

        return errors
