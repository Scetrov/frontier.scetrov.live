+++
date = '2025-04-28T16:22:00+01:00'
title = 'Upgrade Mud'
weight = 70
+++

Sometimes Mud is updated mid-cycle with a bug fix that you need to pull in to get something deployed:

```sh
pnpm mud set-version --tag main && pnpm install
```

This will essentially use the bleeding edge version of Mud.