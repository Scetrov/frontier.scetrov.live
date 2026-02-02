+++
date = '2026-02-02T15:38:00Z'
title = 'gate.move'
weight = 3
codebase = 'https://github.com/evefrontier/world-contracts/blob/main/contracts/builder_extensions/sources/gate.move'
+++

## Overview

The promise of a truly decentralized metaverse lies in "digital physics"—a set of immutable, composable rules that enable emergent gameplay and player-driven innovation. In the EVE Frontier world contracts, the **Smart Gate** system is a primary example of this philosophy. Far more than a simple teleportation point, the Gate is a programmable structure that balances core game integrity with unprecedented player agency.

This guide provides a comprehensive technical breakdown of Gate architecture, logic, and extensibility for developers building on the Frontier platform.

## Learning Objectives

By the end of this article, you will be able to:

1. **Explain** the three-layer architecture of the Frontier world contracts.
2. **Describe** the lifecycle of a Gate, from anchoring to linking.
3. **Analyze** the "Typed Witness Pattern" used for securing extensions.
4. **Implement** interactions with Gates using the developer toolkit and TypeScript SDK.

---

## 1. Architecture and Role

The Frontier world contracts utilize a three-layer model to prioritize **composition over inheritance**.

- **Layer 1: Composable Primitives**: Focused modules handling "physics" logic like spatial positioning ([`location.move`](../../primitives/location.move/)), resource consumption ([`fuel.move`](../../primitives/fuel.move/)), and state management ([`status.move`](../../primitives/status.move/)).
- **Layer 2: Game-Defined Assemblies**: Structures like the [`Gate`](./) that compose these primitives into functional units.
- **Layer 3: Player Extensions**: Custom smart contracts that register with assemblies to modify their behavior.

---

## 2. Operational Lifecycle and Physics

A Gate's lifecycle begins with **Anchoring**, where it is initialized in the `ObjectRegistry` and linked to a [`NetworkNode`](../../primitives/network_node.move/) for power.

### The Gate Lifecycle

```mermaid
sequenceDiagram
    participant Admin
    participant Registry as ObjectRegistry
    participant NWN as NetworkNode
    participant Gate
    participant Char as Character

    Admin->>Registry: anchor()
    Admin->>NWN: connect_assembly(gate_id)
    Admin->>Gate: Create Gate Object
    Admin->>Char: Transfer OwnerCap
    Note over Gate: Status: Anchored/Offline
    Char->>Gate: online(owner_cap, nwn)
    Gate->>NWN: reserve_energy()
    Note over Gate: Status: Online

```

### Core Physics: Linking and Energy

Gates function by linking to another gate to create a transport link. This process is governed by strict "digital physics":

- **Ownership**: Both gates must be owned by the same character.
- **Distance**: Gates must be at least 20KM apart.
- **Location Proofs**: Linking requires a `distance_proof` (a signature from a trusted server) to verify the gates are within the maximum distance allowed for that gate type.
- **Energy Integration**: A gate cannot go online unless its connected [`NetworkNode`](../../primitives/network_node.move/) has reserved energy for it. If a network node is updated or unanchored, the system uses a **"Hot Potato" pattern** (e.g., `UpdateEnergySources`) to ensure all connected gates are updated atomically in the same transaction block.

---

## 3. The Moddability Pattern: Type-Based Authorization

The true power of Frontier lies in **Moddability**. Owners can define custom jump rules through extension contracts using the **Typed Witness Pattern**.

### Authorization Flow

1. **Extension Development**: A developer deploys a contract defining a witness type (e.g., `XAuth`).
2. **Registration**: The gate owner calls `authorize_extension<XAuth>`, adding the `TypeName` to the gate's `extension` field.
3. **Enforcement**: Once an extension is configured, the standard `jump` function will **abort**. Travelers (via the game client) must use `jump_with_permit`.

```mermaid
graph TD
    A[User wants to Jump] --> B{Extension Configured?}
    B -- No --> C[Call jump]
    C --> D[Check Online & Linked]
    D --> E((Success))

    B -- Yes --> F[Call jump_with_permit]
    F --> G[Check Online & Linked]
    G --> H[Validate JumpPermit]
    H --> I[Check Auth Witness Type]
    I --> J[Check Expiry & Route Hash]
    J --> K[Delete Permit]
    K --> E

```

---

## 4. Logic Deep Dive: Jumps and Permits

There are two primary ways to traverse a gate:

### A. Default Jump

Allowed only when no extension logic is configured. It validates that both gates are online and linked before emitting a `JumpEvent`.

### B. Jump with Permit

Required when an extension is authorized. The extension logic (Layer 3) issues a `JumpPermit` object to the player.

- **Route Hashing**: Permits are bound to a specific source/destination pair via a `route_hash`.
- **Direction Agnostic**: The hash is computed from concatenated IDs (A+B) using `blake2b256`, ensuring one permit works for both A→B and B→A.
- **Single-Use**: The `JumpPermit` object is deleted upon a successful jump to prevent replay attacks.

---

## 5. Developer's Toolkit: Bulk Queries and Discovery

External tools (like route planners) can interact with this system by querying Sui's shared objects and indexed events.

### Building a Route Graph

To map the traversable network, a developer should query for `Gate` objects and filter by:

- `status.is_online()`: Only active gates can be used.
- `linked_gate_id`: This defines the edge in the graph.
- `extension`: If a `TypeName` is present, the edge has restricted access.

### Identifying Traversable Paths for Players

A planner determines if a restricted gate is "open" for a specific player by querying the player's address for `JumpPermit` objects:

