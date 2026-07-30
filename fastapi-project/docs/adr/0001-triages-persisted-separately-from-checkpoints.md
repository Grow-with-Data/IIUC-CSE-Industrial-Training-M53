# Triages are persisted separately from LangGraph checkpoints

The LangGraph Postgres checkpointer stores Conversation state, but its tables are
an internal serialization format with no query surface, and the LangGraph docs
recommend pruning old checkpoints on a schedule to stop them growing unboundedly.
Treating the checkpoint as the record of Triages would therefore make routing and
reporting queries require deserializing every checkpoint blob, and would let a
retention policy silently delete business data. We write each Triage to a
`triages` table we own, and treat the checkpoint as disposable conversation
memory.

## Consequences

- The two writes are not atomic. LangGraph commits its checkpoint in its own
  transaction; the `triages` insert is separate. We accept this rather than
  reimplement the checkpointer.
- A failed `triages` insert logs loudly but does not fail the customer's turn.
  This is only safe because the Triage is also held in graph state, so a missing
  row is backfillable by replaying the checkpoint — the data is not lost, only
  its query surface is delayed.
- Checkpoints may be pruned freely without consulting anyone. `triages` may not.
