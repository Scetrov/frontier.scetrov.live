+++
date = '2025-04-28T16:22:00+01:00'
title = 'Off-Chain Tables'
weight = 60
+++

It's possible to create off-chain tables, i.e. tables where the data is available via the Mud Indexer but not from the on-chain store.

```typescript
import { defineWorld } from "@latticexyz/world";

export default defineWorld({
  namespace: "scetrov",
  tables: {
    AuditLog: {
      name: "AuditLog",
      type: "offchainTable",
      key: ['timestamp', 'characterId'],
      schema: {
        timestamp: "uint256",
        characterId: "uint256",
        targetCorp: "uint256",
        operation: "uint8"
      }
    },
  },
});
```

In this example we have a table that we can write two with `AuditLog.set(timestamp, characterId)` that the indexer will pickup so we have a chronological record of actions performed on a contract.

> [!NOTE]
> It's possible to recover this information by walking the blocks from the time the contract was deployed and looking for the calls that mutate state; however this required implementing your own decoding and indexing code which is significantly more work and infrastructure.