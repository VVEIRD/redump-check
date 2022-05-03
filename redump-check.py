# from ntpath import join
import subprocess, sys, time, os, re
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime

print("~~~ Redump Collection Verifier ~~~")
print("~~ Verifies any redump dat      ~~")
print("~~  files against a collection  ~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

ERR_LOG="redump-check.err"
STD_LOG="redump-check.log"

dat_list = type('', (), {})()

sha1_list = {}

def log(type, game, item, msg):
    type = type.upper().strip()
    log_file_name = ERR_LOG if type == 'ERROR' else STD_LOG
    with open(log_file_name, "a", encoding="utf-8") as log_file:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(' '.join([dt_string.ljust(25), type.ljust(10), game.ljust(45), item.ljust(10), msg, '\n']))

def read_redump_file(dat_file):
    xml = root = ET.parse(dat_file).getroot()
    allowed_extensions = {}
    dat_list.entries = {}
    dat_list.header = type('', (), {})()
    dat_list.header.name = xml.find('header/name').text
    dat_list.header.version = xml.find('header/version').text
    dat_list.header.date = xml.find('header/date').text
    dat_list.header.author = xml.find('header/author').text
    dat_list.header.homepage = xml.find('header/homepage').text
    dat_list.header.url = xml.find('header/url').text
    print(dat_list.header.name)
    print(dat_list.header.version)
    sha1_list = {}
    for game_entry in xml.findall('game'):
        game = type('', (), {})()
        game.name = game_entry.get('name')
        game.category = game_entry.get('category')
        game.system = dat_list.header.name
        game.roms = {}
        # Check specific data
        game.complete = False
        game.filename_missmatched = False
        game.filename_missmatched_sha1 = []
        game.matched_roms = {}
        for rom_entry in game_entry.findall('rom'):
            rom = type('', (), {})()
            rom.name = rom_entry.get('name')
            filename, file_extension = os.path.splitext(rom.name)
            if file_extension != '' and allowed_extensions.get(file_extension) is None:
                allowed_extensions[file_extension] = file_extension
            rom.size = rom_entry.get('size')
            rom.crc = rom_entry.get('crc')
            rom.md5 = rom_entry.get('md5')
            rom.sha1 = rom_entry.get('sha1')
            sha1_list[rom_entry.get('sha1')] = [dat_list.header.name, game.name, rom.name]
            game.roms[rom.name] = rom
        dat_list.entries[game.name] = game
    allowed_extensions = [ext for ext in allowed_extensions]
    return dat_list, allowed_extensions, sha1_list

def get_game_by_name(game_name):
    return dat_list.get(game_name)

def get_game_by_hash(hash):
    if sha1_list.get(hash) is not None:
        return dat_list.get(sha1_list.get(hash)[0])
    else:
        return None

def hash_file(file_name):
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    with open(file_name, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
    return (md5.hexdigest(), sha1.hexdigest())

try:
    #print('Number of arguments:', len(sys.argv), 'arguments.')
    #print('Argument List:', str(sys.argv))
    if len(sys.argv) < 3:
        print("~~~ ERROR ~~~")
        print("First argument must be the folder to the collection")
        print("Second argument must be the DAT fril from redump.org")
        print("Example:")
        print("  redump-check D:\\psx\\roms \"D:\\psx\\Sony - PlayStation - Datfile (10649) (2022-05-02 09-44-32).dat\"")
        print("To disable recursive file traversal, add --no-recursive at the end:")
        print("  redump-check D:\\psx\\roms \"D:\\psx\\Sony - PlayStation - Datfile (10649) (2022-05-02 09-44-32).dat\" --no-recursive")
        exit(1)
    roms_folder = sys.argv[1]
    dat_file = sys.argv[2]
    recursive = False if len(sys.argv) >= 4 and sys.argv[3] == "--no-recursive" else True
    dat_list, allowed_extensions, sha1_list = read_redump_file(dat_file)
    print("~~           Settings           ~~")
    print("~~ DAT File: {}".format(dat_file))
    print("~~ ROM Folder: {}".format(roms_folder))
    print("~~ Allowed Extensions: {}".format(', '.join(allowed_extensions)))
    print("~~ Recursive: {}".format("Yes" if recursive else "No"))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    log('~~~~~~~~~~', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~', '~~~~~~~~~~', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    log('INFO', 'CONFIG', 'NONE', 'Dat File: {}'.format(dat_file))
    log('INFO', 'CONFIG', 'NONE', 'ROM Folder: {}'.format(roms_folder))
    log('INFO', 'CONFIG', 'NONE', 'Allowed Extensions: {}'.format(', '.join(allowed_extensions)))
    log('INFO', 'CONFIG', 'NONE', 'Recursive: {}'.format("Yes" if recursive else "No"))
    rom_list = []
    sha1_rom_list = {}
    # Find all rom files
    for (dirpath, dirnames, filenames) in os.walk(roms_folder):
        if recursive or dirpath == roms_folder:
            for file in filenames:
                if file[-4:] in allowed_extensions:
                    game_name = re.sub(' \(Track [0-9]{1,3}\)', '', file)
                    rom_list.append(os.path.join(dirpath, file))


    # Check file hashes of known files
    print("Checking Files:")
    LJUST = max([len(a) for a in rom_list])
    # Hashing Files
    for rom_file in rom_list:
        print('Hashing file - {}'.format(rom_file.ljust(LJUST)), end = '', flush=True)
        (md5, sha1) = hash_file(rom_file)
        log('INFO', 'HASHING', 'ROM', 'Hashing file - {} - SHA1: {}'.format(rom_file, sha1))
        print(' - SHA1: {}'.format(sha1))
        sha1_rom_list[rom_file] = sha1

    # Match files to games
    matched_games = []
    for game_name in dat_list.entries:
        game = dat_list.entries[game_name]
        # List of sha1 hahs of the roms
        game.game_rom_sha1 = {rom.sha1: rom for rom in game.roms.values()}
        # Match hashed files to list of game roms
        game.matched_roms = {file: sha1_rom_list[file] for file in sha1_rom_list if sha1_rom_list[file] in game.game_rom_sha1}
        game.matched_rom_sha1 = {sha1_rom_list[file]: file for file in sha1_rom_list if sha1_rom_list[file] in game.game_rom_sha1}
        # For one or mor hits
        if len(game.matched_roms) > 0:
            game.complete = True if len(game.matched_roms) == len(game.roms) else False
            matched_games.append(game)
        # Find File Name Missmatch
        for sha1 in game.matched_rom_sha1:
            if game.game_rom_sha1[sha1].name != os.path.basename(game.matched_rom_sha1[sha1]):
                game.filename_missmatched = True
                game.filename_missmatched_sha1.append(sha1)
                

    complete_games = [game for game in matched_games if game.complete]
    incomplete_games = [game for game in matched_games if not game.complete]

    print()
    print('Complete Games:')

    sha1_complete = []

    for game in complete_games:
        print ('- {} ({})'.format(game.name, 'Warning' if  game.filename_missmatched else 'Ok'))
        if game.filename_missmatched:
            [print('   * Filename Missmatched, DAT Entry: \'{}\', Local File: \'{}\''.format(game.game_rom_sha1[sha1].name, game.matched_rom_sha1[sha1])) for sha1 in game.filename_missmatched_sha1]
        sha1_complete += [rom.sha1 for rom in game.roms.values()]

    # Remove false positive incomplete entries from the complete list
    remove_incomplete_games = []
    for game in incomplete_games:
        duplicate_rom = [rom for rom in game.roms.values() if rom.sha1 in sha1_complete]
        if len(duplicate_rom) > 0:
            remove_incomplete_games.append(game)
    incomplete_games = [ game for game in incomplete_games if game not in remove_incomplete_games]

    if len(incomplete_games) > 0:
        print()
        print('Incomplete Games (Might include false positives):')
        for game in incomplete_games:
            print ('- {} ({})'.format(game.name, game.complete))

except:
    raise
