# from ntpath import join
import subprocess, sys, time, os, re
import xml.etree.ElementTree as ET
import hashlib
from appdirs import *
from datetime import datetime
import urllib.request
import tempfile
import shutil
import zipfile

appname = "redump-check"
appauthor = "com.github.vveird"

print("~~~ Redump Collection Verifier ~~~")
print("~~ Verifies any redump dat      ~~")
print("~~  files against a collection  ~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

ERR_LOG="redump-check.err"
STD_LOG="redump-check.log"

redump_source = { 
    'Acorn Archimedes':                                 {'dat': 'http://redump.org/datfile/arch/',    'cue': 'http://redump.org/cues/arch/'},
    'Apple Macintosh':                                  {'dat': 'http://redump.org/datfile/mac/',     'cue': 'http://redump.org/cues/mac/'},
    'Atari Jaguar CD Interactive Multimedia System':    {'dat': 'http://redump.org/datfile/ajcd/',    'cue': 'http://redump.org/cues/ajcd/'},
    'Bandai Pippin':                                    {'dat': 'http://redump.org/datfile/pippin/',  'cue': 'http://redump.org/cues/pippin/'},
    'Bandai Playdia Quick Interactive System':          {'dat': 'http://redump.org/datfile/qis/',     'cue': 'http://redump.org/cues/qis/'},
    'Commodore Amiga CD':                               {'dat': 'http://redump.org/datfile/acd/',     'cue': 'http://redump.org/cues/acd/'},
    'Commodore Amiga CD32':                             {'dat': 'http://redump.org/datfile/cd32/',    'cue': 'http://redump.org/cues/cd32/'},
    'Commodore Amiga CDTV':                             {'dat': 'http://redump.org/datfile/cdtv/',    'cue': 'http://redump.org/cues/cdtv/'},
    'Fujitsu FM Towns series':                          {'dat': 'http://redump.org/datfile/fmt/',     'cue': 'http://redump.org/cues/fmt/'},
    'funworld Photo Play':                              {'dat': 'http://redump.org/datfile/fpp/',     'cue': 'http://redump.org/cues/fpp/'},
    'IBM PC compatible':                                {'dat': 'http://redump.org/datfile/pc/',      'cue': 'http://redump.org/cues/pc/'},
    'Incredible Technologies Eagle':                    {'dat': 'http://redump.org/datfile/ite/',     'cue': 'http://redump.org/cues/ite/'},
    'Konami e-Amusement':                               {'dat': 'http://redump.org/datfile/kea/',     'cue': 'http://redump.org/cues/kea/'},
    'Konami FireBeat':                                  {'dat': 'http://redump.org/datfile/kfb/',     'cue': 'http://redump.org/cues/kfb/'},
    'Konami System GV':                                 {'dat': 'http://redump.org/datfile/ksgv/',    'cue': 'http://redump.org/cues/ksgv/'},
    'Mattel Fisher-Price iXL':                          {'dat': 'http://redump.org/datfile/ixl/',     'cue': 'http://redump.org/cues/ixl/'},
    'Mattel HyperScan':                                 {'dat': 'http://redump.org/datfile/hs/',      'cue': 'http://redump.org/cues/hs/'},
    'Memorex Visual Information System':                {'dat': 'http://redump.org/datfile/vis/',     'cue': 'http://redump.org/cues/vis/'},
    'Microsoft Xbox':                                   {'dat': 'http://redump.org/datfile/xbox/',    'cue': 'http://redump.org/cues/xbox/'},
    'Microsoft Xbox 360':                               {'dat': 'http://redump.org/datfile/xbox360/', 'cue': 'http://redump.org/cues/xbox360/'},
    'Namco · Sega · Nintendo Triforce':                 {'dat': 'http://redump.org/datfile/trf/',     'cue': 'http://redump.org/cues/trf/'},
    'Namco System 246':                                 {'dat': 'http://redump.org/datfile/ns246/',   'cue': 'http://redump.org/cues/ns246/'},
    'NEC PC Engine CD & TurboGrafx CD':                 {'dat': 'http://redump.org/datfile/pce/',     'cue': 'http://redump.org/cues/pce/'},
    'NEC PC-88 series':                                 {'dat': 'http://redump.org/datfile/pc-88/',   'cue': 'http://redump.org/cues/pc-88/'},
    'NEC PC-98 series':                                 {'dat': 'http://redump.org/datfile/pc-98/',   'cue': 'http://redump.org/cues/pc-98/'},
    'NEC PC-FX & PC-FXGA':                              {'dat': 'http://redump.org/datfile/pc-fx/',   'cue': 'http://redump.org/cues/pc-fx/'},
    'Neo Geo CD':                                       {'dat': 'http://redump.org/datfile/ngcd/',    'cue': 'http://redump.org/cues/ngcd/'},
    'Nintendo GameCube':                                {'dat': 'http://redump.org/datfile/gc/',      'cue': None},
    'Nintendo Wii':                                     {'dat': 'http://redump.org/datfile/wii/',     'cue': None},
    'Palm OS':                                          {'dat': 'http://redump.org/datfile/palm/',    'cue': 'http://redump.org/cues/palm/'},
    'Panasonic 3DO Interactive Multiplayer':            {'dat': 'http://redump.org/datfile/3do/',     'cue': 'http://redump.org/cues/3do/'},
    'Philips CD-i':                                     {'dat': 'http://redump.org/datfile/cdi/',     'cue': 'http://redump.org/cues/cdi/'},
    'Photo CD':                                         {'dat': 'http://redump.org/datfile/photo-cd/', 'cue': 'http://redump.org/cues/photo-cd/'},
    'PlayStation GameShark Updates':                    {'dat': 'http://redump.org/datfile/psxgs/',   'cue': 'http://redump.org/cues/psxgs/'},
    'Pocket PC':                                        {'dat': 'http://redump.org/datfile/ppc/',     'cue': 'http://redump.org/cues/ppc/'},
    'Sega Chihiro':                                     {'dat': 'http://redump.org/datfile/chihiro/', 'cue': 'http://redump.org/cues/chihiro/'},
    'Sega Dreamcast':                                   {'dat': 'http://redump.org/datfile/dc/',      'cue': 'http://redump.org/cues/dc/'},
    'Sega Lindbergh':                                   {'dat': 'http://redump.org/datfile/lindbergh/', 'cue': None},
    'Sega Mega CD & Sega CD':                           {'dat': 'http://redump.org/datfile/mcd/',     'cue': 'http://redump.org/cues/mcd/'},
    'Sega Naomi':                                       {'dat': 'http://redump.org/datfile/naomi/',   'cue': 'http://redump.org/cues/naomi/'},
    'Sega Naomi 2':                                     {'dat': 'http://redump.org/datfile/naomi2/',  'cue': 'http://redump.org/cues/naomi2/'},
    'Sega Prologue 21 Multimedia Karaoke System':       {'dat': 'http://redump.org/datfile/sp21/',    'cue': 'http://redump.org/cues/sp21/'},
    'Sega RingEdge':                                    {'dat': 'http://redump.org/datfile/sre/',     'cue': None},
    'Sega RingEdge 2':                                  {'dat': 'http://redump.org/datfile/sre2/',    'cue': None},
    'Sega Saturn':                                      {'dat': 'http://redump.org/datfile/ss/',      'cue': 'http://redump.org/cues/ss/'},
    'Sharp X68000':                                     {'dat': 'http://redump.org/datfile/x68k/',    'cue': 'http://redump.org/cues/x68k/'},
    'Sony PlayStation':                                 {'dat': 'http://redump.org/datfile/psx/',     'cue': 'http://redump.org/cues/psx/'},
    'Sony PlayStation 2':                               {'dat': 'http://redump.org/datfile/ps2/',     'cue': 'http://redump.org/cues/ps2/'},
    'Sony PlayStation 3':                               {'dat': 'http://redump.org/datfile/ps3/',     'cue': 'http://redump.org/cues/ps3/'},
    'Sony PlayStation Portable':                        {'dat': 'http://redump.org/datfile/psp/',     'cue': 'http://redump.org'},
    'TAB-Austria Quizard':                              {'dat': 'http://redump.org/datfile/quizard/', 'cue': 'http://redump.org/cues/quizard/'},
    'Tomy Kiss-Site':                                   {'dat': 'http://redump.org/datfile/ksite/',   'cue': 'http://redump.org/cues/ksite/'},
    'VM Labs NUON':                                     {'dat': 'http://redump.org/datfile/nuon/',    'cue': None},
    'VTech V.Flash & V.Smile Pro':                      {'dat': 'http://redump.org/datfile/vflash/',  'cue': 'http://redump.org/cues/vflash/'},
}

system_abbreviations = {
    'arch':      'Acorn Archimedes',
    'mac':       'Apple Macintosh',
    'ajcd':      'Atari Jaguar CD Interactive Multimedia System',
    'pippin':    'Bandai Pippin',
    'qis':       'Bandai Playdia Quick Interactive System',
    'acd':       'Commodore Amiga CD',
    'cd32':      'Commodore Amiga CD32',
    'cdtv':      'Commodore Amiga CDTV',
    'fmt':       'Fujitsu FM Towns series',
    'fpp':       'funworld Photo Play',
    'pc':        'IBM PC compatible',
    'ite':       'Incredible Technologies Eagle',
    'kea':       'Konami e-Amusement',
    'kfb':       'Konami FireBeat',
    'ksgv':      'Konami System GV',
    'ixl':       'Mattel Fisher-Price iXL',
    'hs':        'Mattel HyperScan',
    'vis':       'Memorex Visual Information System',
    'xbox':      'Microsoft Xbox',
    'xbox360':   'Microsoft Xbox 360',
    'trf':       'Namco · Sega · Nintendo Triforce',
    'ns246':     'Namco System 246',
    'pce':       'NEC PC Engine CD & TurboGrafx CD',
    'pc-88':     'NEC PC-88 series',
    'pc-98':     'NEC PC-98 series',
    'pc-fx':     'NEC PC-FX & PC-FXGA',
    'ngcd':      'Neo Geo CD',
    'gc':        'Nintendo GameCube',
    'wii':       'Nintendo Wii',
    'palm':      'Palm OS',
    '3do':       'Panasonic 3DO Interactive Multiplayer',
    'cdi':       'Philips CD-i',
    'photo-cd':  'Photo CD',
    'psxgs':     'PlayStation GameShark Updates',
    'ppc':       'Pocket PC',
    'chihiro':   'Sega Chihiro',
    'dc':        'Sega Dreamcast',
    'lindbergh': 'Sega Lindbergh',
    'mcd':       'Sega Mega CD & Sega CD',
    'naomi':     'Sega Naomi',
    'naomi2':    'Sega Naomi 2',
    'sp21':      'Sega Prologue 21 Multimedia Karaoke System',
    'sre':       'Sega RingEdge',
    'sre2':      'Sega RingEdge 2',
    'ss':        'Sega Saturn',
    'x68k':      'Sharp X68000',
    'psx':       'Sony PlayStation',
    'ps2':       'Sony PlayStation 2',
    'ps3':       'Sony PlayStation 3',
    'psp':       'Sony PlayStation Portable',
    'quizard':   'TAB-Austria Quizard',
    'ksite':     'Tomy Kiss-Site',
    'nuon':      'VM Labs NUON'
}

redump_dats = {}


USER_CONFIG_DIR = user_config_dir(user_data_dir(appname, appauthor))
print(USER_CONFIG_DIR)
TEMP_PATH = tempfile.mkdtemp()


progress = ['Ooo','oOo','ooO','oOo']
i = 0

if not os.path.exists(os.path.join(USER_CONFIG_DIR, 'dat')):
    os.makedirs(os.path.join(USER_CONFIG_DIR, 'dat'))
if not os.path.exists(os.path.join(USER_CONFIG_DIR, 'cue')):
    os.makedirs(os.path.join(USER_CONFIG_DIR, 'cue'))

def log(type, game, item, msg):
    type = type.upper().strip()
    log_file_name = ERR_LOG if type == 'ERROR' else STD_LOG
    with open(log_file_name, "a", encoding="utf-8") as log_file:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(' '.join([dt_string.ljust(25), type.ljust(10), game.ljust(45), item.ljust(10), msg, '\n']))

# Download redump.org datfiles and cuesheets
for system in redump_source:
    if not os.path.exists(os.path.join(USER_CONFIG_DIR, 'dat', system + ".dat")):
        print("~~ Downloading datfiles [{}]   ~~".format(progress[i]), end='\r', flush=True)
        i = i+1 if i+1 < len(progress) else 0
        #print('Downloading redump.org dat data for {}...'.format(system))
        log('INFO', 'CONFIG', 'DAT', 'Downloading redump.org dat data for {}...'.format(system))
        temp_dat_dir = os.path.join(TEMP_PATH, appname, 'dat', system)
        os.makedirs(temp_dat_dir)
        urllib.request.urlretrieve(redump_source[system]['dat'], os.path.join(temp_dat_dir, system + ".zip"))
        with zipfile.ZipFile(os.path.join(temp_dat_dir, system + ".zip"), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(temp_dat_dir))
        for (dirpath, dirnames, filenames) in os.walk(temp_dat_dir):
            for file_name in filenames:
                if file_name.endswith('.dat'):
                    os.rename(os.path.join(dirpath, file_name), os.path.join(USER_CONFIG_DIR, 'dat', system + ".dat"))
        shutil.rmtree(temp_dat_dir)
    if redump_source[system]['cue'] is not None and not os.path.exists(os.path.join(USER_CONFIG_DIR, 'cue', system)):
        print('Downloading redump.org cue data for {}...'.format(system))
        log('INFO', 'CONFIG', 'CUE', 'Downloading redump.org cue data for {}...'.format(system))
        temp_dat_dir = os.path.join(TEMP_PATH, appname, 'dat', system)
        os.makedirs(temp_dat_dir)
        urllib.request.urlretrieve(redump_source[system]['cue'], os.path.join(temp_dat_dir, system + ".zip"))
        os.makedirs(os.path.join(USER_CONFIG_DIR,  'cue', system))
        with zipfile.ZipFile(os.path.join(temp_dat_dir, system + ".zip"), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(os.path.join(USER_CONFIG_DIR,  'cue', system)))
        for (dirpath, dirnames, filenames) in os.walk(temp_dat_dir):
            for file_name in filenames:
                if file_name.endswith('.dat'):
                    os.rename(os.path.join(dirpath, file_name), os.path.join(USER_CONFIG_DIR, 'dat', system + ".dat"))
        shutil.rmtree(temp_dat_dir)

class RedumpRom:
    def __init__(self, name, crc=None, md5=None, sha1=None):
        self.name = name
        self.crc = crc
        self.md5 = md5
        self.sha1 = sha1
    def GetExt(self):
        filename, file_extension = os.path.splitext(self.name)
        return file_extension


class RedumpGame:
    def __init__(self, name, category=None, system=None):
        self.name = name
        self.category = category
        self.system = system
        self.complete = False
        self.filename_missmatched = False
        self.roms = {}
        self.filename_missmatched_sha1 = []
        self.matched_roms = {}
    def AddRom(self, rom):
        if isinstance(rom, RedumpRom) and rom.name not in self.roms:
            self.roms[rom.name] = rom
    


class RedumpDat:
    def __init__(self, name, internal_name=None, version=None, date=None, author=None, homepage=None, url=None):
        self.header = type('', (), {})()
        self.header.name = name
        self.header = type('', (), {})()
        self.header.name = name
        self.header.internal_name = internal_name if internal_name is not None else name
        self.header.version = version
        self.header.date = date
        self.header.author = author
        self.header.homepage = homepage
        self.header.url = url
        self.entries = {}
        self.allowed_extensions = []
        self.sha1_list = {}
    def AddRom(self, game_name, rom):
        if isinstance(rom, RedumpRom) and game_name in self.entries and rom.name not in self.entries[game_name].roms:
            ext = rom.GetExt()
            if ext is not None and ext.strip() != '' and ext not in self.allowed_extensions:
                self.allowed_extensions.append(ext)
            self.sha1_list[rom.sha1] = {self.header.internal_name, game_name, rom.name}
            self.entries[game_name].roms[rom.name] = rom
    def AddGame(self, game):
        if isinstance(game, RedumpGame) and game.name not in self.entries:
            self.entries[game.name] = game
            for rom in game.roms.values():
                ext = rom.GetExt()
                if ext is not None and ext.strip() != '' and ext not in self.allowed_extensions:
                    self.allowed_extensions.append(ext)
                self.sha1_list[rom.sha1] = {self.header.internal_name, game.name, rom.name}

def read_redump_file(dat_file, system_name=None):
    xml = root = ET.parse(dat_file).getroot()
    name = xml.find('header/name').text
    internal_name = system_name if system_name is not None else name
    version = xml.find('header/version').text
    date = xml.find('header/date').text
    author = xml.find('header/author').text
    homepage = xml.find('header/homepage').text
    url = xml.find('header/url').text
    dat_list = RedumpDat(name, internal_name, version, date, author, homepage, url)
    for game_entry in xml.findall('game'):
        name = game_entry.get('name')
        category = game_entry.get('category')
        system = dat_list.header.name
        game = RedumpGame(name, category, system)
        for rom_entry in game_entry.findall('rom'):
            name = rom_entry.get('name')
            size = rom_entry.get('size')
            crc = rom_entry.get('crc')
            md5 = rom_entry.get('md5')
            sha1 = rom_entry.get('sha1')
            rom = RedumpRom(name, crc, md5, sha1)
            game.AddRom(rom)
        dat_list.AddGame(game)
    dat_list.allowed_extensions = [ext for ext in dat_list.allowed_extensions]
    return dat_list, dat_list.allowed_extensions, dat_list.sha1_list

        
# Read redump.org dats
for (dirpath, dirnames, filenames) in os.walk(os.path.join(USER_CONFIG_DIR, 'dat')):
    for file_name in filenames:
        print("~~ Loading datfiles [{}]       ~~".format(progress[i]), end='\r', flush=True)
        i = i+1 if i+1 < len(progress) else 0
        system_name = file_name[:-4]
        abbrv=None
        abbrv=[abbreviations for abbreviations in system_abbreviations if system_abbreviations[abbreviations] == system_name]
        if system_name in redump_source and len(abbrv) == 1:
            dat_list, allowed_extensions, sha1_list = read_redump_file(os.path.join(dirpath, file_name), system_name)
            redump_dats[abbrv[0]] = {'dat_list': dat_list, 'allowed_extensions': allowed_extensions, 'sha1_list': sha1_list}

def get_game_by_name(game_name):
    return dat_list.get(game_name)

def get_game_by_hash(hash):
    if sha1_list.get(hash) is not None:
        return dat_list.get(sha1_list.get(hash)[0])
    else:
        return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ Creates a SHA1 and md5 hash 
# ~~ of a given file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Returns: md5 and sha1 hex encoded 
#          string
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def hash_file(file_name):
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    ttime = time.time()
    i=0
    print("Hashing file - {} [{}]".format(file_name, progress[i]), end='\r', flush=True)
    i = i+1 if i+1 < len(progress) else 0
    with open(file_name, 'rb') as f:
        while True:
            if time.time() - ttime > 1:
                print("Hashing file - {} [{}]".format(file_name, progress[i]), end='\r', flush=True)
                i = i+1 if i+1 < len(progress) else 0
                ttime = time.time()
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
    return (md5.hexdigest(), sha1.hexdigest())



def check_roms(roms_folder, dat_list, allowed_extensions, sha1_list, recursive = True):
    try:
        print("~~           Settings           ~~")
        print("~~ Using datfile for system: {}".format(dat_list.header.name))
        print("~~ ROM Folder: {}".format(roms_folder))
        print("~~ Allowed Extensions: {}".format(', '.join(allowed_extensions)))
        print("~~ Recursive: {}".format("Yes" if recursive else "No"))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        log('~~~~~~~~~~', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~', '~~~~~~~~~~', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        log('INFO', 'CONFIG', 'NONE', 'Using datfile for system: {}'.format(dat_list.header.name))
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
            (md5, sha1) = hash_file(rom_file)
            log('INFO', 'HASHING', 'ROM', 'Hashing file - {} - SHA1: {}'.format(rom_file, sha1))
            print('Hashing file - {}'.format(rom_file.ljust(LJUST)), end = '', flush=True)
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
        # Sort games by category
        categories_complete = {}
        for game in complete_games:
            if categories_complete.get(game.system) is None:
                categories_complete[game.system] = []
            categories_complete[game.system].append(game)
        pad_c = max([len(category) for category in categories_complete])
        # Show complete games by system
        for category in categories_complete:
            print('--- {}---'.format(category + " " + "".ljust(pad_c-len(category), '-')))
            for game in categories_complete[category]:
                print('  {} ({})'.format(game.name, 'Warning' if  game.filename_missmatched else 'Ok'))
                if game.filename_missmatched:
                    [print('   * Filename missmatch, DAT Entry: \'{}\', Local File: \'{}\''.format(game.game_rom_sha1[sha1].name, game.matched_rom_sha1[sha1])) for sha1 in game.filename_missmatched_sha1]
                sha1_complete += [rom.sha1 for rom in game.roms.values()]

        # Remove false positive incomplete entries from the complete list
        remove_incomplete_games = []
        for game in incomplete_games:
            duplicate_rom = [rom for rom in game.roms.values() if rom.sha1 in sha1_complete]
            if len(duplicate_rom) > 0:
                remove_incomplete_games.append(game)
        incomplete_games = [ game for game in incomplete_games if game not in remove_incomplete_games]

        if len(incomplete_games) > 0:
            categories_incomplete = {}
            for game in incomplete_games:
                if categories_incomplete.get(game.system) is None:
                    categories_incomplete[game.system] = []
                categories_incomplete[game.system].append(game)
            pad_i = max([len(category) for category in categories_incomplete])
            pad_i = pad_i if pad_i > pad_c else pad_c
            print()
            print('Incomplete Games (Might include false positives):')
            # Show incomplete games by system
            for category in categories_incomplete:
                print('--- {}---'.format(category + " " + "".ljust(pad_i-len(category), '-')))
                for game in categories_incomplete[category]:
                    print ('- {} ({})'.format(game.name, game.complete))
        print('----{}---'.format("".ljust(pad_c, '-')))
        return complete_games, incomplete_games
    except:
        raise

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ CMD Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check(roms_folder, dat_file):
    if roms_folder is None:
        print("~~~ ERROR ~~~")
        print("Please specifiy a folder to be checked")
        help(1)
    redump_lists = redump_dats
    check_cmd = {}
    if dat_file is not None and dat_file in system_abbreviations:
        check_cmd = redump_dats[dat_file]
        check_cmd['roms_folder'] = roms_folder
    elif dat_file is not None and dat_file.endswith('.cue'):
        dat_list, allowed_extensions, sha1_list = read_redump_file(dat_file)
        check_cmd = {'dat_list': dat_list, 'allowed_extensions': allowed_extensions, 'sha1_list': sha1_list, 'roms_folder': roms_folder}
    else:
        mixed = RedumpDat('Mixed','Mixed')
        for redump_dat in redump_dats.values():
            games = [game for game in redump_dat['dat_list'].entries.values()]
            for game in games:
                game.name += "({})".format(game.system)
                mixed.AddGame(game)
        check_cmd = {'dat_list': mixed, 'allowed_extensions': mixed.allowed_extensions, 'sha1_list': mixed.sha1_list, 'roms_folder': roms_folder}
    check_roms(**check_cmd)

def help(exit_val):
    print('~~~ Help  ~~~')
    print('Use one of the  following arguments to use this tool:')
    print('For checking a directory against all redump.org datfiles use the following command:')
    print()
    print('  redump check /path/to/collection')
    print()
    print('To check only for a specific system use either a system abbreviation (see redump list system) or provide an own dat file:')
    print()
    print('  redump check /path/to/collection psx')
    print('  redump check /path/to/collection /path/to/datfile/psx.dat')
    print()
    print('To list all available system use the following command:')
    print()
    print('  redump list system')
    print()
    print('To reorg your collection use the following command. The reorganization will')
    print()
    print('  a.) Put all rom files into their own subfolder using the games name')
    print('  b.) Rename all missnamed files to their correct names according to the dat file')
    print('  c.) Provide a cue file, if available, from the redump.org cuesheet')
    print('  Only complete Games will be reorganized. Use redump check first to see which')
    print('  games will be affected.')
    print()
    print('  redump reorg /path/to/collection [psx|/path/to/datfile/psx.dat]')
    print('')

    exit(exit_val if not isinstance(exit_val, str) else 1)

CMD = {'check': check, 'help': help}
CMD_ARGS = {
    'check': {'roms_folder': None, 'dat_file': None}, 
    'help': {'exit_val': 0}
}

if len(sys.argv) < 2:
        print("~~~ ERROR ~~~")
        print("Please specifiy a valid action to perform")
        help(1)
if sys.argv[1] not in CMD_ARGS:
        print("~~~ ERROR ~~~")
        print("Unknown command: {}".format(sys.argv[1]))
        help(1)

CMD_ARG = CMD_ARGS[sys.argv[1]]
aargv = sys.argv[2:]
i=0
for arg in CMD_ARG:
    if i < len(aargv):
        CMD_ARG[arg] = aargv[i]
        i+=1
CMD[sys.argv[1]](**CMD_ARG)
