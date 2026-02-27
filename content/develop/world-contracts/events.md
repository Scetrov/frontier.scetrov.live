+++
date = '2026-02-27T12:00:00Z'
title = 'Events Index'
weight = 1
codebase = "https://github.com/evefrontier/world-contracts/tree/main/contracts/world/sources"
+++

This page provides a complete index of every event emitted by the [world-contracts](https://github.com/evefrontier/world-contracts). Events are the primary mechanism for off-chain indexers, game clients, and third-party tools to observe state changes on-chain. All event structs carry the `has copy, drop` abilities, and are emitted via Sui's `event::emit`.

## Access Control

**Source:** [`access/access_control.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/access/access_control.move)

Full documentation: [access_control.move](../access/access_control.move/)

### `OwnerCapCreatedEvent`

Emitted when a new `OwnerCap` is created for an object.

| Field | Type | Description |
|---|---|---|
| `owner_cap_id` | `ID` | The ID of the newly created `OwnerCap`. |
| `authorized_object_id` | `ID` | The ID of the object this capability authorizes. |

### `OwnerCapTransferred`

Emitted when an `OwnerCap` is transferred to a new owner.

| Field | Type | Description |
|---|---|---|
| `owner_cap_id` | `ID` | The ID of the transferred `OwnerCap`. |
| `authorized_object_id` | `ID` | The ID of the object this capability authorizes. |
| `previous_owner` | `address` | The address of the prior owner. |
| `owner` | `address` | The address of the new owner. |

---

## Assemblies

### Assembly

**Source:** [`assemblies/assembly.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/assemblies/assembly.move)

Full documentation: [assembly.move](../assemblies/assembly.move/)

#### `AssemblyCreatedEvent`

Emitted when a new generic assembly is created.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The deterministic game-derived key for the assembly. |
| `owner_cap_id` | `ID` | The ID of the `OwnerCap` created for the assembly owner. |
| `type_id` | `u64` | The assembly type identifier (e.g. Gate, Storage Unit). |

### Gate

**Source:** [`assemblies/gate.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/assemblies/gate.move)

Full documentation: [gate.move](../assemblies/gate.move/)

#### `GateCreatedEvent`

Emitted when a new gate (stargate) is anchored in the world.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the gate. |
| `assembly_key` | `TenantItemId` | The deterministic game-derived key for the gate. |
| `owner_cap_id` | `ID` | The ID of the `OwnerCap` created for the gate owner. |
| `type_id` | `u64` | The assembly type identifier. |
| `location_hash` | `vector<u8>` | A hash representing the gate's spatial location. |
| `status` | `Status` | The initial status of the gate (`ONLINE`, `OFFLINE`, etc.). |

#### `GateLinkedEvent`

Emitted when two gates are linked together, forming a bidirectional jump route.

| Field | Type | Description |
|---|---|---|
| `source_gate_id` | `ID` | The on-chain object ID of the source gate. |
| `source_gate_key` | `TenantItemId` | The game-derived key of the source gate. |
| `destination_gate_id` | `ID` | The on-chain object ID of the destination gate. |
| `destination_gate_key` | `TenantItemId` | The game-derived key of the destination gate. |

#### `GateUnlinkedEvent`

Emitted when a link between two gates is severed.

| Field | Type | Description |
|---|---|---|
| `source_gate_id` | `ID` | The on-chain object ID of the source gate. |
| `source_gate_key` | `TenantItemId` | The game-derived key of the source gate. |
| `destination_gate_id` | `ID` | The on-chain object ID of the destination gate. |
| `destination_gate_key` | `TenantItemId` | The game-derived key of the destination gate. |

#### `JumpEvent`

Emitted when a character successfully jumps through a linked gate.

| Field | Type | Description |
|---|---|---|
| `source_gate_id` | `ID` | The on-chain object ID of the source gate. |
| `source_gate_key` | `TenantItemId` | The game-derived key of the source gate. |
| `destination_gate_id` | `ID` | The on-chain object ID of the destination gate. |
| `destination_gate_key` | `TenantItemId` | The game-derived key of the destination gate. |
| `character_id` | `ID` | The on-chain object ID of the jumping character. |
| `character_key` | `TenantItemId` | The game-derived key of the jumping character. |

### Storage Unit

**Source:** [`assemblies/storage_unit.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/assemblies/storage_unit.move)

Full documentation: [storage_unit.move](../assemblies/storage_unit.move/)

#### `StorageUnitCreatedEvent`

Emitted when a new Storage Unit is anchored.

| Field | Type | Description |
|---|---|---|
| `storage_unit_id` | `ID` | The on-chain object ID of the storage unit. |
| `assembly_key` | `TenantItemId` | The deterministic game-derived key. |
| `owner_cap_id` | `ID` | The ID of the `OwnerCap` created for the owner. |
| `type_id` | `u64` | The assembly type identifier. |
| `max_capacity` | `u64` | The maximum inventory volume capacity. |
| `location_hash` | `vector<u8>` | A hash representing the spatial location. |
| `status` | `Status` | The initial status of the storage unit. |

---

## Entities

### Character

**Source:** [`character/character.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/character/character.move)

Full documentation: [character.move](../entities/character/character.move/)

#### `CharacterCreatedEvent`

Emitted when a new player character is created.

| Field | Type | Description |
|---|---|---|
| `character_id` | `ID` | The on-chain object ID of the character. |
| `key` | `TenantItemId` | The deterministic game-derived key. |
| `tribe_id` | `u32` | The tribe the character belongs to. |
| `character_address` | `address` | The Sui address associated with the character. |

### Killmail

**Source:** [`killmail/killmail.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/killmail/killmail.move)

Full documentation: [killmail.move](../entities/killmail/killmail.move/)

#### `KillmailCreatedEvent`

Emitted when a new combat loss record is created.

| Field | Type | Description |
|---|---|---|
| `killmail_id` | `TenantItemId` | The unique identifier for this killmail. |
| `killer_character_id` | `TenantItemId` | The game-derived key of the character who scored the kill. |
| `victim_character_id` | `TenantItemId` | The game-derived key of the character who was destroyed. |
| `solar_system_id` | `TenantItemId` | The game-derived key of the solar system where the kill occurred. |
| `loss_type` | `LossType` | The type of loss — `SHIP` or `STRUCTURE`. |
| `kill_timestamp` | `u64` | Unix timestamp (in seconds) of the kill. |

### Network Node

**Source:** [`network_node/network_node.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/network_node/network_node.move)

Full documentation: [network_node.move](../assemblies/network-node/network_node.move/)

#### `NetworkNodeCreatedEvent`

Emitted when a new Network Node is created.

| Field | Type | Description |
|---|---|---|
| `network_node_id` | `ID` | The on-chain object ID of the network node. |
| `assembly_key` | `TenantItemId` | The deterministic game-derived key. |
| `owner_cap_id` | `ID` | The ID of the `OwnerCap` created for the owner. |
| `type_id` | `u64` | The assembly type identifier. |
| `fuel_max_capacity` | `u64` | The maximum fuel the node can hold. |
| `fuel_burn_rate_in_ms` | `u64` | The rate at which fuel is consumed, in milliseconds per unit. |
| `max_energy_production` | `u64` | The maximum energy this node can produce. |

---

## Primitives

### Energy

**Source:** [`primitives/energy.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/primitives/energy.move)

Full documentation: [energy.move](../primitives/energy.move/)

#### `StartEnergyProductionEvent`

Emitted when an energy source begins producing energy.

| Field | Type | Description |
|---|---|---|
| `energy_source_id` | `ID` | The on-chain object ID of the energy source. |
| `current_energy_production` | `u64` | The energy production rate at the time of starting. |

#### `StopEnergyProductionEvent`

Emitted when an energy source stops producing energy.

| Field | Type | Description |
|---|---|---|
| `energy_source_id` | `ID` | The on-chain object ID of the energy source. |

#### `EnergyReservedEvent`

Emitted when an assembly reserves energy from a source.

| Field | Type | Description |
|---|---|---|
| `energy_source_id` | `ID` | The on-chain object ID of the energy source. |
| `assembly_type_id` | `u64` | The type of assembly reserving energy. |
| `energy_reserved` | `u64` | The amount of energy reserved in this operation. |
| `total_reserved_energy` | `u64` | The total reserved energy on this source after the reservation. |

#### `EnergyReleasedEvent`

Emitted when reserved energy is released back to a source.

| Field | Type | Description |
|---|---|---|
| `energy_source_id` | `ID` | The on-chain object ID of the energy source. |
| `assembly_type_id` | `u64` | The type of assembly releasing energy. |
| `energy_released` | `u64` | The amount of energy released. |
| `total_reserved_energy` | `u64` | The total reserved energy on this source after the release. |

### Fuel

**Source:** [`primitives/fuel.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/primitives/fuel.move)

Full documentation: [fuel.move](../primitives/fuel.move/)

#### `FuelEvent`

A generic event emitted for all fuel state changes. The `action` field indicates the specific operation.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `type_id` | `u64` | The fuel type identifier. |
| `old_quantity` | `u64` | The fuel quantity before the operation. |
| `new_quantity` | `u64` | The fuel quantity after the operation. |
| `is_burning` | `bool` | Whether the fuel is currently being burned. |
| `action` | `Action` | The action that triggered this event. |

**`Action` enum values:**

| Variant | Description |
|---|---|
| `DEPOSITED` | Fuel was deposited into the assembly. |
| `WITHDRAWN` | Fuel was withdrawn from the assembly. |
| `BURNING_STARTED` | Fuel burning was started. |
| `BURNING_STOPPED` | Fuel burning was stopped. |
| `BURNING_UPDATED` | Fuel quantities were recalculated during a burn cycle. |
| `DELETED` | The fuel storage was deleted. |

#### `FuelEfficiencySetEvent`

Emitted when a fuel type's efficiency multiplier is configured.

| Field | Type | Description |
|---|---|---|
| `fuel_type_id` | `u64` | The fuel type identifier. |
| `efficiency` | `u64` | The efficiency multiplier value. |

#### `FuelEfficiencyRemovedEvent`

Emitted when a fuel type's efficiency configuration is removed.

| Field | Type | Description |
|---|---|---|
| `fuel_type_id` | `u64` | The fuel type identifier. |

### Inventory

**Source:** [`primitives/inventory.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/primitives/inventory.move)

Full documentation: [inventory.move](../primitives/inventory.move/)

#### `ItemMintedEvent`

Emitted when items are minted (bridged from game to chain) into an assembly's inventory.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `character_id` | `ID` | The on-chain object ID of the character performing the action. |
| `character_key` | `TenantItemId` | The game-derived key of the character. |
| `item_id` | `u64` | The unique identifier of the item. |
| `type_id` | `u64` | The item type identifier. |
| `quantity` | `u32` | The number of items minted. |

#### `ItemBurnedEvent`

Emitted when items are burned (bridged from chain back to game).

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `character_id` | `ID` | The on-chain object ID of the character. |
| `character_key` | `TenantItemId` | The game-derived key of the character. |
| `item_id` | `u64` | The unique identifier of the item. |
| `type_id` | `u64` | The item type identifier. |
| `quantity` | `u32` | The number of items burned. |

#### `ItemDepositedEvent`

Emitted when items are deposited into an assembly's inventory.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `character_id` | `ID` | The on-chain object ID of the character. |
| `character_key` | `TenantItemId` | The game-derived key of the character. |
| `item_id` | `u64` | The unique identifier of the item. |
| `type_id` | `u64` | The item type identifier. |
| `quantity` | `u32` | The number of items deposited. |

#### `ItemWithdrawnEvent`

Emitted when items are withdrawn from an assembly's inventory.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `character_id` | `ID` | The on-chain object ID of the character. |
| `character_key` | `TenantItemId` | The game-derived key of the character. |
| `item_id` | `u64` | The unique identifier of the item. |
| `type_id` | `u64` | The item type identifier. |
| `quantity` | `u32` | The number of items withdrawn. |

#### `ItemDestroyedEvent`

Emitted when items are destroyed during inventory cleanup (e.g. when an inventory is deleted).

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `item_id` | `u64` | The unique identifier of the item. |
| `type_id` | `u64` | The item type identifier. |
| `quantity` | `u32` | The number of items destroyed. |

### Metadata

**Source:** [`primitives/metadata.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/primitives/metadata.move)

Full documentation: [metadata.move](../primitives/metadata.move/)

#### `MetadataChangedEvent`

Emitted when an assembly's metadata (name, description, URL) is updated.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `name` | `String` | The new name. |
| `description` | `String` | The new description. |
| `url` | `String` | The new URL. |

### Status

**Source:** [`primitives/status.move`](https://github.com/evefrontier/world-contracts/blob/main/contracts/world/sources/primitives/status.move)

Full documentation: [status.move](../primitives/status.move/)

#### `StatusChangedEvent`

Emitted when an assembly's operational status changes.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | `ID` | The on-chain object ID of the assembly. |
| `assembly_key` | `TenantItemId` | The game-derived key of the assembly. |
| `status` | `Status` | The new operational status. |
| `action` | `Action` | The action that caused the change. |

**`Status` enum values:**

| Variant | Description |
|---|---|
| `NULL` | No status set (initial state). |
| `OFFLINE` | The assembly is offline. |
| `ONLINE` | The assembly is online. |

**`Action` enum values:**

| Variant | Description |
|---|---|
| `ANCHORED` | The assembly was anchored in space. |
| `ONLINE` | The assembly was brought online. |
| `OFFLINE` | The assembly was taken offline. |
| `UNANCHORED` | The assembly was unanchored. |

---

## Quick Reference

A summary table of all **27 events** across the world-contracts:

| Module | Event | Key Trigger |
|---|---|---|
| `access_control` | `OwnerCapCreatedEvent` | An `OwnerCap` is created |
| `access_control` | `OwnerCapTransferred` | An `OwnerCap` changes owner |
| `assembly` | `AssemblyCreatedEvent` | A generic assembly is created |
| `gate` | `GateCreatedEvent` | A gate is anchored |
| `gate` | `GateLinkedEvent` | Two gates are linked |
| `gate` | `GateUnlinkedEvent` | Two gates are unlinked |
| `gate` | `JumpEvent` | A character jumps through a gate |
| `storage_unit` | `StorageUnitCreatedEvent` | A storage unit is anchored |
| `character` | `CharacterCreatedEvent` | A player character is created |
| `killmail` | `KillmailCreatedEvent` | A combat loss is recorded |
| `network_node` | `NetworkNodeCreatedEvent` | A network node is created |
| `energy` | `StartEnergyProductionEvent` | Energy production starts |
| `energy` | `StopEnergyProductionEvent` | Energy production stops |
| `energy` | `EnergyReservedEvent` | Energy is reserved by an assembly |
| `energy` | `EnergyReleasedEvent` | Reserved energy is released |
| `fuel` | `FuelEvent` | Any fuel state change (deposit, withdraw, burn, etc.) |
| `fuel` | `FuelEfficiencySetEvent` | A fuel efficiency multiplier is configured |
| `fuel` | `FuelEfficiencyRemovedEvent` | A fuel efficiency config is removed |
| `inventory` | `ItemMintedEvent` | Items are minted (game → chain) |
| `inventory` | `ItemBurnedEvent` | Items are burned (chain → game) |
| `inventory` | `ItemDepositedEvent` | Items are deposited into inventory |
| `inventory` | `ItemWithdrawnEvent` | Items are withdrawn from inventory |
| `inventory` | `ItemDestroyedEvent` | Items are destroyed during cleanup |
| `metadata` | `MetadataChangedEvent` | Assembly metadata is updated |
| `status` | `StatusChangedEvent` | Assembly status changes |

> **Note:** Extension example contracts (e.g. `tribe_permit`, `corpse_gate_bounty`, and extension `turret` / `gate`) do not emit their own events in the current codebase. The turret assembly documented in [turret.move](../assemblies/turret.move/) is not yet present in the open-source [world-contracts](https://github.com/evefrontier/world-contracts) repository.
