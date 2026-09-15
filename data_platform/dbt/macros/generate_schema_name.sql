{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ var('schema_prefix', '') }}{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
