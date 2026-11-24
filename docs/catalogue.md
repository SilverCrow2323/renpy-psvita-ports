---
layout: page
title: Game catalogue
permalink: /catalogue/
---

Browse the catalogue by title. Every page links back to its original proposal so the source of each claim stays visible.

{% assign games = site.games | sort: "title" %}
{% for game in games %}
### [{{ game.title | escape }}]({{ game.url | relative_url }})

**{{ game.status | default: "Suggested · not evaluated" }}** · [Source issue #{{ game.issue }}](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/{{ game.issue }})

{% if game.cover %}<a href="{{ game.url | relative_url }}"><img src="{{ game.cover | escape }}" alt="{{ game.title | escape }} cover" width="220" loading="lazy"></a>{% endif %}

{{ game.summary | default: "Community proposal. Technical details and compatibility have not yet been independently verified." }}

---
{% endfor %}
