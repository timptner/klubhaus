{% load i18n %}{% autoescape off %}{% blocktrans %}Hi {{ name }},

you have been **removed** as a participant of our field trip _{{ title }}_.{% endblocktrans %}

{% trans "If you are sure that this is a mistake please contact us immediately." %}

{% include 'mail/_signature.md' %}{% endautoescape %}
