+++
title = "Domain coverage"
weight = 20
+++

The table classifies source at the reviewed commits. **Archived legacy** is not active v1 functionality; generic Entity primitives do not prove that a gameplay domain has been ported.

| v0 domain or v1 module | v1 state | Evidence and consequence |
| --- | --- | --- |
| Entity, Component, Action, Request, Requirement | Active v1 implementation | [`core`](https://github.com/evefrontier/world-contracts/tree/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/core/sources) supplies the modular foundation, now keyed by numeric component IDs rather than names. |
| Opaque fittings | Active generic storage, not gameplay logic | [`GenericModule`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/generic_module/sources/generic_module.move) stores type IDs and bytes without implementing a fitting's behavior. |
| Character identity | Redesigned equivalent | [`Identity`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/character/sources/identity.move) is an installed component emitting `CharacterCreated`, not v0's Character layout. |
| Item and storage inventory | Active v1 implementation | Active [`inventory`](https://github.com/evefrontier/world-contracts/tree/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/inventory/sources) uses one inventory per component; ephemeral per-caller inventories were removed. |
| Display metadata | Redesigned equivalent | Active [`metadata`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/metadata/sources/metadata.move) installs a component and routes edits through a typed requirement; it is not v0's metadata layout. |
| EVE currency | Active separate package | [`currency::EVE`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/currency/sources/EVE.move) defines a capped-supply coin and admin treasury, separate from archived v0 assets. |
| Assemblies: gate, turret, storage unit | Archived legacy only | v0 modules remain under [`contracts/archive/world`](https://github.com/evefrontier/world-contracts/tree/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/archive/world/sources/assemblies). |
| Network nodes and rifts | No direct active v1 equivalent | Modular power is active, but it does not port the v0 network-node or rift API. |
| Killmails | Redesigned equivalent | [Killmail](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/killmail/sources/record.move) records game-reported losses on their own Entities through an admin-gated request. |
| Creation sections and Shell | Active v1 implementation | [Layout](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/creation/sources/layout.move) indexes installed module IDs by section and tracks the Shell. |
| Fuel, energy, status | Partially represented | [PowerGrid](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/power/sources/power_grid.move) implements fuel-dependent generation and load grants, not the v0 primitives or their interfaces. |
| Access, location, registry | Partially represented | Active core has services and registry concepts, with materially different interfaces and checks. |
| Extension examples | Archived legacy only | Examples were moved below [`archive`](https://github.com/evefrontier/world-contracts/tree/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/archive/extension_examples). |
| v1 deployment | Separately evidenced / runtime unverified | [`dev/world.json`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/deployments/dev/world.json) lists nine packages; live/test/UAT manifests hold different environment-specific facts. None independently verifies on-chain state. |

A domain can be partially represented by generic platform features without possessing its v0 lifecycle, type, API, or authorization checks.
