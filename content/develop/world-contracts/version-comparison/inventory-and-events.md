+++
title = "Inventory, bridges, and events"
weight = 40
+++

v0 [`inventory`](https://github.com/evefrontier/world-contracts/blob/843f706efe74b0c5b818d4282587f4a58893107c/contracts/world/sources/primitives/inventory.move) dynamically attaches inventory to an assembly and moves transit items with parent, tenant, and location metadata. Its bridge flow relies on game-server/location-proof handling and emits domain events carrying assembly and character identity.

v1's active [`StorageInventory`](https://github.com/evefrontier/world-contracts/blob/485740eae181638f494bd574e18a10ba0c991303/contracts/inventory/sources/inventory.move) is an Entity module with a main inventory and lazy ephemeral inventories keyed by the request-authorized entity. Item type and quantity requirements constrain operations. Tenant-scoped identity is derived from the enclosing `EntityKey` and emitted event keys, rather than retained as item-carried provenance. Builders must configure the enclosing action and consume the module-scoped requirements.

The reviewed v1 `Item` holds an ID, type, quantity, and volume; it does not retain the v0 transit item's parent, location, tenant, or provenance fields. Capacity-accounted item movement remains, but object layout, public calls, authorization routing, and event/indexer fields change. Rebuild indexers against active v1 events rather than assuming v0 names or payloads survive. The active module alone does not establish a v0-equivalent signed server bridge: treat bridge authorization as dependent on configured actions and deployment evidence.
