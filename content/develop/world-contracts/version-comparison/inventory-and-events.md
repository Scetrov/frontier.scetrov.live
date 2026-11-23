+++
title = "Inventory, bridges, and events"
weight = 40
+++

v0 [`inventory`](https://github.com/evefrontier/world-contracts/blob/6fd08169ba4c0e880e91548cd0314cbb91bc92ed/contracts/world/sources/primitives/inventory.move) dynamically attaches inventory to an assembly and moves transit items with parent, tenant, and location metadata. Its bridge flow relies on game-server/location-proof handling and emits domain events carrying assembly and character identity.

v1's active [`Inventory`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/inventory/sources/inventory.move) is one balance area per installed Entity component, keyed by numeric component ID. The former `StorageInventory` main/ephemeral-per-caller routing is gone. Item type and quantity requirements constrain deposit, withdrawal, and bridge operations; bridge-in and bridge-out handlers additionally push an admin sponsor requirement. The source says the owner can sign and the gas sponsor must be on `AdminACL`; this is not a v0-equivalent signed location-proof bridge. Bridges, deposits, and withdrawals also enqueue an online power-grant requirement.

The reviewed v1 [`Item`](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/inventory/sources/item.move) holds an ID, type, quantity, volume, and source Entity ID, but not the v0 transit item's parent, location, or tenant fields. It has `key` but not `store`, preventing arbitrary `public_transfer` outside the inventory flow. Capacity-accounted movement remains, but object layout, routing, and event/indexer fields differ. `InventoryInstalled` and `InventoryUninstalled` bracket a component's lifetime; uninstall also burns remaining balances. Rebuild indexers against active v1 events rather than assuming v0 payloads survive.

Single and batch deposits accept items from the same Entity or one recorded as docked with it (see [Entity](https://github.com/evefrontier/world-contracts/blob/acb0a16cd4b754bd9c41c058007932f131a7f258/contracts/core/sources/entity.move)). Batch moves apply the requirement's quantity bounds to the total and emit `ItemsDeposited` or `ItemsWithdrawn`; teardown emits batched `ItemsDestroyed` for remaining balances. Movement events identify the inventory's Entity and component rather than relying on the item ID alone.
