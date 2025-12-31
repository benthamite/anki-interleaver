#!/usr/bin/env python3
import requests
import sys

ANKI_CONNECT_URL = "http://127.0.0.1:8765"

# ---------- CONFIG: matches your setup ----------

# Put your real deck names here.
DECK_NAMES = [
    "deck1",
    "deck2",
]

# The field to write the final global order into.
MASTERRANK_FIELD = "MasterRank"

# Set to False to prevent the script from trying (and failing) to reposition cards.
# You will still need to do the manual reposition step in Anki after running this.
UPDATE_CARD_DUE = False

# ------------------------------------------------


def anki_invoke(action, **params):
    """Call AnkiConnect and return the result or raise."""
    payload = {"action": action, "version": 6, "params": params}
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("error") is not None:
            raise RuntimeError(f"AnkiConnect API error on action '{action}': {data['error']}")
        return data.get("result")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to connect to AnkiConnect. Is Anki open? Error: {e}")


def main():
    if not DECK_NAMES:
        print("DECK_NAMES is empty; edit the script.", file=sys.stderr)
        sys.exit(1)

    print("Connecting to AnkiConnect...")

    # Preflight: ensure the MasterRank field exists on all note types used in the
    # relevant decks before doing any updates.
    print(f"\n--- Preflight: checking '{MASTERRANK_FIELD}' field exists ---")
    decks_query = " or ".join([f'deck:"{d}"' for d in DECK_NAMES])
    note_ids = anki_invoke("findNotes", query=decks_query)
    if not note_ids:
        print("No notes found in the specified decks.")
        sys.exit(0)

    notes_info = anki_invoke("notesInfo", notes=note_ids)

    models_missing_field = set()
    for note in notes_info:
        model_name = note.get("modelName")
        fields = note.get("fields", {})
        if model_name and MASTERRANK_FIELD not in fields:
            models_missing_field.add(model_name)

    if models_missing_field:
        missing = ", ".join(sorted(models_missing_field))
        raise RuntimeError(
            f"Missing required note field '{MASTERRANK_FIELD}' on note types: {missing}. "
            "Add the field in Anki (Browse → select a note → Fields… → Add) and re-run."
        )

    print(f"OK: '{MASTERRANK_FIELD}' exists on all relevant note types.")

    # Step 1: For each deck, get its list of new cards in their default Anki order.
    processed_decks = []
    total_new = 0
    print("\n--- Finding New Cards in Decks ---")
    for name in DECK_NAMES:
        query = f'deck:"{name}" is:new'
        # findCards returns cards sorted by due number, which is the natural new card order.
        ordered_cids = anki_invoke("findCards", query=query)
        count = len(ordered_cids)
        print(f"  Deck '{name}': Found {count} new cards.")
        processed_decks.append({"name": name, "cards": ordered_cids, "count": count})
        total_new += count

    if total_new == 0:
        print("\nNo new cards were found in the specified decks.")
        sys.exit(0)

    # Step 2: Build the global interleaving schedule based on deck sizes.
    print(f"\nTotal new cards: {total_new}. Computing global schedule...")
    indexes = [0] * len(processed_decks)
    global_order = []
    for g in range(total_new):
        best_deck_idx = -1
        best_score = None
        for i, d in enumerate(processed_decks):
            if indexes[i] >= d["count"]: continue
            score = (indexes[i] / d["count"]) - (g / total_new)
            if best_score is None or score < best_score:
                best_score, best_deck_idx = score, i
        
        d = processed_decks[best_deck_idx]
        cid = d["cards"][indexes[best_deck_idx]]
        global_order.append((cid, g))
        indexes[best_deck_idx] += 1
    print("Global schedule computed.")

    # Step 3: Write MasterRank to notes. This requires mapping cards back to their notes.
    # We build a map of Card ID -> Note ID. This is robust against broken cardsInfo.
    print("Building Card ID to Note ID map...")

    cid_to_nid_map = {}
    for note in notes_info:
        for cid in note.get('cards', []):
            cid_to_nid_map[cid] = note['noteId']

    # Determine the final rank for each note.
    note_to_update = {}
    for cid, rank in global_order:
        nid = cid_to_nid_map.get(cid)
        if nid:
            if nid not in note_to_update or rank < note_to_update[nid]:
                note_to_update[nid] = rank
    
    print(f"Updating {len(note_to_update)} notes one-by-one (this may take a moment)...")
    updated_count = 0
    total_to_update = len(note_to_update)
    for nid, rank in note_to_update.items():
        payload = {"note": {"id": nid, "fields": {MASTERRANK_FIELD: str(rank)}}}
        anki_invoke("updateNoteFields", **payload)
        updated_count += 1
        print(f"\r  Progress: {updated_count}/{total_to_update}", end="")
    print("\nMasterRank field updated.")

    # Step 4: Remind user to reposition manually.
    if not UPDATE_CARD_DUE:
        deck_disjunction = " OR ".join([f'deck:"{d}"' for d in DECK_NAMES])
        print("\n[SUCCESS] Script finished. Now, please reposition cards manually in Anki.")
        print(f"Paste this in your browser: is:new ({deck_disjunction})")
        print("2. Sort by the 'MasterRank' column.")
        print("3. Select all cards and use 'Cards -> Reposition'.")
    else:
        # This part is skipped but left for clarity.
        print("\nUPDATE_CARD_DUE is True, but this installation does not support automated repositioning.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
