{% load i18n %}{% autoescape off %}{% url 'accounts:activate' uid token as link %}{% blocktrans with short_name=user.get_short_name %}Hi {{ short_name }},

you're receiving this email because you requested a new account at {{ site_name }}.

Please [click here]({{ protocol }}://{{ domain }}{{ link }}) to activate your account.{% endblocktrans %}

{% include 'mail/_signature.md' %}{% endautoescape %}
