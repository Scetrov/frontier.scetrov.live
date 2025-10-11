+++
date = '2025-04-28T16:22:00+01:00'
title = 'Mud Resource IDs'
weight = 20
+++

They are encoded in a similar way to how ABI is encoded, albeit using slightly different methods.

Typically it's possible to simply chop the `0x` from the beginning, parse it as a `BigInteger` or another type that supports huge numbers, convert to a byte array and then to a string, trimming any `\0` characters from the end.

However you can take the byte offset and length to extract out the parts of the string if you know what the scheme is:

```csharp
var inputNumeric = BigInteger.Parse(inputRaw, NumberStyles.HexNumber);
var inputBytes = inputNumeric.ToByteArray().Reverse().ToArray();
var resourceType = Encoding.UTF8.GetString(inputBytes[..2]).TrimEnd('\0');
var namespaceId = Encoding.UTF8.GetString(inputBytes[2..16]).TrimEnd('\0');
var systemId = Encoding.UTF8.GetString(inputBytes[16..]).TrimEnd('\0');
```

You can also do this from the command line as long as you have Foundry installed:

```sh
> cast --to-ascii 0x7379657665776f726c64000000000000536d61727453746f72616765556e6974
< syeveworldSmartStorageUnit
```

The first two digits represent the type of resource:

 - `sy` means System
 - `tb` means Table