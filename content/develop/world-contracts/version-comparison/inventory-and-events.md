+++
title = "Inventory, bridges, and events"
weight = 40
+++

v0 [`inventory`](https://github.com/evefrontier/world-contracts/blob/d33ff232bd3878e8f9ad0721e18564b21facc925/contracts/world/sources/primitives/inventory.move) dynamically attaches inventory to an assembly and moves transit items with parent, tenant, and location metadata. Its bridge flow relies on game-server/location-proof handling and emits domain events carrying assembly and character identity.

v1's active [`Inventory`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/inventory/sources/inventory.move) is one balance area per installed Entity component, keyed by numeric component ID. The former `StorageInventory` main/ephemeral-per-caller routing is gone. Item type and quantity requirements constrain deposit, withdrawal, and bridge operations; bridge-in and bridge-out handlers additionally push an admin sponsor requirement. The source says the owner can sign and the gas sponsor must be on `AdminACL`; this is not a v0-equivalent signed location-proof bridge.

The reviewed v1 [`Item`](https://github.com/evefrontier/world-contracts/blob/8bf651194898b693211614632561a3926c6de99c/contracts/inventory/sources/item.move) holds an ID, type, quantity, and volume but not the v0 transit item's parent, location, tenant, or provenance fields. It has `key` but not `store`, preventing arbitrary `public_transfer` outside the inventory flow. Capacity-accounted movement remains, but object layout, routing, and event/indexer fields differ. `InventoryInstalled` and `InventoryUninstalled` bracket a component's lifetime; uninstall also burns remaining balances. Rebuild indexers against active v1 events rather than assuming v0 payloads survive.
