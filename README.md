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

## setup (one-time)

### clone the repo

```bash
git clone https://github.com/tlon-team/anki-interleaver
```

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

1. In Anki, go to Tools > Manage Note Types
2. Select a note type used by one of the decks you listed above
3. Click **Fields...**
4. Click **Add**
5. Name it `MasterRank`
6. Check the "Sort by this field in the browser" option.
7. Repeat steps 2–6 until all relevant note types have the `MasterRank` field.

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

1. In the main Anki window, click **Browse**.
2. Search for all new cards within the decks you interleaved. Example:

   `is:new (deck:"Main::Japanese" OR deck:"Main::Swedish")`

   (The script will output and copy to the clipboard the exact text you need to
   paste.)
3. Sort the cards by 'Sort Field' (if it doesn't show up, right-click on the column
   headers and enable it).
4. Select all cards (Cmd/Ctrl + A).
5. Choose **Cards → Reposition…**
6. Use:
   - Start position: `1`
   - Step: `1`
   - Randomize order: unchecked
   - Shift positions of existing cards: unchecked

## cleanup

If you are happy with the new ordering, you can delete the `MasterRank` field.

## license

MIT
