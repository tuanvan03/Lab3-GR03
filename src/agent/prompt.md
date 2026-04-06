Question: {{ question }}
{% if histories %}
--- Conversation History ---
{% for entry in histories %}
{{ entry }}
{% endfor %}
--- End of History ---
{% endif %}
