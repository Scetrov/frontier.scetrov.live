+++
date = '2025-04-28T16:22:00+01:00'
title = 'Solidity and Mud'
weight = 5
+++

If anyone is new to Ethereum Virtual Machine and Solidity I have some resources that I have found useful:

- **[Ethereum Book](https://github.com/ethereumbook/ethereumbook)** - Antonopoulos & Woods is freely available on GitHub, you can also buy it in paperback or as an eBook.
- **Solidity Overview** - Blockchain Council has a [quick writeup](https://www.blockchain-council.org/ethereum/solidity-for-beginners-a-guide-to-getting-started/) on Solidity, it's a five minute read at most.
- **Microsoft Solidity (Intro Course)** - Microsoft has a [short 45m course](https://learn.microsoft.com/en-us/training/modules/blockchain-learning-solidity/) on Solidity fundamentals
- **Full Blockchain Development Course** - If you prefer video content then [Cyfrin Updraft](https://updraft.cyfrin.io/) covers everything from basics to DevOps with Foundry and auditing smart contracts.
- It's worth reading through [MUD Documentation](https://mud.dev/introduction) and doing the [Guides](https://mud.dev/guides/hello-world). If you get stuck on a Mud then they have a [Discord](https://discord.gg/latticexyz) Channel named `#mud-help`.
- If you get stuck then ChatGPT/Claude is useful, however the more developer focused [Phind](https://www.phind.com/search?home=true) works best if you ask it full questions.
- If you still need more help then there is always the [Ethereum StackExchange](https://ethereum.stackexchange.com/) or [Peeranha](https://www.peeranha.io/).

> [!IMPORTANT]
> There is nothing wrong with ignoring all of these resources and jumping in and having a go, the Smart Object Framework and Mud abstract a lot of the complexity so it's entirely possible to get started with a basic terminal and a text editor, no experience required.

## Stay Safe On Chain

This project has been and will continue to be the target for bad actors, there are some steps you can take to protect yourself.

1. If in doubt don't sign the transaction, and ask someone you trust for advice.
2. Use tools like [ScamSniffer](https://www.scamsniffer.io/), [WalletGuard](https://www.walletguard.app/) and Blockaid (in Metamask) to scan transactions. They are not fool proof though, they will frequently miss new threats.
3. Store your password recovery phrase in a secure location, ideally offline in a way that is resistant to corrosion and fire damage.
4. Use a hardware wallet to store anything of value in a cold wallet, and keep it in a safe place, never use it for day to day transactions.
5. Don't use the same private keys for testnet and mainnet, assume your testnet keys are compromised from the moment you create them.

## Stay Safe Off Chain

Bad actors will use social engineering and phishing to attempt to gain access to your accounts, including Discord and crypto wallets, be aware of the scams:

1. Wallet Drainers are often disguised as wallet verification tools in community discord servers, only trust verification from official servers.
2. Wallet Drainers may also be spammed as claim links and airdrop notifications on Discord and services such as Telegram, Signal and IRC, if you are redirected to a suspicious domain, exit out of the window and inform community admins immediately.
3. You may be contacted in a chat channel or DMs by someone from "an affiliated project" offering you a paid position as a play tester, they are likely trying to steal your discord username and password so that they can spam scam links to other discords.
4. It is likely that at some point a mod or developer will have their account compromised through phishing or session stealing, be wary of unexpected announcements about airdrops, coin distributions or claiming access.
5. **As a rule if it seems too good to be true, it probably is.**