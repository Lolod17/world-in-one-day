# world-in-one-day

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/lolod17/world-in-one-day/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/lolod17/world-in-one-day/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One 1024×1024 page for Friday 20 November 2026: sixteen stories from six
regions, each one an event of that day or first reported that day, with the
date set at the size a reader cannot miss. Three splashes carry the day's
biggest events with a drawn scene each, nine numbered cards cover the rest of
the world, and four short lines close the page. Big type, flat colour, no
detail that only survives at full size — the page is built to be read at
about 300 pixels across.

## How it works

`tools/render.py` draws the page at build time with real fonts and saves
`entry.png`. `main.py` is the entry the grader runs: it copies that committed
image to `$MAKEFUN_OUTPUT_DIR/entry.png` and nothing else, so both of the
grader's runs write identical bytes with no network, no clock and no state.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
python3 tools/render.py   # rebuild the page (needs Pillow and the macOS system fonts)
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
