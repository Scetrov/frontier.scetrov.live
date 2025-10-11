+++
title = "Sui CLI Visualization"
++
title = "Sui CLI Visualization"
date = 2025-10-11T00:00:00Z
draft = false
type = "doc"
weight = 5
description = "A single-page reference and diagram for the entire `sui` CLI command tree."
+++

This page documents the full `sui` command tree (top-level commands and the most important subcommands). Use this as a quick orientation; for runnable examples and recipes see `.github/sui-cli-instructions.md`.

Below is a Mermaid class diagram showing the full CLI tree at a glance in left-right orientation. Expand specific nodes with `sui <command> --help` for deeper options.

```mermaid
classDiagram
    direction LR
    
    class sui {
        <<root>>
        +start
        +network
        +genesis
        +genesis-ceremony
        ++
        title = "Sui CLI Visualization"
        date = 2025-10-11T00:00:00Z
        draft = false
        type = "doc"
        weight = 5
        description = "A single-page reference and diagram for the entire `sui` CLI command tree."
        ++

        This page documents the top-level `sui` command tree (top-level commands and important subcommands). Use this as a quick orientation; for runnable examples and recipes see `.github/sui-cli-instructions.md`.

        Below is a Mermaid class diagram showing the CLI tree at a glance in left-right orientation. Expand specific nodes with `sui <command> --help` for deeper options.

        ```mermaid
        classDiagram
            direction LR

            class sui {
                <<root>>
                +start
                +network
                +genesis
                +genesis-ceremony
                +keytool
                +client
                +validator
                +move
                +bridge-committee-init
                +fire-drill
                +analyze-trace
                +replay
            }

            class start {
                <<command>>
                +--network.config
                +--force-regenesis
                +--with-faucet
                +--with-indexer
                +--with-graphql
                +--pg-port
                +--pg-host
                +--pg-db-name
                +--pg-user
                +--pg-password
                +--fullnode-rpc-port
                +--epoch-duration-ms
                +--data-ingestion-dir
                +--no-full-node
                +--committee-size
            }

            class network {
                <<command>>
                +--network.config
                +--dump-addresses
            }

            class genesis {
                <<command>>
                +--from-config
                +--write-config
                +--working-dir
                +--force
                +--epoch-duration-ms
                +--benchmark-ips
                +--with-faucet
                +--committee-size
            }

            class genesis_ceremony {
                <<command>>
                +init
                +validate-state
                +add-validator
                +list-validators
                +build-unsigned-checkpoint
                +examine-genesis-checkpoint
                +verify-and-sign
                +finalize
            }

            class keytool {
                <<command>>
                +update-alias
                +convert
                +decode-or-verify-tx
                +decode-multi-sig
                +generate
                +import
                +export
                +list
                +load-keypair
                +multi-sig-address
                +multi-sig-combine-partial-sig
                +multi-sig-combine-partial-sig-legacy
                +show
                +sign
                +sign-kms
                +unpack
                +zk-login-sign-and-execute-tx
                +zk-login-enter-token
                +zk-login-sig-verify
                +zk-login-insecure-sign-personal-message
            }

            class client {
                <<command>>
                +active-address
                +active-env
                +addresses
                +balance
                +call
                +chain-identifier
                +dynamic-field
                +envs
                +execute-signed-tx
                +execute-combined-signed-tx
                +faucet
                +gas
                +merge-coin
                +new-address
                +new-env
                +object
                +objects
                +party-transfer
                +pay
                +pay-all-sui
                +pay-sui
                +ptb
                +publish
                +serialized-tx
                +serialized-tx-kind
                +split-coin
                +switch
                +tx-block
                +transfer
                +transfer-sui
                +upgrade
                +verify-bytecode-meter
                +verify-source
                +remove-address
                +replay-transaction
                +replay-batch
                +replay-checkpoint
            }

            class ptb {
                <<subcommand>>
                +--assign
                +--dry-run
                +--dev-inspect
                +--gas-coin
                +--gas-budget
                +--gas-price
                +--gas-sponsor
                +--make-move-vec
                +--merge-coins
                +--move-call
                +--split-coins
                +--transfer-objects
                +--publish
                +--upgrade
                +--preview
                +--tx-digest
                +--sender
                +--serialize-unsigned-transaction
                +--serialize-signed-transaction
                +--summary
                +--warn-shadows
            }

            class validator {
                <<command>>
                +make-validator-info
                +become-candidate
                +join-committee
                +leave-committee
                +display-metadata
                +update-metadata
                +update-gas-price
                +report-validator
                +serialize-payload-pop
                +display-gas-price-update-raw-txn
                +register-bridge-committee
                +update-bridge-committee-node-url
            }

            class move {
                <<command>>
                +build
                +coverage
                +disassemble
                +manage-package
                +migrate
                +new
                +test
                +summary
            }

            class coverage {
                <<subcommand>>
                +summary
                +source
                +bytecode
                +lcov
            }

            class bridge_committee_init {
                <<command>>
                +--network.config
                +--client.config
                +--bridge_committee.config
            }

            class fire_drill {
                <<command>>
                +metadata-rotation
            }

            class analyze_trace {
                <<command>>
                +gas-profile
                +--path
                +--output-dir
            }

            class replay {
                <<command>>
                +--client.config
                +--client.env
                +--digest
                +--digests-path
                +--terminate-early
                +--trace
                +--output-dir
                +--show-effects
                +--overwrite
            }

            sui --> start
            sui --> network
            sui --> genesis
            sui --> genesis_ceremony
            sui --> keytool
            sui --> client
            sui --> validator
            sui --> move
            sui --> bridge_committee_init
            sui --> fire_drill
            sui --> analyze_trace
            sui --> replay
            client --> ptb
            move --> coverage

        ```
            sui --> fire_drill

            sui --> analyze_trace
