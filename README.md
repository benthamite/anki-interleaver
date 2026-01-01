# Interleave new cards across multiple Anki decks

This repository contains a small Python script, `interleave.py`, that helps you
interleave *new* cards across multiple Anki decks while preserving the original
order *within each deck*.

The practical goal is to avoid finishing all new cards from one deck long before
you start making progress in another. Instead, you get a combined “master”
ordering that keeps you moving through each deck at roughly the same pace
(proportional to how many new cards each deck contains).

Example (Deck 1 has 4 new cards, Deck 2 has 2 new cards):

- Deck 1: D1[1], D1[2], D1[3], D1[4]
- Deck 2: D2[1], D2[2]

The resulting interleaving will be approximately 2:1:

- D1[1], D1[2], D2[1], D1[3], D1[4], D2[2]

## setup (one-time)

### install any missing requirements

- Desktop Anki
- [AnkiConnect](https://foosoft.net/projects/anki-connect/) installed and enabled
- Python 3
- Python dependency: `requests`

### clone the repo

```bash
git clone https://github.com/tlon-team/anki-interleaver
```

## usage

### backup (recommended)

Before running the script on a large collection, make a backup: in Anki, go to
**File → Create Backup** and select a location for the backup file.

### run the script

1. Open Anki (AnkiConnect must be running; keep Anki open).
2. Run:

```bash
python interleave.py
```

3. Follow the prompts.

## license

MIT
