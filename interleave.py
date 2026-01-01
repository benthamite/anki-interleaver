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

    # Preflight: ensure the decks exist.
    print("\n--- Preflight: checking decks exist ---")
    deck_names_in_anki = set(anki_invoke("deckNames"))
    missing_decks = [d for d in DECK_NAMES if d not in deck_names_in_anki]
    if missing_decks:
        missing = ", ".join(missing_decks)
        raise RuntimeError(
            f"Deck(s) not found in Anki: {missing}. "
            "Fix DECK_NAMES (must match exactly) and re-run."
        )


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

    # Step 3: Reposition new cards directly via AnkiConnect.
    print(f"\nRepositioning {len(global_order)} new cards (this may take a while)...")
    updated_count = 0
    total_to_update = len(global_order)
    for cid, rank in global_order:
        # Card positions are 1-indexed.
        new_position = rank + 1
        anki_invoke(
            "setSpecificValueOfCard",
            card=cid,
            keys=["due"],
            newValues=[new_position],
        )
        updated_count += 1
        print(f"\r  Progress: {updated_count}/{total_to_update}", end="")
    print("\nNew cards repositioned.")

    print("\n[SUCCESS] Script finished. New cards have been repositioned.")




if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
