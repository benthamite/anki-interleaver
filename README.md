# Interleave new cards across multiple Anki decks

This repository contains a small Python script, `interleave.py`, that helps you
interleave *new* cards across multiple Anki decks while preserving the original
order *within each deck*.

The practical goal is to avoid finishing all new cards from one deck long before
you start making progress in another. Instead, you get a combined “master”
ordering that keeps you moving through each deck at roughly the same pace
(proportional to how many new cards each deck contains).

This is especially useful when you have (for example):

- Deck 1 with 4000 new cards
- Deck 2 with 2000 new cards

…and you want the global order to behave like a 2:1 interleaving:

- D1[1], D1[2], D2[1], D1[3], D1[4], D2[2], …

## what the script does

At a high level, `interleave.py`:

1. Pulls the list of *new cards* in each selected deck via AnkiConnect.
2. Uses the order Anki already assigns to new cards in each deck (“new card
   position”, i.e. the internal new-card ordering) as the deck’s internal order.
3. Builds a combined schedule that tries to keep each deck “on pace” according
   to its share of total new cards.
4. Writes a `MasterRank` value (a note field you create) to each note so you can
   sort in the Anki browser.
5. You then perform the final “Cards → Reposition…” step manually in Anki,
   sorted by `MasterRank`.

The script does **not** rely on a manually maintained per-deck position field.

## requirements

- Desktop Anki
- [AnkiConnect](https://foosoft.net/projects/anki-connect/) installed and enabled
- Python 3
- Python dependency: `requests`

## installation

Clone this repo and install dependencies:

```bash
pip install requests
```

## setup in Anki (one-time)

### 1) create the `MasterRank` note field

`MasterRank` must be a **note field** (not a browser column).

In Anki:

1. Open **Browse**
2. Select a note of the note type(s) you use in the target decks
3. Click **Fields...**
4. Click **Add**
5. Name it `MasterRank`
6. Repeat for each note type used by the decks you’ll interleave (if you have
   multiple note types)

If a deck contains multiple note types, you must add `MasterRank` to all of
them, otherwise those notes cannot be updated consistently.

## configuration

Open `interleave.py` and set the list of deck names:

- `DECK_NAMES`: exact deck names as shown in Anki (including `Parent::Child`
  notation if applicable)

Example:

```python
DECK_NAMES = [
    "Main::Started::known_kanji",
    "Main::Started::8000+ most common swedish words",
]
```

If you change the `MasterRank` field name, also update `MASTERRANK_FIELD`
accordingly.

## usage

1. Open Anki (AnkiConnect must be running; keep Anki open).
2. Run:

```bash
python interleave.py
```

When it finishes, it will have updated the `MasterRank` field on the notes it
processed.

### apply the order in Anki (manual step)

Because AnkiConnect support differs across setups, the script is designed to
avoid repositioning via the API. Instead:

1. In Anki, open **Browse**
2. Search for your target decks, e.g.:

   `deck:"Deck 1" or deck:"Deck 2"`

3. Add the `MasterRank` column in the browser (see below)
4. Sort by `MasterRank` ascending
5. Select all matching cards
6. Menu: **Cards → Reposition...**
7. Use:
   - Start position: `1`
   - Step: `1`

After repositioning, studying new cards from the combined selection (for
example, a parent deck that includes the subdecks, or a filtered deck) will
follow that interleaved order.

## how to show `MasterRank` in the Anki browser

`MasterRank` is a note field, but it can still be shown as a browser column.

In the **Browse** window:

1. Click the column chooser (or right-click on a column header).
2. Choose **Fields** / **Columns** (wording varies by version).
3. Add the `MasterRank` field as a column.
4. Sort by clicking the `MasterRank` column header.

If you don’t see `MasterRank` in the list, check:

- You added the field to the note type currently shown in the browser
- You are browsing notes/cards that actually use a note type that contains
  `MasterRank`

## notes on ordering

### per-deck order

The script uses Anki’s existing new-card order per deck. Concretely, it queries
for `is:new` cards in each deck via AnkiConnect and uses the returned order as
the deck’s internal order.

If you want a different per-deck order, you should set that order in Anki first
(e.g. via the Browser and “Reposition”) and then re-run the script.

### interleaving strategy

If deck A has `nA` new cards and deck B has `nB` new cards, the script aims to
emit cards such that, at any point in the combined sequence, each deck has had
approximately the same fraction of its new cards scheduled.

This generalizes to any number of decks.

## troubleshooting

### “AnkiConnect error: ...”

- Confirm Anki is open
- Confirm AnkiConnect is installed and enabled
- Confirm AnkiConnect is listening on `http://127.0.0.1:8765`

### cards are missing / ranks look wrong

- Verify the cards are *new* (`is:new`)
- Verify those notes’ note types contain the `MasterRank` field
- If you have multiple cards per note, `MasterRank` is written on the note;
  multiple cards of the same note will share that value.

### i can’t see `MasterRank` in the browser

You almost certainly did not add the `MasterRank` field to the note type(s)
being displayed.

## safety

This script updates note fields (`MasterRank`). It does not delete notes/cards.

Still, it is recommended that you:

- Sync Anki before running it
- Make a backup (File → Export / or copy your collection) before applying
  large-scale changes

## license

Choose a license (MIT recommended) and add it as `LICENSE` if you intend others
to reuse/modify the script.
