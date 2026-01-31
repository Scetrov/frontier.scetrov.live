# Add Jargon Buster Entry

Add new terminology entries to the technology-specific jargon buster pages.

## Context

The site maintains jargon buster pages to help developers understand terminology:

- `content/getting-started/mud/jargon-buster.md` - EVM/Solidity/MUD terms
- `content/getting-started/sui/jargon-buster.md` - Sui/Move terms

These pages define key terms that developers encounter when working with EVE Frontier.

## Instructions

1. Identify the appropriate jargon buster page based on technology
2. Add entries in alphabetical order within the existing structure
3. Keep definitions concise but complete

## Entry Format

```markdown
### Term Name

Clear, concise definition of the term. Include:
- What it is
- Why it matters in EVE Frontier context
- Any relevant technical details

**Example**: If applicable, a brief code snippet or usage example.

**Related**: Links to related terms or documentation.
```

## Guidelines

### For MUD/EVM Terms

Focus on:

- Solidity concepts (contracts, modifiers, events)
- MUD framework specifics (Systems, Tables, World)
- EVM mechanics (gas, transactions, state)
- EVE Frontier specific terms (Smart Assemblies, World contracts)

### For Sui/Move Terms

Focus on:

- Move language concepts (modules, abilities, generics)
- Sui-specific features (objects, PTBs, shared objects)
- Object model (owned, shared, immutable, wrapped)
- EVE Frontier Sui terms (Primitives, Assemblies, Extensions)

## Example Entries

### MUD Example

```markdown
### System

A Mud System is a stateless smart contract that contains game logic. Systems read and write to Tables (the data layer) and are the only way to modify world state.

**Related**: [Tables](#tables), [World](#world)
```

### Sui Example

```markdown
### Programmable Transaction Block (PTB)

A PTB is a batch of transactions executed atomically on Sui. Unlike EVM transactions, PTBs can compose multiple function calls that pass objects between them within a single block.

**Example**: A PTB might create an object in one call, modify it in another, and transfer it in a third—all atomically.

**Related**: [Object](#object), [Transaction](#transaction)
```

## User Input Required

- **Technology**: MUD/EVM or Sui/Move?
- **Term**: What term needs to be defined?
- **Definition**: Clear explanation of the term
- **Context**: How does this relate to EVE Frontier development?
- **Examples**: Any code or usage examples?
- **Related terms**: Other relevant jargon buster entries
