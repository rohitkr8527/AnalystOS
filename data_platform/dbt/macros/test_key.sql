{% test key(model, columns) %}
select {% for column in columns %}{{ column }}{% if not loop.last %}, {% endif %}{% endfor %}
from {{ model }}
group by {% for column in columns %}{{ column }}{% if not loop.last %}, {% endif %}{% endfor %}
having count(*) > 1
    or {% for column in columns %}{{ column }} is null{% if not loop.last %} or {% endif %}{% endfor %}
{% endtest %}