1. **Query Objects**: Call `suix_getOwnedObjects` for type `world::gate::JumpPermit`.
2. **Validate Metadata**:
   - **Character ID**: `permit.character_id` must match the player’s `Character` ID.
   - **Route Hash**: Match against the hash of the intended source and destination.
   - **Expiry**: `permit.validity_period` must be greater than current `clock` time.

---

## 6. Security and Obfuscation

To support "fog of war" mechanics, Frontier stores locations as cryptographic hashes. This allows for the verification of proximity without revealing exact coordinates on-chain. developers must use the `verify_distance` function within the [`world::location`](../../primitives/location.move/) primitive to prove that two entities are legally interacting based on their private coordinates.

---

## 7. Developer's Implementation Guide: TypeScript/JavaScript

Interacting with Gates requires a mix of standard Sui SDK patterns and Frontier-specific utilities for managing game state and character identity.

### 1. Environment Initialization

Before interacting with the world, developers must initialize a context that includes the `SuiClient`, the user's `Keypair`, and the Frontier network configuration.

```typescript
import { initializeContext, getEnvConfig } from "../utils/helper";

const env = getEnvConfig(); // Loads PRIVATE_KEY and SUI_NETWORK from .env
const { client, keypair, config, address } = initializeContext(
  env.network,
  env.playerExportedKey,
); // Sets up the client and identifies the package IDs
```

### 2. Addressing Objects: Deterministic Derivation

EVE Frontier uses a deterministic registry system to manage object IDs. Instead of hardcoding hex strings, developers should derive object IDs using the `ObjectRegistry` ID and the in-game `ITEM_ID`.

```typescript
import { deriveObjectId } from "../utils/derive-object-id";
import { NWN_ITEM_ID, ASSEMBLY_ITEM_ID } from "../utils/constants";

// Derive the on-chain Object ID for a specific structure
const networkNodeId = deriveObjectId(
  config.objectRegistry,
  NWN_ITEM_ID,
  config.packageId,
);

const gateId = deriveObjectId(
  config.objectRegistry,
  ASSEMBLY_ITEM_ID,
  config.packageId,
);
```

### 3. Pattern: Borrow, Use, Return (OwnerCaps)

Most Gate operations (linking, going online) require an `OwnerCap`. In Frontier, these are typically stored within the player's `Character` object. Developers must use a "Borrow/Return" pattern within a single transaction block to authenticate.

```typescript
import { Transaction } from "@mysten/sui/transactions";
import { MODULES } from "../utils/config";

const tx = new Transaction();

// 1. Borrow the OwnerCap from the Character object
const [ownerCap] = tx.moveCall({
  target: `${config.packageId}::${MODULES.CHARACTER}::borrow_owner_cap`,
  typeArguments: [`${config.packageId}::${MODULES.GATE}::Gate`],
  arguments: [tx.object(characterId), tx.object(gateOwnerCapId)],
});

// 2. Use the OwnerCap for the Gate operation
tx.moveCall({
  target: `${config.packageId}::${MODULES.GATE}::online`,
  arguments: [
    tx.object(gateId),
    tx.object(networkNodeId),
    tx.object(config.energyConfig),
    ownerCap,
  ],
});

// 3. Return the OwnerCap back to the Character object
tx.moveCall({
  target: `${config.packageId}::${MODULES.CHARACTER}::return_owner_cap`,
  typeArguments: [`${config.packageId}::${MODULES.GATE}::Gate`],
  arguments: [tx.object(characterId), ownerCap],
});
```

### 4. Executing a Jump Transaction

When a user performs a jump, the client must construct the transaction based on whether an extension is active.

#### Standard Jump (Public)

```typescript
tx.moveCall({
  target: `${config.packageId}::${MODULES.GATE}::jump`,
  arguments: [
    tx.object(sourceGateId),
    tx.object(destinationGateId),
    tx.object(characterId),
  ],
});
```

#### Jump with Permit (Restricted)

For restricted gates, the developer must first fetch the `JumpPermit` object from the user's inventory and pass it as an argument.

```typescript
// Fetch permit from user inventory via RPC
const permitObject = await client.getOwnedObjects({
  owner: playerAddress,
  filter: { StructType: `${config.packageId}::gate::JumpPermit` },
});

tx.moveCall({
  target: `${config.packageId}::${MODULES.GATE}::jump_with_permit`,
  arguments: [
    tx.object(sourceGateId),
    tx.object(destinationGateId),
    tx.object(characterId),
    tx.object(permitObject.data[0].data.objectId), // The single-use permit
    tx.object(CLOCK_OBJECT_ID), // Required for expiry check
  ],
});
```

### 5. Sponsored Transactions

Frontier supports sponsored transactions, allowing admins to cover gas costs for players. This requires collecting signatures from both the player and the sponsor before execution.

```typescript
import { executeSponsoredTransaction } from "../utils/transaction";

await executeSponsoredTransaction(
  tx,
  client,
  playerKeypair,
  adminKeypair,
  playerAddress,
  adminAddress,
);
```

---

## Conclusion

The Smart Gate system represents a paradigm shift in game infrastructure. By separating core physics from player-defined rules, Frontier creates a living, programmable world. Whether building a simple transport route or a complex, tribe-restricted toll network, developers have the tools to define the very horizon of the EVE Frontier.

By combining the **Typed Witness Pattern** for logic with the **Borrow/Return** pattern for authentication, EVE Frontier provides developers with a robust framework for building complex space infrastructure. These TypeScript patterns allow your applications to navigate the "digital physics" of the world while maintaining strict security and character-based identity.
