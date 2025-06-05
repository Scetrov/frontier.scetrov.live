+++
date = '2025-06-05T12:02:00+01:00'
title = 'Understanding Wallets'
weight = 50
+++

There is often a lot of confusion with terms used for the tools we use to access the blockchain, predominantly these are:

- **Wallets** a bit of software that is used to store private keys,
- **Accounts** a single Blockchain account identified by a unique Public Key and secured through a Private Key
- **Account Index** a part of BIP-44 that allows multiple indexed account to be derived from a single seed phrase.
- **Seed Phrase** and **Mnemonic Code** are effectively the same thing although different standards use different words.

Technically all you need to have access to be able to sign and transmit transactions using a Wallet is the Private Key, however virtually all Wallets allow for the import of a BIP-39 Seed Phrase from which many wallets can be derived. EVE Vault is no different, however as it stands it only supports importing a seed phrase not a private key, other wallets such as OneKey (which EVE Vault is based upon) and Metamask will allow the import of private keys alone.

Seed Phrases were invented to make it easier for end-users to backup and transcribe keys onto paper or between air-gapped systems, typically it is a lot easier for a user to type `deer grace speed cargo frame cushion wall filter deputy wire squeeze happy` than it is to type `0xed621b05d05a65658e42b9af8eb6713009780ac517eb0ed712eeb61db873ceee` despite them being of similar length and encapsulating the same data.

> BIP39 was introduced by Marek Palatinus, Pavol Rusnak, Aaron Voisine, and Sean Bowe in 2013 to propose a standardized method of generating mnemonic sentences for deterministic wallets. The idea behind BIP39 was to create a process that could be universally adopted, ensuring cross-compatibility between different wallets.
> -- [Trezor](https://trezor.io/learn/advanced/what-is-bip39)

It is important to note that the BIP39 words results in an *Extended Public Key* which is combined with the [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) derivation path to form a [Hierarchical Deterministic Wallet (BIP-32)](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki). There are several other schemes for deriving wallets, and many wallets support several of them, see also [BIP-49](https://github.com/bitcoin/bips/blob/master/bip-0049.mediawiki), [BIP-84](https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki) and [BIP-141](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki) - you can play about with all of these on [Ian Coleman's Mnemonic Code Converter](https://iancoleman.io/bip39/).

What this means is effectively each seed phrase (i.e. `need enter link blood addict year vicious vendor below soup invest crime`) will result in an entire hierarchy of wallets which while all derived from the same 144-bit (for a 12-word phrase) or 288-bit (for a 24-word phrase) number are not mathematically provable as being connected to each other.

Not every wallet uses BIP-44 in it's entirety, but chances are EVE Vault increments either `account` or `address_index` in the derivation path: `purpose' / coin_type' / account' / change / address_index` to create accounts 1-3... it could in theory use 5 or 69 it wouldn't matter as you can keep increasing either of those numbers and probabilistically create practically infinite wallets.

You might ask:

> could we not run out of addresses if everyone can just increment the number

Given that the lower estimate of the number of atoms in the universe is 10^78 which is the same magnitude as a 256-bit number. Not every single number in that magnitude is a valid address, because they have to be on the `SECP256k1` curve, specifically, can't be zero and must be smaller than `ffffffff ffffffff ffffffff fffffffe baaedce6 af48a03b bfd25e8c d0364141` roughly 10^52. However, the chances of a collision are astronomically low.

More importantly the electricity cost to generate a single address is many orders of magnitude higher than the average value across all possible Ethereum addresses. This means that for every $1 of electricity you spent you would likely manage to guess 1/10^35 worth of ETH - not to mention that if we were to capture the entire solar output of our sun (Dyson Sphere) and build all of the conventional computers from all of the resources in our solar system then the sun would still be exhausted before we searched the entire address space.

Quantum Computing is another matter however, and Ethereum has a plan for building further [Quantum Resistance into Ethereum](https://ethereum.org/en/roadmap/future-proofing/) in the future.