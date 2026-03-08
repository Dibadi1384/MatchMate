# Field sources config

**`field_sources.json`** maps each profile field (e.g. from `profile_predictions.csv` / `user_gemini_profile`) to:

- **best_source:** Short description of which data best informs this field (no OAuth URLs).
- **data_sources:** Which parts of the **compact JSON** (and DB) to use for this field: `chrome`, `youtube`, `calendar`, `maps`. Matching uses the compact JSON file only; this config says which section(s) apply to each field.
- **inference_strength:** Optional. `weak` or `weak_without_fit` means the field is inferred with less confidence when using only the listed sources.

**Matching:** Use the per-user compact JSON file (e.g. `compact_json/{user_id}.json`) and this config. For each field, use only the sections listed in `data_sources` (e.g. for `location` use `maps` and `calendar`; for `hobbies` use `chrome` and `youtube`). No OAuth or scope URLs are used; everything is driven by the extracted/compacted data.
