{% load i18n %}{% autoescape off %}{% url 'accounts:password_reset_confirm' uidb64=uid token=token as link %}{% blocktranslate with short_name=user.get_short_name %}Hi {{ short_name }},

you're receiving this email because you requested a password reset for your user account at _{{ site_name }}_.

Please [click here]({{ protocol }}://{{ domain }}{{ link }}) to choose a new password.{% endblocktranslate %}

{% include 'mail/_signature.md' %}{% endautoescape %}
