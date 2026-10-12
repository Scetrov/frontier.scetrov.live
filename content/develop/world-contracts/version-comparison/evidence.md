+++
title = "Evidence, contradictions, and limits"
weight = 70
+++

Evidence has an order of authority: pinned Move source and tests establish implemented behavior; manifests and deployment artifacts establish only their explicit environment facts; upstream prose is contextual and can be stale. All factual upstream references in this chapter are immutable commit URLs from the [canonical cursor](../).

The reviewed dev tree retains v0 source below [`contracts/archive`](https://github.com/evefrontier/world-contracts/tree/d2027030ac168faa3da86dbaedd17c1f2d0a3845/contracts/archive), while active packages are elsewhere. The decoder README's `contracts/world` wording conflicts with that active layout. The earlier claim that the dev deployment manifest omits inventory is no longer true: the [reviewed manifest](https://github.com/evefrontier/world-contracts/blob/d2027030ac168faa3da86dbaedd17c1f2d0a3845/deployments/dev/world.json) names core, character, currency, inventory, and metadata. The [live manifest](https://github.com/evefrontier/world-contracts/blob/d2027030ac168faa3da86dbaedd17c1f2d0a3845/deployments/live/world.json) names MVR app capabilities but does not list published packages. No manifest establishes which code is active in-game.

Active [Entity deletion](https://github.com/evefrontier/world-contracts/blob/d2027030ac168faa3da86dbaedd17c1f2d0a3845/contracts/core/sources/entity.move) now aborts with `EComponentsInstalled` while any component is still installed, so a delete leaves no orphaned component dynamic fields.
Server-signed proofs are likewise implemented: [proof](https://github.com/evefrontier/world-contracts/blob/d2027030ac168faa3da86dbaedd17c1f2d0a3845/contracts/core/sources/services/proof.move) verifies kind, sender, deadline, admin server, and the server's Ed25519 signature (via [sig_verify](https://github.com/evefrontier/world-contracts/blob/d2027030ac168faa3da86dbaedd17c1f2d0a3845/contracts/core/sources/services/sig_verify.move)), while [docking](https://github.com/evefrontier/world-contracts/blob/d2027030ac168faa3da86dbaedd17c1f2d0a3845/contracts/core/sources/services/docking.move) still allows an admin/sponsor attestation as a transitional path.
These are source-observed facts, not runtime findings.

No Sui, Docker, or deployed-environment execution was performed for this documentation review. Consequently source review does not verify runtime compatibility, publish status, live game activation, server configuration, or production security properties. Re-run the maintenance workflow after either branch advances or is rewritten; it pins candidates, accounts for changed files, and preserves this cursor until validation succeeds.
