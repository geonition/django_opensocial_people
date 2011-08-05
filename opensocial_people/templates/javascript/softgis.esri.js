/* global dojo, djConfig, console, esri  */
{% extends "javascript/softgis_client.commons.js" %}

{% block library_specific_block %}
	{% for client in softgis_clients %}
	{{ client }}
	{% endfor %}
{% endblock %}
