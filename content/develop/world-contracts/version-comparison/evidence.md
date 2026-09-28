+++
title = "Evidence, contradictions, and limits"
weight = 70
+++

Evidence has an order of authority: pinned Move source and tests establish implemented behavior; manifests and deployment artifacts establish only their explicit environment facts; upstream prose is contextual and can be stale. All factual upstream references in this chapter are immutable commit URLs from the [canonical cursor](../).

The reviewed dev tree retains v0 source below [`contracts/archive`](https://github.com/evefrontier/world-contracts/tree/8bf651194898b693211614632561a3926c6de99c/contracts/archive), while active packages are elsewhere. The decoder README's `contracts/world` wording conflicts with that active layout. The earlier claim that the dev deployment manifest omits inventory is no longer true: the [reviewed manifest](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/deployments/dev/world.json) names core, character, currency, inventory, and metadata. The [live manifest](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/deployments/live/world.json) names MVR app capabilities but does not list published packages. No manifest establishes which code is active in-game.

Active [Entity deletion](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/core/sources/entity.move) explicitly notes that leftover component dynamic fields can be orphaned. [Location verification](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/core/sources/services/location_service.move) still compares caller and target hashes, with signed proofs left as a TODO. These are source-observed limitations, not runtime findings.

No Sui, Docker, or deployed-environment execution was performed for this documentation review. Consequently source review does not verify runtime compatibility, publish status, live game activation, server configuration, or production security properties. Re-run the maintenance workflow after either branch advances or is rewritten; it pins candidates, accounts for changed files, and preserves this cursor until validation succeeds.
