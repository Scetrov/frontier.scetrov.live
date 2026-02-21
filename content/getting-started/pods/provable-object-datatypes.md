+++
date = '2025-04-29 15:14:04'
title = 'Provable Object Datatypes (PODs)'
weight = 10
+++

## Programmable Cryptography

Traditionally we have used special-purpose cryptographic primitives to provide guarantees of specific qualities of a system or data:

- **Signatures** guarantee the integrity of information emitted by a system, Bob can prove to Alice that the message was unchanged between it being signed and the signature verified.
- **Encryption** guarantees that a third party is unable to read information in transit, i.e. Alice is able to pass a message via Edgar to Bob; but Edgar is unable to read the message and Bob is.
- **Authentication** guarantees the authority of a system, i.e. Alice can prove to Bob that she isn't being impersonated as it relates to non-repudiation.
  Programmable Cryptography is a wider technology movement that aims to provide general purpose cryptographic primitives that offer cryptographic guarantees unbounded by the limitations of special-purpose cryptography:
- **Fully-homomorphic Encryption** allows Alice to execute a program over Bob's data without Alice learning anything about the content of the data or the output of the program.
- **Multi-party computation** allows Alice to execute a program over Bob, Charlie and David's data without Alice learning anything about the content of the data, however Alice can see the output of the program.
- **ZKSNARKs** allows Alice to prove that a discrete unit of code was executed on some secret inputs without revealing anything about those inputs.
- **Witness Encryption** allows a message to be encrypted to a program (i.e. a bit of code).
- **Obfuscation** allows a program to be scrambled in such a way that it can still be executed but they can't decompile the program to understand how it works or what it's internal state is.
  Programmable Cryptography can be considered in a similar way to the transition from special-purpose integrated circuits for washing machines towards the use of the now ubiquitous 8086-compatible processors found in many modern appliances.

## PODs in EVE Frontier

CCP have told us that Provable Object Datatypes within EVE Frontier can be used by both CCP by implementing well-known, to EVE Frontier, datatypes for interoperability. They are also available to 3rd-party developers to implement their own capabilities.

### Use Cases

While the possible uses are still emergent there are some obvious use-cases that work well with EVE Frontier:

1. **Information hiding** - preventing there being one big list of all smart assemblies deployed by everyone everywhere.
2. **Ephemeral transactional data** - there are instances where you want to be able to know something once. Gate ticketing is a good example, you don't actually need to keep a record of all historical tickets.
3. **Self-sovereign identity** - only sharing the minimal information required to prove someone has rights to do something. i.e. MJD could issue a gate ticket that allowed a spy to access the REAP gate network without anyone else (even in REAP) knowing. (technically a sub-class of information hiding).
4. **Claims-based identity** - access based upon a set of claims, rather than a set of roles is **much** more expressive.

> [!TIP]
> Most of the API has been "PODified", which means that data about Gate Jumps, Killmails, Types, Solar Systems and Market Data can be issued by EVE Frontier as the signer.

## Further Reading

I strongly recommend reading the following pages:

1. [Introduction to PODs](https://docs.evefrontier.com/pods)
2. [Creating and Verifying PODs](https://docs.evefrontier.com/creating-and-verifying-pods)
3. [Zero Knowledge Proofs](https://docs.evefrontier.com/zero-knowledge-proofs)

> [!TIP]
> The examples are very good if you want to jump in and start coding.

## References

1. [Introduction to PODs - EVE Frontier, CCP (2025)](https://docs.evefrontier.com/pods)
2. [Introduction | pod.org, 0xPARC (2025)](https://pod.org/pod/introduction)
3. [POD resources for EVE Frontier Hackathon 2025, Gubsheep, 0xPARC (2025)](https://0xparc.notion.site/POD-resources-for-EVE-Frontier-Hackathon-2025-1d971e0a5420809b9142f4c77a08c546)
