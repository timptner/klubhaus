from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse_lazy

from accounts.models import User, Modification
from klubhaus.mails import PostmarkTemplate


class Command(BaseCommand):
    help = "Send an email to all admins informing about pending modification requests."

    def handle(self, *args, **options):
        admins = User.objects.filter(is_superuser=True)
        modifications = Modification.objects.filter(state=Modification.REQUESTED)
        amount = modifications.count()

        if amount == 0:
            self.stdout.write(
                "Zero pending modification requests. No need to send mails."
            )
            return

        template = PostmarkTemplate()

        recipients = []
        payloads = []
        for admin in admins:
            recipients.append(admin.email)
            payload = {
                'first_name': admin.first_name,
                'amount': amount,
                'action_url': 'https://klubhaus.farafmb.de' + reverse_lazy('accounts:modification_list'),
            }
            payloads.append(payload)

        errors = template.send_message_batch(recipients, payloads, 'modification-admin-notification')

        if errors:
            recipients, error_list = zip(*errors.items())
            raise CommandError(f"There were {len(errors)} errors while trying to send mails. ({', '.join(recipients)})")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully sent {admins.count()} mails.")
            )
