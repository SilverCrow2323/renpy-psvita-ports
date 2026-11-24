# Wiki source and publishing

The wiki-source directory contains the tracked Markdown source for the practical GitHub Wiki. Edit these files rather than changing only the live Wiki.

## Page rules

- One topic per page.
- Start with a short explanation and say when the page is useful.
- Keep candidate, testing, available-port and failed-basic-conversion statuses distinct.
- Do not claim compatibility without test evidence.
- Do not upload copyrighted game files or private game assets.
- Link to the central README and the detailed docs/ pages for full instructions.

## Publishing

1. Open the [GitHub Wiki](https://github.com/SilverCrow2323/Renpy-Vita-Portings/wiki).
2. Ensure the Wiki has been initialized with a Home page.
3. From a clone with Git credentials, run: sh tools/publish_wiki.sh

The publisher copies reviewed Markdown pages to the special Wiki repository. This publishing step is separate from merging changes to this repository.
