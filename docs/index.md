---
layout: home
title: Ren'Py Vita Catalogue
---

<p align="center"><strong>SPDW FACTORY · PLAYSTATION VITA</strong></p>

# Stories worth carrying. Ports worth testing.

A community catalogue for Ren'Py visual novels and games being evaluated, adapted or already ported to PlayStation Vita.

> **Reality check:** a title in this catalogue is not automatically playable. Suggestions, community projects, partial ports and verified tests are kept separate.

## Explore

- [Browse every title]({{ '/catalogue/' | relative_url }})
- [Community port installation guides](https://github.com/SilverCrow2323/renpy-psvita-ports/blob/main/docs/PORTING-GUIDES.md)
- [Compatibility guide](https://github.com/SilverCrow2323/renpy-psvita-ports/blob/main/docs/COMPATIBILITY.md)
- [Testing checklist](https://github.com/SilverCrow2323/renpy-psvita-ports/blob/main/docs/TESTING.md)
- [Suggest a title](https://github.com/SilverCrow2323/renpy-psvita-ports/issues/new?template=ren-py-game.md)

## Status legend

| Status | Meaning |
|---|---|
| Suggested · not evaluated | A community member proposed the game; no technical test is claimed |
| Under investigation | Source/build details or a reproducible test are being collected |
| Partial / blocked | A test exists, but known failures prevent a full-playability claim |
| Community port linked | A separate Vita project was supplied; not independently verified by this catalogue |
| Verified playable | A named build completed a documented playthrough test on a named runtime and Vita |

## Featured titles

{% assign featured = site.games | sort: "title" %}
<div class="game-grid">
{% for game in featured limit: 8 %}
  <article class="game-card">
    {% if game.cover %}<a href="{{ game.url | relative_url }}"><img src="{{ game.cover | escape }}" alt="{{ game.title | escape }} cover" loading="lazy"></a>{% endif %}
    <h3><a href="{{ game.url | relative_url }}">{{ game.title | escape }}</a></h3>
    <p>{{ game.status | default: "Suggested · not evaluated" }}</p>
  </article>
{% endfor %}
</div>

## What we do not do

We do not redistribute commercial game data, cracked builds, proprietary scripts or artwork. The future distribution tool will inspect and package files supplied by the user; it will not bypass DRM or turn unsupported engine features into compatible ones by wishful thinking.
