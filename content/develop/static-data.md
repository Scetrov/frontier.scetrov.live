+++
date = '2025-06-29T13:10:00+01:00'
title = 'Static Data'
weight = 70
+++

Static Data is the data that is downloaded by the EVE Frontier Launcher and used by the client to display information in the game without downloading information from servers.

Inherently static data is unchanging, and is stored on-disk in an immutable form, however the use of that data will vary with patches.

> [!IMPORTANT]
> The availability and correctness of these files is entirely down to CCP, if they choose to remove something from static data, change the format or use it in a different way they will likely do so without informing the community. These are effectively internal data structures and not intended to be destructured and read.

## Finding Files

The easiest way to find files is through a text search of the contents of `C:\CCP\EVE Frontier` with Visual Studio Code or `grep`. There are a couple of key locations to extract filenames from.

The following contain server specific information, i.e. where `{server}` is `stillness` it's for the live server, if you have access to `{nova}` then you will also have these files too.

- `/index_{server}.txt`
- `/{server}/resfileindex.txt`
- `/{server}/resfileindex_prefetch.txt`

Each of these files are in the same format where each line is mad up of the following components.

```res
res:{logical_path},{file_path},{hash},{size},{unknown}
```

Where each line represents a file in the virtual filesystem:

- `{logical_path}` is the path of the original file and typically indicates the content and format.
- `{file_path}` is the actual path relative to `C:\CCP\EVE Frontier\ResFiles`
- `{hash}` and `{size}` represented attributes about the file use to verify integrity.
- I don't know what the last (`{unknown}`) part is.

## Formats

- **`.pickle`** - [Pickles](https://docs.python.org/3/library/pickle.html) are a Python-native data format that supports base Python types in addition to circular references and other Python features. They can be decoded using the Python library or 3rd Party Libraries for other languages such as [Razorvine.Pickle](https://www.nuget.org/packages/Razorvine.Pickle/).
- SQLite Databases (`.db` or `.sqlite`) - Simple relational databases in [SQLite format](https://sqlite.org/) can be accessed either through [a browser](https://sqlitebrowser.org/) and programmatically from any language.
- FSD Binaries - A custom binary format that can be decoded with [Phobos](https://github.com/pyfa-org/Phobos).
- `.schema` / `.static` Files - Contain a custom `.schema` with byte offsets for individual fields to be read from a `.static` file.
- Images and Models - In various formats including DirectX (`.dds`) and Portable Network Graphics (`.png`).

## Key Files

There are several key files included in the game client:

- `starmapcache.pickle` a Pickle file containing Regions, Constellations, Solar Systems and Jumps.
- `mapObjects.db` a SQLite database containing NPC Stations and Celestials (i.e. Planets and Moons).
- `localization_fsd_main.pickle` a Pickle file containing translation data, can be combined with `localization_fsd_en-us.pickle` to derive the English names for entities in the static data.
- `blueprintsbymaterialtypeids.pickle` to derive some Blueprint data.
