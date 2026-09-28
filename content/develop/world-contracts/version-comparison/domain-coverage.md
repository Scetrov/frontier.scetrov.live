+++
title = "Domain coverage"
weight = 20
+++

The table classifies source at the reviewed commits. **Archived legacy** is not active v1 functionality; generic Entity primitives do not prove that a gameplay domain has been ported.

| v0 domain or v1 module | v1 state | Evidence and consequence |
| --- | --- | --- |
| Entity, Component, Action, Request, Requirement | Active v1 implementation | [`core`](https://github.com/evefrontier/world-contracts/tree/8bf651194898b693211614632561a3926c6de99c/contracts/core/sources) supplies the modular foundation, now keyed by numeric component IDs rather than names. |
| Opaque fittings | Active generic storage, not gameplay logic | [`GenericModule`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/core/sources/generic_module.move) stores type IDs and bytes without implementing a fitting's behavior. |
| Character identity | Redesigned equivalent | [`Identity`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/character/sources/identity.move) is an installed component emitting `CharacterCreated`, not v0's Character layout. |
| Item and storage inventory | Active v1 implementation | Active [`inventory`](https://github.com/evefrontier/world-contracts/tree/8bf651194898b693211614632561a3926c6de99c/contracts/inventory/sources) uses one inventory per component; ephemeral per-caller inventories were removed. |
| Display metadata | Redesigned equivalent | Active [`metadata`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/metadata/sources/metadata.move) installs a component and routes edits through a typed requirement; it is not v0's metadata layout. |
| EVE currency | Active separate package | [`currency::EVE`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/currency/sources/EVE.move) defines a capped-supply coin and admin treasury, separate from archived v0 assets. |
| Assemblies: gate, turret, storage unit | Archived legacy only | v0 modules remain under [`contracts/archive/world`](https://github.com/evefrontier/world-contracts/tree/8bf651194898b693211614632561a3926c6de99c/contracts/archive/world/sources/assemblies). |
| Network nodes, killmails, rifts | No active v1 equivalent / not yet ported | Present on v0/main; v0 Rift mining announcements do not establish an active dev port. |
| Fuel, energy, status | Archived legacy only | v0 primitives are retained in archive, not active modules. |
| Access, location, registry | Partially represented | Active core has services and registry concepts, with materially different interfaces and checks. |
| Extension examples | Archived legacy only | Examples were moved below [`archive`](https://github.com/evefrontier/world-contracts/tree/8bf651194898b693211614632561a3926c6de99c/contracts/archive/extension_examples). |
| v1 deployment | Separately evidenced / runtime unverified | [`dev/world.json`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/deployments/dev/world.json) names five packages; live/test/UAT manifests hold different environment-specific facts. None independently verifies on-chain state. |

A domain can be partially represented by generic platform features without possessing its v0 lifecycle, type, API, or authorization checks.
