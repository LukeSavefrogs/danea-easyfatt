---
title: Roadmap
---

# 🚧 Roadmap di sviluppo

<!-- 💻🔨⏳ -->
{%- assign ordered_tasks = site.data.roadmap.tasks | group_by: 'category' %}

{% for category in site.data.roadmap.categories -%}
{%- assign current_category = ordered_tasks | where: "name", category.id -%}
{%- assign items = current_category[0].items | sort: "completed" | reverse -%}

{% for task in items -%}
{%- assign checkmark = " " -%}
{%- if task.completed == 100 -%}
{%- assign checkmark = "x" -%}
{%- endif -%}

{%- assign color = category.color -%}
{%- if task.color -%}
{%- assign color = task.color -%}
{%- endif -%}

{%- assign label = category.name -%}
{%- if task.label -%}
{%- assign label = task.label -%}
{%- endif -%}

{%- assign status = "" -%}
{%- if task.completed > 0 and task.completed < 100 -%}
{%- assign status = "(" | append: task.completed | append: "%)" -%}
{%- endif -%}


- [{{checkmark}}] {{task.title}}<span class="label {{"label-" | append: color}} label-reset">{{label}} {{status}}</span>  
  {{task.body}}
{% endfor -%}
{% endfor %}