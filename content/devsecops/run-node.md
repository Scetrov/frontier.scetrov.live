+++
date = '2025-04-28T16:22:00+01:00'
title = 'Run a Redstone, Garnet or Pyrope Node'
weight = 10
+++

Ensure that Docker and Docker Compose are installed, then checkout the git repository, we're going to make some changes to it though:

```sh
git clone https://github.com/latticexyz/redstone-node.git
```

I suggest you use multiple shells as there are some long running processes, in the first shell:
```sh
cd redstone-node/docker-compose/
mkdir data
cd data
wget -c https://pub-b17471e3fbff42cc9f1ed12b36844067.r2.dev/geth-latest.tar.gz
tar xvzf geth-latest.tar.gz
rm geth-latest.tar.gz
cd ..
```

In the second shell:
```sh
cd redstone-node/docker-compose/
```

Edit `.env` and add:
```ini
L1=https://rpc.ankr.com/eth_holesky
```

> [!IMPORTANT]
> Ankr has **just** enough of an allowance (~30/request/sec) for this to work.

Edit `./config/garnet/run-consensus-layer.sh` and update the command:
```sh
  --l2=http://op-geth:8551 \
  --metrics.enabled \                    # add this line
  --l2.jwt-secret=/data/geth/jwtsecret \
```

Once the the download and untargz of the data is done in the first shell it can be closed, then in the remaining shell:
```sh
docker compose -f garnet-compose.yml up -d
```

You can trail the logs with:
```sh
docker compose -f garnet-compose.yml logs -f --tail 10
```
For reduced typing the following `start.sh` and `stop.sh` can be used:
## `start.sh`

```sh
#!/bin/bash

cd ~/redstone-node/docker-compose
podman compose -f garnet-compose.yml up -d && podman compose -f garnet-compose.yml logs -f --tail 10
```
## `stop.sh`

```sh
#!/bin/bash

cd ~/redstone-node/docker-compose
podman compose -f garnet-compose.yml down --remove-orphans --rmi all -t 30 -v
```