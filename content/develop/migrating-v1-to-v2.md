+++
date = '2025-06-11T15:31:00+01:00'
title = 'Migrating from v1 to v2 (New Era)'
weight = 50
+++

There are some fairly substantial changes migrating from EVE Frontier Founder Access Cycle 4 to the New Era, these are my notes on the things that I have had to change to bring it in-line with Smart Object Framework v2 and the World API v2.

> [!IMPORTANT]
> This document is incomplete, and not intended to be canonical or complete, if you find additional areas please feel free to [Send a Pull Request](https://github.com/Scetrov/frontier.scetrov.live/compare) or message me on Discord (User ID: `265550347433410560`)

## World API

The majority of the routes in the World API have been removed and been replaced with new routes prefixed with `/v2` with pagination support through the `limit=10` and `offset=0` semantics.

### Native Pagination

Any endpoint that used to return a JSON array `[ { } ]` now returns a paginated structure alongside metadata:

```json
{
    "data": [
        ... objects in the page ...
    ],
    "metadata": {
        "total": 350,
        "limit": 10,
        "offset": 0
    }
}
```

You can control which page of the API is returned by passing `offset=o` where `o` is a positive integer or zero that represents the number of items to skip (i.e. it's not the page number). You can control how many results are returned by passing the `limit=l` where `l` is a positive integer that controls the number of results returned in a single page payload. The limits seem to default to 10 and have a maximum value of 100 for most endpoints.

### Authentication

There are four new endpoints that require Authentication, at the moment there isn't a user interface for getting a JWT, however you can grab one from the EVE Frontier Website:

1. Go to https://evefrontier.com/en and Login,
2. Open DevTools by pressing `F12` and switch to the **Application** tab,
3. Find the `__Secure-eve-frontier.session-token` cookie, the value should start with `ey`,
4. Either use https://jwt.io or a tool like DevToys to decode this JWT,
5. Once decoded it will contain an `access_token` field in the token, you use this for the `Authorization` header in the format `Authorization: Bearer {access_token}`,
6. You should now be able to call the authenticated endpoints to GET a payload.

## Mud World

There is a new Mud World for Era 6 - Cycle 1 with the Store Address: `0xcdb380e0cd3949caf70c45c67079f2e27a77fc47` this is an instance of the v2 world structure so there are some significant changes to the tables:

- The `eveworld` namespace has been renamed to `evefrontier`,
- The old `eveerc721*` namespaces have been removed, some of the data has been moved to the `evefrontier` namespace, this is because SmartCharacters and SmartAssemblies are no longer implemented as ERC-721 NFTs,
- The word `Table` has been removed from the end of many tables:
  - `CharactersTable` becomes `Characters`,
  - `CharactersByAddr` becomes `CharactersByAcco` to reflect ERC-4337's use of Account for Account Abstraction,
  - `LocationTable` becomes `Location` (note: no `s` on the end),
  - `EntityTable` becomes `Entity`,
  - `SmartAssemblyTable` becomes `SmartAssembly`
  - `DeployableFuelBa` becomes `Fuel`
  - ... and so on
- Many of the fields have been renamed within the tables, this is because there is a new [Class/Object/System Relation Map](https://github.com/projectawakening/world-chain-contracts/blob/develop/mud-contracts/smart-object-framework-v2/class_object_system.jpg) for v2
  - Characters (*previously CharactersTable*):
    - `characterId` becomes `smartObjectId`
    - `corpId` becomes `tribeId`
  - CharactersByAddr (*previously CharactersByAcco*)
    - `characterAddress` becomes `account`,
    - `characterId` becomes `smartObjectId`,
  - Fuel (*was DeployableFuelBa*)
    - `fuelConsumptionPerMinute` becomes `fuelBurnRateInSeconds` (this was always a burn rate, just the name of the column was poorly named)
- There are several new Tables for the new Smart Assemblies and to support Smart Object Framework v2:
  - `NetworkNoteEnerg`
  - `NetworkNodeByAss` (LOL)
  - `NetworkNodeAssem`
  - `NetworkNode`
  - `Tenant`