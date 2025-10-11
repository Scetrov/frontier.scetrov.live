+++
date = '2025-10-10T19:08:00+01:00'
title = 'Jargon Buster'
weight = 30
+++

As with all of blockchain Sui comes with it's own buzzwords and jargon that confuse new users:

- **`Coin<T>` (Coin of T)** - a generic type in Sui that represents a coin of a specific type T. This allows for the creation and management of different types of coins on the Sui blockchain. This also means you can have multiple stacks of one type of coin in your account with each object (stack) having an individual object ID, balance and owner. You can call `splitCoins` and `mergeCoins` to manage stacks of coins.
- **Epochs** - time periods in the Sui blockchain that are used to manage the network's consensus and governance. Each epoch lasts for a fixed duration, and at the end of each epoch, the network's validators are rotated to ensure decentralization and security.
- **Equivocation** - a security feature in Sui that prevents double-spending and ensures the integrity of transactions. It involves the use of cryptographic techniques to verify the authenticity of transactions and prevent fraud.
- **Fullnodes** - nodes in the Sui network that maintain a complete copy of the blockchain and participate in the network's consensus process. Fullnodes are responsible for validating transactions, producing new blocks, and ensuring the integrity of the Sui blockchain.
- **Groth16** - a type of zero-knowledge proof system used in Sui to enable privacy-preserving transactions. Groth16 zk-SNARKs allows users to prove the validity of a transaction without revealing any sensitive information about the transaction itself.
- **Indexer** - a component of the Sui blockchain that maintains a searchable index of all objects and transactions on the network. The Indexer allows users to quickly and easily find specific objects and transactions, making it easier to interact with the Sui blockchain.
- **Loyalty Tokens** - a type of token on the Sui blockchain that represents a user's loyalty or commitment to a particular project or community. These tokens can be used to incentivize and reward users for their participation and engagement and can only be used within the context of the project that issued them.
- **Move** - the programming language used to write smart contracts on the Sui blockchain. It's designed to be safe and flexible, with similarities to Rust, C# and TypeScript.
- **Objects** - the fundamental building blocks of data on the Sui blockchain. Everything in Sui is represented as an object, including accounts, coins, and smart contracts.
- **Programmable Transaction Blocks (PTBs)** - is a feature that allows developers to create custom transaction logic and workflows on the Sui blockchain. PTBs enable more complex interactions and operations within a single transaction.
- **Sponsorship** - a mechanism that allows users to pay for transaction fees on behalf of other users. This is particularly useful for onboarding new users who may not have SUI tokens to pay for gas fees or in the context of EVE Frontier for a game developer to pay for the gas fees of their players as part of a subscription.
- **Sui Name Service (SNS)** - a decentralized naming system that allows users to register human-readable names for their Sui addresses. SNS makes it easier for users to share and remember their Sui addresses, similar to how domain names work on the internet.
- **Validators** - nodes in the Sui network that are responsible for validating transactions and producing new blocks. Validators are selected through a staking mechanism, where users can stake their SUI tokens to become validators and earn rewards for their participation in the network.
- **Verifiably Random Function (VRF)** - a cryptographic function that generates random values that can be verified by others. In Sui, VRFs are used to ensure the fairness and randomness of certain operations, such as leader election and transaction ordering.
- **zkLogins** - a privacy-preserving authentication mechanism that allows users to prove their identity, using Apple, Facebook, Google, Microsoft, etc., without revealing any sensitive information. zkLogins use zero-knowledge proofs to enable secure and private authentication on the Sui blockchain.
