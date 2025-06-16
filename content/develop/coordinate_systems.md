+++
date = '2025-04-28T16:22:00+01:00'
title = 'Coordinate Systems'
weight = 60
+++

The EVE Frontier game happens in three-dimensional space. Every object has a corresponding vector `(x, y, z)`, measured in meters. Each component can be positive or negative. The origin `(0, 0, 0)` is close to the galactic center.

There are five distinct sources of three dimensional coordinates:

1. The `/v2/solarsystems` and `/v2/solarsystems/{id}` endpoints in the World API, in addition to the `solarSystem` object on various other payloads this states the coordinates in absolute terms relative to the galactic center, however only in limited precision (it appears to be about 16-17 bits of precision or roughly an 8 byte double precision value type).
2. The location of individual assemblies in the `/v2/smartassemblies` and `/v2/smartassemblies/{id}` endpoints in the World API, these are **relative to the center of the local star** and have a similar limited precision (i.e. 16-17 bits of precision).
3. The location of individual assemblies on-chain in the `Location` table, these are highly precise values absolute values as they are stored as `uint256` however they have had `1 << 256` added to them.
4. The `starmapcache.pickle` resource file contains the absolute positions of all solar systems in the map with a very high degree of precision, however as it exists within the `ResFiles` it needs to be decoded from Python Pickle format a process that must be repeated each time the star map is updated.
5. The `mapObjects.db` resource file contains the relative (to the star) position of celestial objects (Planets, Moons) again as it in the `ResFiles` and needs to be read using a SQLite database browser or by writing code to extract the rows from the tables.

## API Sources

The API sources are of low precision and depending on the endpoint are either absolute or relative to the star, historically low precision caused banding when zoomed in as the locations of stars are rounded to the nearest 100,000 km, the precision has been increased in recent cycles largely avoiding this problem. It is important to parse the values using a sufficiently high precision type as for example a `single` precision (4-byte) number will cut off a significant amount.

> [!IMPORTANT]
> Many of the the absolute numbers provided by CCP can not be accurately parsed by JavaScript's default JSON Parser as they exceed `MAX_SAFE_INTEGER` for the JavaScript engine. This can be circumvented by pre-processing the JSON file and matching any excessively long integers with a RegEx and surrounding them with strings then parsing the strings as `Big` or `BigInt`.

## On-chain Sources

The on-chain sources are the highest possible precision however depending on how you are using it may require transforming to recover the in-game values:

- if you are simply calculating the distance between two solar systems or gates then you can use them as is, that is because if you add a consistent offset to all components of a vector it is simply translates the coordinates in 3D space thus measuring the distance between the translated coordinates results in the same distance as the untranslated coordinates.
- if you are rendering these on a map, and especially combining them with data from other sources then you need to subtract `1 << 255` from each of the components of the vector.

> [!TIP]
> Be careful when calculating `1 << 255` as in some languages using a `1` will result in an implicit cast to a low precision type, for example `BigInteger.One << 255` results in `57896044618658097711785492504343953926634992332820282019728792003956564819968`  but `1 << 255` results in `-2,147,483,648`. This isn't a problem in languages such as Solidity where the native type is a Unsigned 256-bit integer.

## ResFile Sources

The ResFile sources are somewhat risky to use as CCP may without notice remove them or change the format and/or structure of the files. However if you are willing to do the extra work these give you the highest precision static locations in the world in either absolute (for solar systems) or relative (for celestials). You can use tools such as [Pickle](https://docs.python.org/3/library/pickle.html) and [DB Browser for SQLite](https://sqlitebrowser.org/) to inspect the contents of the files, be careful not to change them.
