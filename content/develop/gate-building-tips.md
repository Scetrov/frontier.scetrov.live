+++
date = '2025-07-06 10:37:00'
title = 'Gate Building Tips'
weight = 80
+++

## The Easy Way

The easy way involves simply using the in-game dApp, it requires a little bit of pre-planning but is easy, say you have two gates you want in System A and System B:

1. Jump/Gate to System A and drop a gate, take a note of the location using the in-game notepad,
2. Jump/Gate to System B and drop the second gate, again take a note of the location,
3. Wait 4h from the first gate being anchored, fly back to the gate in System A, add Salt and Bring Online using the dApp,
4. Fly to the gate in System B, add Salt and Bring Online using the dApp,
5. From B, select the gate in System A and click Link

Now jump through from B to A and then back to A to test it. You can apply a contract using [EVE Datacore](https://evedataco.re).

## The Hard Way

This is the way of doing this if for some reason the in-game dApp doesn't work (or stops working), or if you want to understand waht the in-game dApp is doing behind the scenes.

1. [Install EVE Vault](https://docs.evefrontier.com/EveVault/installation) in Chrome/Edge/Brave (anything based on Chromium), try and avoid mixing and matching with other Wallet plugins, use a separate profile if required.
2. Make sure your gates show up on chain and grab the `smartObjectIds` for them, either via [the API](https://blockchain-gateway-stillness.live.tech.evefrontier.com/v2/smartassemblies), via the game (Big number top right) or via [EVE Datacore](https://evedataco.re) (props to WOLF for building a great tool).
3. Use the [Mud Explorer](https://explorer.mud.dev/pyrope/worlds/0xcdb380e0cd3949caf70c45c67079f2e27a77fc47/interact?function=) to link and online them.
4. Link them first with [`evefrontier__linkGates`](https://explorer.mud.dev/pyrope/worlds/0xcdb380e0cd3949caf70c45c67079f2e27a77fc47/interact?function=linkSmartGates#evefrontier__linkGates), sometimes you need to do it for both directions (flip the numbers)
5. Online each gate with [`evefrontier__bringOnline`](https://explorer.mud.dev/pyrope/worlds/0xcdb380e0cd3949caf70c45c67079f2e27a77fc47/interact?function=bringOnline#evefrontier__bringOnline)
6. Once you have everything working, you can Configure the Smart Gates to use your contract, worth getting the gates working first in case you have a bug in your code. CCPs default behavior (allow all) is known to work.

## Troubleshooting

First check to make sure that the `smartObjectId` appears in [`SmartGateConfig`](https://explorer.mud.dev/pyrope/worlds/0xcdb380e0cd3949caf70c45c67079f2e27a77fc47/explore?tableId=0x746265766566726f6e74696572000000536d61727447617465436f6e66696700&query=SELECT%2520%2522smartObjectId%2522%252C%2520%2522systemId%2522%252C%2520%2522maxDistance%2522%2520FROM%2520%2522evefrontier__SmartGateConfig%2522%2520WHERE%2520%2522smartObjectId%2522%2520%253D%25206043610207003986359583354976893946421984347946311295347196971213130287377900%2520LIMIT%252010%2520OFFSET%25200%253B&page=0&pageSize=10) by replacing the long number in the query with your `smartObjectId`:

```sql
SELECT "smartObjectId", "systemId", "maxDistance" FROM "evefrontier__SmartGateConfig" WHERE "smartObjectId" = smartObjectId goes here LIMIT 10 OFFSET 0;
```

Initially the `systemId` will be a null byte array, `0x0000000000000000000000000000000000000000000000000000000000000000`, once you apply your contract this will become your mud `systemId` identifier string encoded as a byte array. The `maxDistance` field is in meters, you can calculate the maximum lightyears by taking the long number i.e. `1040680351983804840` and dividing it by the number of meters in a light year (`9460730472580800`), depending on the precision of your calculator you will either get *110 ly* or something very close to it (i.e. 109.999999999 ly).

If something doesn't work, you can try to unlink them with [`evefrontier__unlinkGates`](https://explorer.mud.dev/pyrope/worlds/0xcdb380e0cd3949caf70c45c67079f2e27a77fc47/interact?function=unLink#evefrontier__unlinkGates), again flipping the numbers works sometimes too. You can toggle them [offline with `evefrontier__bringOffline`](https://explorer.mud.dev/pyrope/worlds/0xcdb380e0cd3949caf70c45c67079f2e27a77fc47/interact?function=offline#evefrontier__bringOffline) and online, but wait 30s between each action so that everything catches up.

**If cycling the gates doesn't work, unlinking and relinking them doesn't work, they are probably broken at the mud level, you need to Dismantle to Cargo Container in-game and rebuild (you get all of the mats and salt back), this way you get a new clean `smartObjectId`.**

From my own experience, and from the experience of AWAR, DEAD and ONYX, this works most of the time, there are still the odd gates that never show up on chain.
