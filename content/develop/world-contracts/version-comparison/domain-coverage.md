+++
title = "Domain coverage"
weight = 20
+++

The table classifies source at the reviewed commits. **Archived legacy** is not active v1 functionality; generic Entity primitives do not prove that a gameplay domain has been ported.

| v0 domain or v1 module | v1 state | Evidence and consequence |
| --- | --- | --- |
| Entity, Action, Request, Requirement | Active v1 implementation | [`core`](https://github.com/evefrontier/world-contracts/tree/485740eae181638f494bd574e18a10ba0c991303/contracts/core/sources) supplies the modular foundation. |
| Character identity | Redesigned equivalent | [`Identity`](https://github.com/evefrontier/world-contracts/blob/485740eae181638f494bd574e18a10ba0c991303/contracts/character/sources/identity.move) is an installed module, not v0's Character layout. |
| Item and storage inventory | Active v1 implementation | Active [`inventory`](https://github.com/evefrontier/world-contracts/tree/485740eae181638f494bd574e18a10ba0c991303/contracts/inventory/sources) is request-routed. |
| Assemblies: gate, turret, storage unit | Archived legacy only | v0 modules remain under [`contracts/archive/world`](https://github.com/evefrontier/world-contracts/tree/485740eae181638f494bd574e18a10ba0c991303/contracts/archive/world/sources/assemblies). |
| Network nodes, killmails, rifts | No active v1 equivalent / not yet ported | Present on v0/main, absent from the active v1 package set. |
| Fuel, energy, status, metadata | Archived legacy only | v0 primitives are retained in archive, not active modules. |
| Access, location, registry | Partially represented | Active core has services and registry concepts, with materially different interfaces and checks. |
| Extension examples | Archived legacy only | Examples were moved below [`archive`](https://github.com/evefrontier/world-contracts/tree/485740eae181638f494bd574e18a10ba0c991303/contracts/archive/extension_examples). |
| v1 deployment | Deployment unknown or separately evidenced | [`dev/world.json`](https://github.com/evefrontier/world-contracts/blob/485740eae181638f494bd574e18a10ba0c991303/deployments/dev/world.json) names some artifacts, not every active package or a production environment. |

The coverage rows are intentionally conservative: a domain can be partially represented by generic platform features without possessing its v0 lifecycle, type, API, or authorization checks.
