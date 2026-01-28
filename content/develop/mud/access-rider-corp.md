+++
date = '2025-04-28T16:22:00+01:00'
title = 'Access Rider Corp (from a Smart Contract)'
weight = 10
+++

You can access the corporation that a rider belongs to with the following code:

```solidity
import { CharactersTable } from "../../../codegen/tables/CharactersTable.sol"; uint256

.
. <snip>
.

uint256 playerCorp = CharactersTable.getCorpId(characterId);
uint256 smartGateOwner = CharactersByAddressTable.get(IERC721(DeployableTokenTable.getErc721Address()).ownerOf(sourceGateId));
uint256 smartGateOwnerCorp = CharactersTable.getCorpId(smartGateOwner);
```

> [!IMPORTANT]
> In the future World v2 will remove the IERC721 interface from DeployableTokenTable and, we can however simply call `{table_name}.get(sourceGateId)` without using `IERC721`.
