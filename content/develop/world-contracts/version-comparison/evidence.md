+++
title = "Evidence, contradictions, and limits"
weight = 70
+++

Evidence has an order of authority: pinned Move source and tests establish implemented behavior; manifests and deployment artifacts establish only their explicit environment facts; upstream prose is contextual and can be stale. All factual upstream references in this chapter are immutable commit URLs from the [canonical cursor](../).

The reviewed dev tree retains v0 source below [`contracts/archive`](https://github.com/evefrontier/world-contracts/tree/485740eae181638f494bd574e18a10ba0c991303/contracts/archive), while active packages are elsewhere. The decoder README's `contracts/world` wording conflicts with that active layout. The dev deployment manifest lists core and character but not inventory. These are recorded contradictions/limits, not gaps to fill with inference.

No Sui, Docker, or deployed-environment execution was performed for this documentation review. Consequently source review does not verify runtime compatibility, publish status, live game activation, server configuration, or production security properties. Re-run the maintenance workflow after either branch advances or is rewritten; it pins candidates, accounts for changed files, and preserves this cursor until validation succeeds.
