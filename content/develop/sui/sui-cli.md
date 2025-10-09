+++
date = '2025-10-09T20:50:00+01:00'
title = 'Sui Client Cookbook'
weight = 20
+++

The [`sui` client](https://docs.sui.io/guides/developer/getting-started) is a command line interface, it can be installed along with other tools in several ways.

## Install

### Homebrew

Homebrew is available for MacOS, Linux and WSL:

```sh
brew install sui
```

### Chocolatey

Chocolatey is an older package manager for Windows:

```pwsh
choco install sui
```

## `suiup`

[`Suiup`](https://github.com/MystenLabs/suiup) is a new tool from MystenLabs and works similar to `rustup`, you can install `suiup` with:

```sh
curl -sSfL https://raw.githubusercontent.com/Mystenlabs/suiup/main/install.sh | sh
```

Then install `sui` with:

```sh
suiup install sui
```

It is also possible to download and install all packages from the [GitHub Releases](https://github.com/MystenLabs/sui/releases) page.

## Cookbook

Below are a fairly unordered series of commands, to copy and paste as required. You will first need to run `sui client` then press `y` then `[Enter]` to create the configuration and an initial keypair.

> [!NOTE]
> Sui's documentation isn't great when it comes to the URL for the RPC endpoint for the avoidance of doubt there are three main RPC nodes for the three main networks:
>
>  - Devnet: `https://fullnode.devnet.sui.io:443`
>  - Testnet: `https://fullnode.testnet.sui.io:443`
>  - Mainnet: `https://fullnode.mainnet.sui.io:443`

> [!INFORMATION]
> For any command you can suffix `--help` to get the help page up, i.e. `sui client --help`. If you want the output to be in JSON format for use in scripts, then use `sui client --json`.

### Creating Accounts

To create a new account using `ed25519` with the alias `alice`:

```sh
sui client new-address ed25519 alice
```

You can optionally provide the word length as `word[12|15|18|21|24]` to provide different length mnemonic phrases / recovery phrases, additionally you can specify the full derivation path, i.e. `m/74'/784'/0'/0/0`.

If you want to create `secp256k1` or `secp256r1` signature scheme accounts simply substitute the 4th parameter.

```sh
sui client new-address secp256k1 bob
```

or

```sh
sui client new-address secp256r1 charlie
```

In each case the cli will output the `alias`, `address` (Public Key), `keyScheme` and `recoveryPhrase` (Mnemonic Phrase) and store the private key in the sui client keystore.

To request testnet funds for an account, use the `faucet` subcommand:

```sh
sui client faucet --address alice
```

You can replace `alice` with any alias you current have generated or imported, this will provide you with a link where you can request SUI for testing purposes. Once requested you can check your balance with:

```sh
sui client balance alice
```

Again replace `alice` with any alias, or even a full address (but I don't recommend it).
