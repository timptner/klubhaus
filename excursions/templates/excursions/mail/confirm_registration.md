{% load i18n %}{% autoescape off %}{% url 'field_trips:field_trip_detail' pk as link %}{% blocktrans %}Hi {{ name }},

we confirm your registration for our field trip _{{ title }}_ on {{ date }}.

You can find more information on the [detail page]({{ protocol }}://{{ domain }}{{ link }}) of our field trip.{% endblocktrans %}

{% include 'mail/_signature.md' %}{% endautoescape %}
