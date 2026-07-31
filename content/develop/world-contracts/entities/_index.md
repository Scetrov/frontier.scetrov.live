+++
date = '2026-07-31T00:00:00Z'
title = "Entities"
type = "chapter"
weight = 3
codebase = "https://github.com/evefrontier/world-contracts/tree/main/contracts/world/sources"
+++

Entities are predominately used to manage data persistence and shared state in the EVE Frontier world. They are the primary way to store configuration, track state across transactions, and enable cross-assembly interaction. Alongside player-facing entities, the world contracts include server-controlled Rifts: authorized sponsors create, share, broadcast coordinates for, and remove Rifts; Rifts have no `OwnerCap`. This chapter covers the core entity patterns used across world contracts, including:

{{% children sort="weight" %}}

{{% tip-menu-search %}}
