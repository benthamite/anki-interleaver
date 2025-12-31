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

## setup (one-time)

### configure the Python script

Open `interleave.py` and set the list of deck names:

- `DECK_NAMES`: exact deck names as shown in Anki (including `Parent::Child`
  notation if applicable)

Example:

```python
DECK_NAMES = [
    "Main::Japanese",
    "Main::Swedish",
]
```

### create the `MasterRank` note field

In Anki:

1. Open **Browse**
2. Select a note of the note type(s) you use in the target decks
3. Click **Fields...**
4. Click **Add**
5. Name it `MasterRank`
6. Repeat for each note type used by the decks listed in the previous step.

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

When it finishes, it will have updated the `MasterRank` field on the notes it
processed.

### apply the order in Anki

Because AnkiConnect capabilities vary (and some installations do not support
repositioning actions via the API), the final “reposition” step is done manually:

1. In Anki, open **Browse**
2. Search for the decks you interleaved (example):

   `deck:"Main::Japanese" or deck:"Main::Swedish"`

3. Add the `MasterRank` column:
   - In the Browse window, click the **Fields** button (or **Columns**, depending
     on your Anki version), and enable `MasterRank`.
4. Click the `MasterRank` column header to sort ascending.
5. Select all cards (`Cmd+A` on macOS).
6. Choose **Cards → Reposition…**
7. Use:
   - Start position: `1`
   - Step: `1`

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

If you’re browsing multiple note types at once, ensure the note type(s) used by
the target decks include a `MasterRank` field.

## license

MIT
