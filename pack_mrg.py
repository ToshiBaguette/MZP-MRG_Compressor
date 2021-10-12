import os
import sys
import struct
import math
from pathlib import Path

OUTPUT_FILE_NAME = 'output_archive.mrg'

def parse_args():
    if len(sys.argv) > 1:
        args = Path(sys.argv[1])
        if args.is_dir(): return sys.argv[1]
        elif args.is_file(): return args.parent

    else: return Path('.')

def get_file_name_from_path(path):
    return path[path.rfind('/')+1:path.rfind('.')]


def write_file(output_file, input_dir):
    print('Writing Header...')
    output_file.write(b'mrgd00')  # File Signature

    # Next, we iterate over all of our files to get the number of files and their size, as well as their real path
    files = {  }
    nb_files = 0
    for file in os.listdir(input_dir):
        path_to_file = input_dir + f'/{file}'
        files[get_file_name_from_path(path_to_file)] = [os.path.getsize(path_to_file), path_to_file]
        nb_files += 1

    # We write the number of files in the archive
    output_file.write(struct.pack('<H', nb_files))

    # Before anything else, we have to order some files
    # allscr.nam, unknownX.mrg and unknownX2.mrg seems to HAVE TO be in first
    file_names = ['allscr', 'unknownX', 'unknownX2']
    for file in files:
        if file not in file_names:
            file_names.append(file)

    print('Writing Archive Header Entries...')
    # Now, we must write the archive entry descriptors
    # One for each file, with this type of data :
        # 2 first bytes - sector at which the file starts
        # 2 next bytes - offset, within sector, before the file starts
        # 2 next bytes - size of the file in sectors (counting offset within sector)
        # 2 next bytes - size of file in its last sector
    current_computed_offset = 0
    last_file_size_out_of_sector = 0
    file_offsets = {  }
    for file in file_names:
        sector_offset = current_computed_offset // 0x800
        offset = last_file_size_out_of_sector

        if sector_offset * 2048 + offset > current_computed_offset:
            # I don't clearly understand why, but it is possible for the current_compute_offset to be a little off
            # Maybe it's because of the sector_offset being an integer after the division ?
            # In any case, we have to put some offset before the file
            file_offsets[file] = (sector_offset * 2048 + offset) - current_computed_offset
            current_computed_offset = (sector_offset * 2048 + offset)

        sector_size_upper_boundary = ((offset + files[file][0]) // 0x800) + 1
        size = files[file][0] - (sector_size_upper_boundary - 1) // 0x20 * 0x10000 

        output_file.write(struct.pack('<H', sector_offset))
        output_file.write(struct.pack('<H', offset))
        output_file.write(struct.pack('<H', sector_size_upper_boundary))
        output_file.write(struct.pack('<H', size))

        current_computed_offset += files[file][0]
        last_file_size_out_of_sector = files[file][0] % 0x800

    print('Writing files...')
    # Finally, we can directly write the content of our files
    total_written = 0
    for file in file_names:
        print(f'Writing file {file}.')

        if file_offsets.get(file, False):
            output_file.write(b'\xFF' * file_offsets[file])

        input_file = open(files[file][1], 'rb')
        data = input_file.read()
        input_file.close()

        output_file.write(data)
        total_written += len(data)

    output_file.close()


def main():
    input_dir = parse_args()
    try:
        output_file = open(OUTPUT_FILE_NAME, 'wb')
    except Exception as e:
        print(e)
        sys.exit(1)

    print('Starting repack...')
    write_file(output_file, input_dir)
    print('Writing finished.')


if __name__ == '__main__':
    main()
