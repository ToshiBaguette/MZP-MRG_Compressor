# MZP File Format

## Introduction

MZP files are archives that was mostly used in PlayStation 2 / PSP-era video games a very little subset of titles.

I personally found it used in Tsukihime -A Piece of Blue Glass Moon- to archive everything related to the script of the game in a single file.

The file extension of MZP files can be `.mzp`, but it also can be `.mrg`. In this case, the file must not be confused with real MRG Files (those are accompanied by `.hed` and `.nam` files).

## Inner Working

A MZP archive consists of a header (representing file signature, and how the archive is partitioned), and the files themselves.

The file do not count size of files in bytes, but in sectors. A sector is a group of 2048 bytes, each sector is 2 KB.

### File Header

Every thing in the header is saved in little-endian, to say, the first 4 bits of a byte are in first position, and then come the 4 last bits.
Thus `0x6D` is, in little-endian, the equivalent of `0xD6` in big-endian.

```
1. Signature of MZP archive "mrgd00" (the bytes 0x6D 0x72 0x67 0x64 0x30 0x30) - 6 Bytes
2. Number of files in the archive - 2 Bytes
```

Then, for each file in the archive, there will be the next 8 bytes repeated :
```
1. Offset (in sectors) of the file within the archive - 2 Bytes
2. Offset of the file within the starting sector (in bytes) - 2 Bytes
3. Size of the file (in sectors) - 2 Bytes
4. Size of the file withing the last sector (in bytes) - 2 Bytes
```
Header of the archive does not count as offset.

### File Content

Next, every file is packed one next to another. It is possible to add some offset between files within the archive, as long as this offset taken in account in the header.

The files can be saved in big-endian, it doesn't really matter, you should just make sure of the endianness of the target computer that will read the archive and how it wants to read the bytes.


# Tool

In this repo, there is a single Python file named `pack_mrg.py`. This script is made to create a mzp file archive, with every file in a directory.

## Usage

```
py pack_mrg.py /path/to/directory
```
This will then output a file name `output_archive.mrg`, containing every file in the specified directory.

The archive can then be read with a tool like `unpack_allsrc.py` available in the repo [PS-HuneX_Tools](https://github.com/Hintay/PS-HuneX_Tools)

# Credit

I based my work on the first explaination available from [Waku_Waku](https://github.com/mchubby/psp-ayakashibito_tools/blob/master/specs/mzp_format.md). Having some trouble really understanding some points, I thought of reverse-engeneering the file format myself, and create an archiving tool to put in practice what I learned. Then, I decided to make a new explanation on the file format myself.
