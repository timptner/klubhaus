import requests

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


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
