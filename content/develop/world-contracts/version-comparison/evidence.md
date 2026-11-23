+++
title = "Evidence, contradictions, and limits"
weight = 70
+++

Evidence has an order of authority: pinned Move source and tests establish implemented behavior; manifests and deployment artifacts establish only their explicit environment facts; upstream prose is contextual and can be stale. All factual upstream references in this chapter are immutable commit URLs from the [canonical cursor](../).

The reviewed dev tree retains v0 source below [`contracts/archive`](https://github.com/evefrontier/world-contracts/tree/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/archive), while active packages are elsewhere. The decoder README's `contracts/world` wording conflicts with that active layout. The earlier claim that the dev deployment manifest omits inventory is stale: the [reviewed manifest](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/deployments/dev/world.json) lists all nine active packages and their MVR entries. The [live manifest](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/deployments/live/world.json) names MVR app capabilities but does not list published packages. No manifest establishes which code is active in-game.

Active [Entity deletion](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/core/sources/entity.move) now aborts with `EComponentsInstalled` while any component is still installed, so a delete leaves no orphaned component dynamic fields.
Server-signed proofs are likewise implemented: [proof](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/core/sources/services/proof.move) verifies kind, sender, deadline, admin server, and the server's Ed25519 signature (via [sig_verify](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/core/sources/services/sig_verify.move)). The old standalone docking service is gone: [Entity](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/core/sources/entity.move) records docking state through admin-gated requests instead.
These are source-observed facts, not runtime findings.

No Sui, Docker, or deployed-environment execution was performed for this documentation review. Consequently source review does not verify runtime compatibility, publish status, live game activation, server configuration, or production security properties. Re-run the maintenance workflow after either branch advances or is rewritten; it pins candidates, accounts for changed files, and preserves this cursor until validation succeeds.
