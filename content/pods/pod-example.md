+++
date = '2025-04-30 12:27:00'
title = 'Creating and Verifying Pods'
weight = 10
+++

CCP have provided an example in the form of [Creating and Verifying PODs](https://docs.evefrontier.com/creating-and-verifying-pods), the below is a slight refinement of these examples I used to understand what was going on.

## Prerequisites

You will need to have setup your tools in line with [Setting Up Your Tools](https://docs.evefrontier.com/Tools) from CCP, specifically you will need the following:

- `node v18` (earlier and later versions are not supported)
- `pnpm v8` or `v9` (later versions are likely to work but are untested)

Check your versions with:

```s
> node --version
< v18.20.8
> pnpm --version
< 9.15.9
```

## Step 1: Setup the Project

First create a folder, for example `~/source/pod-examples`, from your shell:

```sh
mkdir -p ~/source/pod-examples
cd ~/source/pod-examples
```

Install `@pcd/pod' and TypeScript:

```sh
pnpm install @pcd/pod tsx
```

## Step 2: Generate a Key Pair

Create a file named `keygen.ts` and add the following at the top:

```typescript
// Import Packages
import { randomBytes } from 'crypto';
import { deriveSignerPublicKey } from '@pcd/pod';
import * as path from 'path';
import * as fs from 'fs';
```

This imports four libraries including a [Cryptographically Secure Pseudo Random Number Generator](https://nodejs.org/api/crypto.html#cryptorandombytessize-callback), a function from the PODs SDK to derive a keypair and then two libraries for accessing the file system.

In the same file, add code to generate some random bytes using the CSPRNG this is effectively a huge number in the order of 2^256:

```typescript
// Generate a 32-byte random private key
const key: Buffer = randomBytes(32);
```

We need to derive a private key from this huge number, which we do by creating a private signing key:

```typescript
// Convert the key to a hex string
const privateSigningKey: string = key.toString('hex');
console.log("Generated Private Key:");
console.log(privateSigningKey);
```

> [!IMPORTANT]
> Any key that is generated for production must be appropriately secured, either by deriving it from an otherwise secure form of cryptographic randomness, or by deriving the random bytes from a recovery phrase or other form of cryptographic data. Alternatively the private key can be stored encrypted with a password in a database.

and the public signing key:

```typescript
// Output Signer Public Key
const publicSigningKey: string = deriveSignerPublicKey(privateSigningKey);
console.log("\nGenerated Signer Public Key:");
console.log(publicSigningKey);
```

We can then then write these out to files and the console, so that we can use them to create and subsequently verify the POD:

```typescript
// Get the current directory
const currentDirectory: string = process.cwd();
const privateKeyPath: string = path.join(currentDirectory, "private.key");
const publicKeyPath: string = path.join(currentDirectory, "public.key");
fs.writeFileSync(privateKeyPath, privateSigningKey, 'utf8');
fs.writeFileSync(publicKeyPath, publicSigningKey, 'utf8');
```

Save the changes to the file, and then run this keygen command with:

```sh
pnpm tsx keygen.ts
```

### Step 3: Create the POD

Create a new file named `createPod.ts` and add the following imports at the top, again we are pulling in the POD SDK and the utilities to read and write files:

```typescript
// Import Packages
import { POD, PODEntries, JSONPOD, deriveSignerPublicKey } from "@pcd/pod";
import * as fs from 'fs';
import * as path from 'path';
```
Now comes the interesting bit, we create the POD itself:

```typescript
const myEntries: PODEntries = {
  security_level: {
    type: "int",
    value: 4n
  },
  holder_smart_character_address: {
    type: "string",
    value: "0x6d11ac8f376b6284a7e5d62a340f71869b3063ae"
  },
  issued_date: {
    type: "date",
    value: new Date("2025-04-10T00:00:00.000Z")
  },
  expiry_date: {
    type: "date",
    value: new Date("2026-04-10T00:00:00.000Z")
  },
  pod_type: { type: "string", value: "corpName.security_badge" },
};
```

This creates an object as follows:

- `security_level` which is an integer (i.e. a whole number) with a value of `4`.
- `holder_smart_character_address` which is a string and represents the public key / address of the holder.
- `issued_date` which is a date expressed as an ISO 8601 format representing the time the POD was created.
- `expiry_data` which is a date expressed as an ISO 8601 format representing the point in time when this pod becomes invalid.
- `pod_type` is a `string` containing a namespaced typeId, as this is just a string it could be anything but typically forms a dotted hierarchy from left to right.

Next we do some work to load the key pair from disk:

```typescript
// Get the current directory and locate, then load, the private key
const currentDirectory: string = process.cwd();
const privateKeyPath: string = path.join(currentDirectory, "private.key");
const privateSigningKey: string = fs.readFileSync(privateKeyPath, 'utf8');
```

Then we print the public signing key:

```typescript
// Output Signer Public Key
const publicSigningKey = deriveSignerPublicKey(privateSigningKey);
console.log("\nSigner Public Key");
console.log(publicSigningKey + "\n");
```

> [!NOTE]
> The step above is *largely* redundant as we already know this public key from the `keygen.ts` step; it is however useful to have this printed here as a validation and debugging step as an unexpected key would break the verification step below.

Before we create the POD itself:

```typescript
// Create the POD
const myPOD = POD.sign(myEntries, privateSigningKey);
```

And serialize it to a JSON string:

```typescript
// Convert POD to JSON then String
const jsonPOD: JSONPOD = myPOD.toJSON();
const serializedPOD: string = JSON.stringify(jsonPOD);
```

We then print the values to the console and write the pod to `pod.json`:

```typescript
// Output POD
console.log(jsonPOD);
console.log("\nStringified\n");
console.log(serializedPOD);
const serializedPODPath = path.join(currentDirectory, "pod.json");
fs.writeFileSync(serializedPODPath, serializedPOD);
```

Save the changes to the file and run it with:

```sh
pnpm tsx createPod.ts
```

## Step 4: Verify the POD

To verify the POD you will need to create a third file `verifyPod.ts` and again import some functions from the POD SDK and the `fs` and `path` libraries:

```typescript
// Import Packages
import { POD, PODValue } from "@pcd/pod";
import * as fs from 'fs';
import * as path from 'path';
```

Do the work to load the POD and the public key from the files:

```typescript
// Load the POD and Public Key
const currentDirectory: string = process.cwd();
const serializedPODPath: string = path.join(currentDirectory, "pod.json");
const serializedPOD: string = fs.readFileSync(serializedPODPath, 'utf8');
const publicKeyPath: string = path.join(currentDirectory, "public.key");
const officialPublicKey: string = fs.readFileSync(publicKeyPath, 'utf8');
```

You can then parse the POD and load it into the SDK to get a POD in-memory:

```typescript
// Create the POD from the String
const receivedPOD: POD = POD.fromJSON(JSON.parse(serializedPOD));
```

The `POD` type has several utility functions on it allowing for POD operations, for example `.verifySignature()` can be used to verify the POD:

```typescript
// Verify the POD
if(!receivedPOD.verifySignature()){
    throw new Error("Invalid POD");
}

console.log("Verified POD")
```

By checking the `signerPublicKey` from a known trusted source you can validate that it was signed by a trusted party:

```typescript
if(receivedPOD.signerPublicKey != officialPublicKey){
    throw new Error("Not the official signer");
}

console.log("Verified Official Signer")
```

In the same spirit of caution and trust, you can compare the `podType` (or any other known constant values) to ensure that they match the expected type:

```typescript
const officialPodType: string = "corpName.security_badge"
const podType: PODValue | undefined = receivedPOD.content.getValue("pod_type");

if(podType?.value != officialPodType){
    throw new Error("Not the official pod type");
}

console.log("Verified Official Pod Type")
```

Finally extract the `security_level` value from the POD and echo it to the console:

```typescript
// Get a value from the POD
const level: PODValue | undefined = receivedPOD.content.getValue("security_level");
console.log("Level:", level?.value)
```

Save the changes and the file and run it with:

```sh
pnpm tsx verifyPod.ts
```

## Summary

In this article we have used TypeScript to:

- ✅ Generate a public/private key pair,
- ✅ Create a POD and sign it with the **private** key,
- ✅ Verify the same POD with the **public** key.

I'm going to be using this as a [Kata](https://en.wikipedia.org/wiki/Kata) to help me better understand the process by repeating the exercise every couple of days. This will helm me develop more familiarity with POD and it's SDKs and help me build a new mental model, why don't you join me in this practice by re-implementing it yourself tomorrow.
