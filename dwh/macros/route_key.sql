{% macro route_key(origin_column, destination_column) %}
md5(upper({{ origin_column }}) || '-' || upper({{ destination_column }}))
{% endmacro %}
