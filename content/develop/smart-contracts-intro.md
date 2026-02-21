+++
date = '2026-02-21T12:23:00Z'
title = "Introduction to Smart Contracts"
weight = 5
description = "Overview of smart contracts in EVE Frontier — what they are, how Frontier uses them, and key Move patterns."
+++

## What Are Smart Contracts?

Smart contracts are programs that execute on the blockchain. They enforce persistent rules, manage assets, automate actions, and run shared logic in a secure, deterministic, and verifiable way. In EVE Frontier, smart contracts are the foundation for Smart Assembly functionality and on-chain business logic. Contracts are written in [Move](https://move-book.com/) and deployed to [Sui](https://sui.io/).

Sui validators compile and verify Move modules, execute transactions on the Move VM, and persist the resulting state on-chain. This ensures that all business logic runs deterministically and that any participant can verify correctness.

---

## How Frontier Uses Smart Contracts

EVE Frontier uses smart contracts to power a world that is open to builders. Game characters, storage units, gates, turrets, and more live on-chain as objects created from smart contracts. The logic that mutates and queries this state is implemented in Move modules, allowing builders to extend and interoperate with the game through well-defined, auditable interfaces.

Key aspects:

* **Objects as Game State** — In-game assets (items, assemblies, characters) are represented as Move structs/objects on Sui. Each object has a unique ID, ownership (owned by address, owned by object, or shared), and typed fields. Functions in smart contracts create, transfer, and mutate these objects.
* **Deterministic Execution** — All logic runs on the Move virtual machine in a deterministic way. The same inputs produce the same outputs for every validator, enabling consensus and verification.
* **Modular Design** — Business logic is organized into separate Move modules. Smart Assemblies (Storage Unit, Gate, Turret) are implemented as distinct modules that can be composed and extended.

---

## Access Control

Smart contracts enforce who can call what and when:

* **Function Visibility** — Move supports `public`, `public(package)`, and `public(entry)` functions. Public functions are directly callable from transactions; `public(package)` functions are callable only by modules in the same package.
* **Capability-Based Access** — Many operations require a capability object (e.g., `OwnerCap`, `JumpPermit`) or a shared access-control object (`AdminACL`). The caller must own the capability or be an authorized sponsor to perform the action. This pattern enables fine-grained, transferable permissions.
* **Typed Witness** — Restrict function callers by requiring a witness type as an argument. Only callers able to construct (or receive) that type can invoke the function, which lets player-built packages call world functions when authorized. See [typed witness pattern](https://move-book.com/programmability/witness-pattern).
* **Publisher Object** — A [Publisher](https://move-book.com/programmability/publisher) object is claimed in a package's `init` function using a one-time witness. It proves authorship of a package and is used to authorize package-level operations.
* **Transaction Context** — The `TxContext` provides sender address, epoch, and other transaction-level data. Contracts use this to enforce rules such as "only the owner" or "only during a specific epoch."

---

## Move Patterns in Frontier

* **Capability Pattern** — A capability object grants rights (e.g., admin, owner) to specific actions. Only accounts holding the capability can call permissioned functions. See [`access_control.move`](world-contracts/access/access_control.move/).
* **Hot Potato** — A one-time-use object that must be consumed within the same transaction. Used to enforce that a sequence of actions completes atomically (e.g., when a parent node goes offline, all connected assemblies must go offline).
* **Shared Objects** — Most Frontier objects are shared so that the game server and multiple parties can read and mutate them. Shared objects use Sui's built-in versioning and access control for concurrent updates.

---

## Next Steps

* [EVE Frontier World Explainer](world-contracts/) — Overview of the three-layer world architecture.
* [Object Model](object-model/) — How in-game items map to on-chain objects.
* [Ownership Model](ownership-model/) — Capability-based access control hierarchy.
* [Move documentation](https://move-book.com/concepts/) — Move language concepts.
* [World Contracts source](https://github.com/evefrontier/world-contracts) — Source code and examples.
