# Comparison completeness reference

Before completion, account for every changed relevant file and all active/archive Move modules. For each v0 domain and active v1 module, record one of: `active-v1`, `redesigned`, `partial`, `archived-only`, `not-yet-ported`, `main-only`, `deployment-unknown`.

Review package manifests; public/package-visible functions, structs/abilities, aborts, events and indexer payloads; tests; SDK/PTB builders; MVR/deployment artifacts; Docker, localnet, accounts, CI, package management, and error decoding. Archive code is historical evidence only. Pair every difference with retained principles and developer/migration impact.

Use immutable source URLs. State whether a claim is source/test fact, manifest/deployment fact, inference, contradiction, or unknown. Do not infer deployment, runtime behavior, production readiness, or full domain portability from source presence. Report uncategorized changed files, missing coverage, mutable links, and residual uncertainty as incomplete.