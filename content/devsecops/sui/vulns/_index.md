+++
title = 'Possible Vulnerabilities'
date = '2025-11-26T00:00:00Z'
+++

This section documents **34 vulnerability classes** commonly found in Sui Move smart contracts. Each vulnerability has its own dedicated page with detailed explanations, vulnerable code examples, and recommended mitigations.

## Overview

Sui Move contracts face unique security challenges due to the object-centric model, capability-based access control, and programmable transaction blocks (PTBs). Understanding these vulnerabilities is essential for writing secure smart contracts.

## Vulnerability Categories

### Access Control & Authorization (1-9)
- [Object Transfer Misuse](object-transfer-misuse/) - Unintended object transfers breaking invariants
- [Object Freezing Misuse](object-freezing-misuse/) - Malicious freezing of critical objects
- [Numeric / Bitwise Pitfalls](numeric-bitwise-pitfalls/) - Overflow and shift operation issues
- [Ability Misconfiguration](ability-misconfiguration/) - Improper `copy`, `drop`, `store`, `key` abilities
- [Access-Control Mistakes](access-control-mistakes/) - `TxContext` and sender verification issues
- [Shared Object DoS](shared-object-dos/) - Denial of service via shared object contention
- [Improper Object Sharing](improper-object-sharing/) - Accidental exposure of objects as shared
- [Dynamic Field Misuse](dynamic-field-misuse/) - Child-object and dynamic field vulnerabilities
- [Sponsored Transaction Pitfalls](sponsored-transaction-pitfalls/) - Meta-transaction authority confusion

### Logic & State Management (10-20)
- [General Move Logic Errors](general-move-logic-errors/) - PTB reordering and mutation issues
- [Capability Leakage](capability-leakage/) - Authority leakage via indirect APIs
- [Phantom Type Confusion](phantom-type-confusion/) - Type parameter injection attacks
- [Unsafe Object ID Usage](unsafe-object-id-usage/) - Identity assumptions on child objects
- [Dynamic Field Key Collisions](dynamic-field-key-collisions/) - Key collision vulnerabilities
- [Event Design Vulnerabilities](event-design-vulnerabilities/) - Ambiguous or missing events
- [Unbounded Child Growth](unbounded-child-growth/) - State bloat from unlimited children
- [PTB Ordering Issues](ptb-ordering-issues/) - Non-deterministic PTB execution
- [PTB Refund Issues](ptb-refund-issues/) - Inconsistent state from partial execution
- [Ownership Model Confusion](ownership-model-confusion/) - Incorrect ownership transitions
- [Weak Initializers](weak-initializers/) - Reinitialization attacks

### External Integration & Advanced (21-34)
- [Oracle Validation Failures](oracle-validation-failures/) - Off-chain oracle trust issues
- [Unsafe Option Authority](unsafe-option-authority/) - Authority toggles via Option
- [Clock Time Misuse](clock-time-misuse/) - Timestamp and time logic vulnerabilities
- [Transfer API Misuse](transfer-api-misuse/) - Object ownership model transitions
- [Unbounded Vector Growth](unbounded-vector-growth/) - Gas exhaustion from large vectors
- [Upgrade Boundary Errors](upgrade-boundary-errors/) - ABI breaks on package upgrades
- [Event State Inconsistency](event-state-inconsistency/) - State/event synchronization
- [Read API Leakage](read-api-leakage/) - Information exposure via view functions
- [Unsafe BCS Parsing](unsafe-bcs-parsing/) - Off-chain deserialization issues
- [Unsafe Test Patterns](unsafe-test-patterns/) - Test code leaking to production
- [Unvalidated Struct Fields](unvalidated-struct-fields/) - Missing input validation
- [Inefficient PTB Composition](inefficient-ptb-composition/) - Gas exhaustion patterns
- [Overuse of Shared Objects](overuse-of-shared-objects/) - Unnecessary sharing risks
- [Parent Child Authority](parent-child-authority/) - Implicit authority assumptions

---

## OWASP / MITRE CWE Mapping

| #  | Vulnerability Class                | OWASP Top 10 | MITRE CWE                 |
| -- | ---------------------------------- | ------------ | ------------------------- |
| 1  | Object Transfer Misuse             | A01          | CWE-284, CWE-275          |
| 2  | Object Freezing Misuse             | A01          | CWE-284, CWE-732          |
| 3  | Numeric / Bitwise Pitfalls         | A06 / A03    | CWE-681, CWE-190          |
| 4  | Ability Misconfiguration           | A01          | CWE-284, CWE-266          |
| 5  | Access-Control Mistakes            | A01          | CWE-285, CWE-639          |
| 6  | Shared Object DoS                  | A05 / A06    | CWE-400, CWE-834          |
| 7  | Improper Sharing of Objects        | A01          | CWE-284, CWE-277          |
| 8  | Dynamic Field Misuse               | A01 / A05    | CWE-710, CWE-915          |
| 9  | Sponsored TX Pitfalls              | A01          | CWE-285, CWE-863          |
| 10 | Reentrancy-like PTB Issues         | A01 / A04    | CWE-841, CWE-362          |
| 11 | Accounting / Fee Logic Bugs        | A04          | CWE-682, CWE-840          |
| 12 | Capability Leakage                 | A01          | CWE-284, CWE-668          |
| 13 | Phantom Type Confusion             | A04          | CWE-693, CWE-704          |
| 14 | Unsafe `object::id()`              | A01          | CWE-639, CWE-915          |
| 15 | Dynamic Field Key Collisions       | A01 / A05    | CWE-653, CWE-706          |
| 16 | Event Model Vulnerabilities        | A04 / A09    | CWE-223, CWE-778          |
| 17 | Unbounded Child Growth             | A06 / A05    | CWE-400, CWE-770          |
| 18 | PTB Order Logic Flaws              | A04          | CWE-841, CWE-662          |
| 19 | Ownership-Model Confusion          | A01          | CWE-284, CWE-266          |
| 20 | Weak Initializers                  | A01          | CWE-284, CWE-665          |
| 21 | Oracle Validation Failures         | A08          | CWE-345, CWE-353          |
| 22 | Unsafe `Option` Authority          | A04          | CWE-696, CWE-693          |
| 23 | Clock / Time Misuse                | A04          | CWE-682, CWE-664          |
| 24 | Misuse of Transfer APIs            | A01          | CWE-284                   |
| 25 | Unbounded Vector Growth            | A05          | CWE-770                   |
| 26 | Upgrade Boundary Errors            | A04 / A06    | CWE-685, CWE-694          |
| 27 | Event-State Inconsistency          | A09          | CWE-778, CWE-223          |
| 28 | Read API Leakage                   | A01          | CWE-200 (Info Exposure)   |
| 29 | Unsafe Off-chain Parsing           | A08          | CWE-502, CWE-116          |
| 30 | Unsafe Test Signer Use             | A04          | CWE-704, CWE-665          |
| 31 | Unvalidated Struct Fields          | A04          | CWE-20 (Input Validation) |
| 32 | Inefficient PTBs                   | A05 / A06    | CWE-400                   |
| 33 | Overuse of Shared Objects          | A01          | CWE-284                   |
| 34 | Parent→Child Authority Assumptions | A01          | CWE-863, CWE-284          |

{{% children sort="weight" %}}

{{% tip-menu-search %}}
