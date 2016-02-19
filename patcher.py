#! coding: utf8

import sys, os, time, re
from binascii import hexlify, unhexlify
__author__ = 'Icyblade'
__credits__ = ['AK-48', 'FrostBlade', 'Icyblade']
__maintainer__ = 'Icyblade'

patcher = {
    'x86': {
        'addon': (
            '837E2801750B8B4510C70005000000EBAB',
            '837E2801EB0B8B4510C70005000000EBAB',
            '837E2801EB0B8B4510C70005000000EBAB',
        ),
        'green': (
            'F64518018B35(?P<a>[0-9A-F]{6})0159648B0D2C0000008945148955FC8B34B1C786040000000200000074(?P<b>[0-9A-F]{2})',
            'F64518008B35\g<a>0159648B0D2C0000008945148955FC8B34B1C786040000000200000075\g<b>',
            'F64518008B35(?P<a>[0-9A-F]{6})0159648B0D2C0000008945148955FC8B34B1C786040000000200000075(?P<b>[0-9A-F]{6})'
        ),
        'crash1': (
            '558BEC83EC24833(?P<a>[0-9A-F]{8})100740D80',
            '33C0C383EC24833\g<a>100740D80',
            '33C0C383EC24833(?P<a>[0-9A-F]{8})100740D80'
        ),
    },
    'x64': {
        'addon': (
            '83F8017516C745000500000032C0488B5C24604883C4405F5E5DC3',
            '83F801EB16C745000500000032C0488B5C24604883C4405F5E5DC3',
            '83F801EB16C745000500000032C0488B5C24604883C4405F5E5DC3'
        ),
        'green': (
            'F6842480000000018B15(?P<a>[0-9A-F]{6})0165488B0C255800000041BD08000000488BE8488B3CD141C744(?P<b>[0-9A-F]{2})00020000000F84(?P<c>[0-9A-F]{2})000000',
            'F6842480000000008B15\g<a>0165488B0C255800000041BD08000000488BE8488B3CD141C744\g<b>00020000000F85\g<c>000000',
            'F6842480000000008B15(?P<a>[0-9A-F]{6})0165488B0C255800000041BD08000000488BE8488B3CD141C744(?P<b>[0-9A-F]{2})00020000000F85(?P<c>[0-9A-F]{2})000000',
        ),
        'crash1': (
            '4C894C242055415641574881EC(?P<a>[0-9A-F]{2})010000',
            '33C0C3242055415641574881EC\g<a>010000',
            '33C0C3242055415641574881EC(?P<a>[0-9A-F]{2})010000',
        ),
    },
}

def patch(filename):
    fi = open(filename, 'rb')
    fi_cont = hexlify(fi.read()).upper()
    fi.close()
    
    # backup
    if not os.path.exists('./backup/'):
        os.mkdir('./backup/')
    fb = open('./backup/%s.%s' % (filename, int(time.time())), 'wb')
    fb.write(unhexlify(fi_cont))
    fb.close()
    
    # determine architecture
    offset = fi_cont.find('5045')
    if offset:
        magic = fi_cont[offset:offset+12]
        if magic == '504500004C01':
            type = 'x86'
        elif magic == '504500006486':
            type = 'x64'
        else:
            print('Cannot determine architecture, magic: %s' % magic)
            return
    print('Processing WowB%s.exe ...' % ('-64' if type == 'x64' else ''))
    
    # patch
    for target, patch in patcher[type].iteritems():
        print('- Patching %s...' % target),
        if re.findall(patch[0], fi_cont):
            print('Found, patching')
            fi_cont = re.sub(patch[0], patch[1], fi_cont)
        elif re.findall(patch[2], fi_cont):
            print('Already patched')
        else:
            print('CRITICAL, pattern not found. Does Blizzard make some changes?')
        
    # output
    fo = open(filename, 'wb')
    fo.write(unhexlify(fi_cont))
    fo.close()

def main(argv):
    try:
        input_filename = argv[1]
        if os.path.isfile(input_filename):
            patch(input_filename)
        else:
            print('File not found')
    except IndexError:
        patch('WowB.exe')
        patch('WowB-64.exe')
    print
    raw_input('Press any key to exit...')

def string_to_hex(string, delimiter=':'):
    return delimiter.join('{:02x}'.format(ord(c)) for c in string).upper()

if __name__ == '__main__':
    main(sys.argv)
