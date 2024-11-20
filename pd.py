import sigrokdecode as srd
from enum import IntEnum

class Ann(IntEnum):
    DATA = 0

class State(IntEnum):
    INIT = 0
    F0 = 1
    E0 = 2
    F0_E0 = 3

class Decoder(srd.Decoder):
    api_version = 3
    id = 'ibmpc_kbd'
    name = 'IBM keycode'
    longname = 'IBM PC AT/XT keyboard'
    desc = 'IBM PC AT/XT keyboard/mouse interface.'
    license = 'gplv2+'
    inputs = ['ibmpc_atxt']
    outputs = []
    tags = ['PC']
    options = (
        {'id': 'cs', 'desc': 'Code Set', 'default': 'cs2', 'values': ('cs1', 'cs2', 'cs3')},
    )
    annotations = (
        ('data', 'Data'),
    )
    annotation_rows = (
        ('code', 'Code', (0,)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = State.INIT

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def decode(self, ss, es, data):
        direction, byte = data

        if direction == 'H->D':
            self.put(ss, es, self.out_ann, [Ann.DATA, ['Cmd: %s' % self.to_cmd(byte), 'C', 'C']])
            self.state = State.INIT
            return;

        if self.state == State.INIT:
            if byte == 0xF0:
                self.state = State.F0
            elif byte == 0xE0:
                self.state = State.E0
            elif byte == 0xAA and self.options['cs'] in ['cs2', 'cs3']:
                self.state = State.INIT
                self.put(ss, es, self.out_ann, [Ann.DATA, ['BAT OK', 'OK', 'OK']])
            elif byte == 0xFC and self.options['cs'] in ['cs2', 'cs3']:
                self.state = State.INIT
                self.put(ss, es, self.out_ann, [Ann.DATA, ['BAT NG', 'NG', 'NG']])
            elif byte == 0xFA:
                self.state = State.INIT
                self.put(ss, es, self.out_ann, [Ann.DATA, ['Res: ACK', 'ACK', 'A']])
            else:
                self.state = State.INIT
                if self.options['cs'] == 'cs1':
                    if byte & 0x80:
                        self.put(ss, es, self.out_ann, [Ann.DATA,
                                ['↑: %s' % self.to_code(byte & 0x7F), '↑', '↑']])
                    else:
                        self.put(ss, es, self.out_ann, [Ann.DATA,
                                ['↓: %s' % self.to_code(byte & 0x7F), '↓', '↓']])
                else:
                    self.put(ss, es, self.out_ann, [Ann.DATA,
                            ['↓: %s' % self.to_code(byte), '↓', '↓']])

        elif self.state == State.F0:
            if byte == 0xE0:
                self.state = State.F0_E0
            else:
                self.state = State.INIT
                self.put(ss, es, self.out_ann, [Ann.DATA,
                        ['↑: %s' % self.to_code(byte), '↑', '↑']])

        elif self.state == State.E0:
            self.state = State.INIT
            self.put(ss, es, self.out_ann, [Ann.DATA,
                    ['↓: %s' % self.to_e0_code(byte), '↓', '↓']])

        elif self.state == State.F0_E0:
            self.state = State.INIT
            self.put(ss, es, self.out_ann, [Ann.DATA,
                    ['↑: %s' % self.to_e0_code(byte), '↑', '↑']])



    def to_code(self, byte):
        if self.options['cs'] == 'cs1':
            return self.cs1_to_str(byte)
        elif self.options['cs'] == 'cs2':
            return self.cs2_to_str(byte)
        elif self.options['cs'] == 'cs3':
            return self.cs3_to_str(byte)

    def to_e0_code(self, byte):
        if self.options['cs'] == 'cs1':
            return self.cs1_e0_to_str(byte)
        elif self.options['cs'] == 'cs2':
            return self.cs1_e0_to_str(byte)
        elif self.options['cs'] == 'cs3':
            return '???'

    def to_cmd(self, byte):
        try:
            return {
                0xED: 'Set Indicator',
                0xEE: 'Echo',
                0xF0: 'Select Scan Code',
                0xF2: 'Read ID',
                0xF4: 'Enable',
                0xF5: 'Default Disable',
                0xF6: 'Set Default',
                0xF7: 'Set All Keys - Typematic',
                0xF8: 'Set All Keys - Make/Break',
                0xF9: 'Set All Keys - Make',
                0xFA: 'Set All Keys - Typematic/Make/Break',
                0xFB: 'Set Key Type - Typematic',
                0xFC: 'Set Key Type - Make/Break',
                0xFD: 'Set Key Type - Make',
                0xFE: 'Resend',
                0xFF: 'Reset',
            }[byte]
        except:
            return '???'

    def cs3_to_str(self, byte):
        try:
            return {
                0x01:   'LGui',
                0x03:   'Vol Down',
                0x04:   'Vol Up',
                0x05:   'Mute',
                0x06:   'HENKAN',
                0x07:   'F1',
                0x08:   'F13',
                0x09:   'RGui',
                0x0A:   'App',
                0x0B:   'MHENKAN',
                0x0C:   'Pause',
                0x0D:   'Tab',
                0x0E:   '`',
                0x0F:   'F2',
                0x10:   'F14',
                0x11:   'Ctrl',
                0x12:   'LShift',
                0x13:   'ISO \\',
                0x14:   'CapsL',
                0x15:   'Q',
                0x16:   '1',
                0x17:   'F3',
                0x18:   'F15',
                0x19:   'Alt',
                0x1A:   'Z',
                0x1B:   'S',
                0x1C:   'A',
                0x1D:   'W',
                0x1E:   '2',
                0x1F:   'F4',
                0x20:   'F16',
                0x21:   'C',
                0x22:   'X',
                0x23:   'D',
                0x24:   'E',
                0x25:   '4',
                0x26:   '3',
                0x27:   'F5',
                0x28:   'F17',
                0x29:   'Space',
                0x2A:   'V',
                0x2B:   'F',
                0x2C:   'T',
                0x2D:   'R',
                0x2E:   '5',
                0x2F:   'F6',
                0x30:   'F18',
                0x31:   'N',
                0x32:   'B',
                0x33:   'H',
                0x34:   'G',
                0x35:   'Y',
                0x36:   '6',
                0x37:   'F7',
                0x38:   'F19',
                0x39:   'Alt',
                0x3A:   'M',
                0x3B:   'J',
                0x3C:   'U',
                0x3D:   '7',
                0x3E:   '8',
                0x3F:   'F8',
                0x40:   'F20',
                0x41:   ',',
                0x42:   'K',
                0x43:   'I',
                0x44:   'O',
                0x45:   '0',
                0x46:   '9',
                0x47:   'F9',
                0x48:   'F21',
                0x49:   ',',
                0x4A:   '/',
                0x4B:   'L',
                0x4C:   ';',
                0x4D:   'P',
                0x4E:   '-',
                0x4F:   'F10',
                0x50:   'F22',
                0x51:   'RO',
                0x52:   '\'',
                0x53:   'ISO #',
                0x54:   '[',
                0x55:   '=',
                0x56:   'F11',
                0x57:   'F23',
                0x58:   'Ctrl',
                0x59:   'RShift',
                0x5A:   'Ret',
                0x5B:   ']',
                0x5C:   '\\',
                0x5D:   'JPY',
                0x5E:   'F12',
                0x5F:   'F24',
                0x60:   'Down',
                0x61:   'Left',
                0x62:   'Home',
                0x63:   'Up',
                0x64:   'End',
                0x65:   'Insert',
                0x66:   'BS',
                0x67:   '/',
                0x68:   ',',
                0x69:   '1',
                0x6A:   'Rig',
                0x6B:   'P4',
                0x6C:   'P7',
                0x6D:   'Delete',
                0x6E:   'Page Up',
                0x6F:   'Page Down',
                0x70:   'P0',
                0x71:   'P.',
                0x72:   'P2',
                0x73:   'P5',
                0x74:   'P6',
                0x75:   'P8',
                0x76:   'Esc',
                0x77:   'Num Lock',
                0x78:   'P=',
                0x79:   'Enter',
                0x7A:   'P3',
                0x7B:   'P-',
                0x7C:   'P+',
                0x7D:   'P9',
                0x7E:   'Scroll Lock',
                0x83:   'Print Screen',
                0x84:   'P*',
                0x85:   'P,',
                0x86:   'P=',
                0x87:   'KANA',
            }[byte]
        except:
            return '???'

    def cs2_e0_to_str(self, byte):
        try:
            return {
                0x10:   'WWW Search',
                0x11:   'Right Alt',
                0x14:   'Right Control',
                0x15:   'Scan Previous Track',
                0x18:   'WWW Favorites',
                0x1F:   'Left GUI',
                0x20:   'WWW Refresh',
                0x21:   'Volume Down',
                0x23:   'Mute',
                0x27:   'Right GUI',
                0x28:   'WWW Stop',
                0x2B:   'Calculator',
                0x2F:   'App',
                0x30:   'WWW Forward',
                0x32:   'Volume Up',
                0x34:   'Play/ Pause',
                0x37:   'Keyboard Power',
                0x37:   'System Power',
                0x38:   'WWW Back',
                0x3A:   'WWW Home',
                0x3B:   'Stop',
                0x3F:   'System Sleep',
                0x40:   'My Computer',
                0x48:   'Mail',
                0x4A:   'Keypad /',
                0x4D:   'Scan Next Track',
                0x50:   'Media Select',
                0x5A:   'Keypad Enter',
                0x5E:   'System Wake',
                0x69:   'End',
                0x6B:   'Left Arrow',
                0x6C:   'Home',
                0x70:   'Insert',
                0x71:   'Delete',
                0x72:   'Down Arrow',
                0x74:   'Right Arrow',
                0x75:   'Up Arrow',
                0x7A:   'Page Down',
                0x7C:   'Print Screen',
                0x7D:   'Page Up',
                0x7E:   'Break (Ctrl-Pause)',
            }[byte]
        except:
            return '???'

    def cs2_to_str(self, byte):
        try:
            return {
                0x00:   'Overrun Error',
                0x01:   'F9',
                0x03:   'F5',
                0x04:   'F3',
                0x05:   'F1',
                0x06:   'F2',
                0x07:   'F12',
                0x08:   'F13',
                0x09:   'F10',
                0x0A:   'F8',
                0x0B:   'F6',
                0x0C:   'F4',
                0x0D:   'Tab',
                0x0E:   '` ~',
                0x0F:   'Keypad =',
                0x10:   'F14',
                0x11:   'Left Alt',
                0x12:   'Left Shift',
                0x13:   'Katakana/Hiragana',
                0x14:   'Left Control',
                0x15:   'q Q',
                0x16:   '1 !',
                0x18:   'F15',
                0x1A:   'z Z',
                0x1B:   's S',
                0x1C:   'a A',
                0x1D:   'w W',
                0x1E:   '2 @',
                0x20:   'F16',
                0x21:   'c C',
                0x22:   'x X',
                0x23:   'd D',
                0x24:   'e E',
                0x25:   '4 $',
                0x26:   '3 #',
                0x27:   'PC9800 Keypad ,',
                0x28:   'F17',
                0x29:   'Space',
                0x2A:   'v V',
                0x2B:   'f F',
                0x2C:   't T',
                0x2D:   'r R',
                0x2E:   '5 %',
                0x30:   'F18',
                0x31:   'n N',
                0x32:   'b B',
                0x33:   'h H',
                0x34:   'g G',
                0x35:   'y Y',
                0x36:   '6 ^',
                0x38:   'F19',
                0x3A:   'm M',
                0x3B:   'j J',
                0x3C:   'u U',
                0x3D:   '7 &',
                0x3E:   '8 *',
                0x40:   'F20',
                0x41:   ', <',
                0x42:   'k K',
                0x43:   'i I',
                0x44:   'o O',
                0x45:   '0 )',
                0x46:   '9 (',
                0x48:   'F21',
                0x49:   '. >',
                0x4A:   '/ ?',
                0x4B:   'l L',
                0x4C:   '; :',
                0x4D:   'p P',
                0x4E:   '- _',
                0x50:   'F22',
                0x51:   'ろ',
                0x52:   '\' "',
                0x54:   '[ {',
                0x55:   '= +',
                0x57:   'F23',
                0x58:   'Caps Lock',
                0x59:   'Right Shift',
                0x5A:   'Return',
                0x5B:   '] }',
                0x5D:   '\\',
                0x5F:   'F24',
                0x5F:   '半角/全角',
                0x61:   'Europe 2',
                0x62:   'ひらがな',
                0x63:   'かたかな',
                0x64:   '変換',
                0x66:   'Backspace',
                0x67:   '無変変',
                0x69:   'Keypad 1 End',
                0x6A:   '¥(Yen)',
                0x6B:   'Keypad 4 Left',
                0x6C:   'Keypad 7 Home',
                0x6D:   'Keypad ,',
                0x70:   'Keypad 0 Insert',
                0x71:   'Keypad . Delete',
                0x72:   'Keypad 2 Down',
                0x73:   'Keypad 5',
                0x74:   'Keypad 6 Right',
                0x75:   'Keypad 8 Up',
                0x76:   'Escape',
                0x77:   'Num Lock',
                0x78:   'F11',
                0x79:   'Keypad +',
                0x7A:   'Keypad 3 PageDn',
                0x7B:   'Keypad -',
                0x7C:   'Keypad *',
                0x7D:   'Keypad 9 PageUp',
                0x7E:   'Scroll Lock',
                0x83:   'F7',
                0xF1:   '한한(Hanja)',
                0xF2:   '한옝(Hangul/English)',
                0xFC:   'POST Fail',
            }[byte]
        except:
            return '???'

    def cs1_e0_to_str(self, byte):
        try:
            return {
                0x10: 'Scan Previous Track',
                0x19: 'Scan Next Track',
                0x1C: 'Keypad Enter',
                0x1D: 'Right Control',
                0x20: 'Mute',
                0x21: 'Calculator',
                0x22: 'Play/ Pause',
                0x24: 'Stop',
                0x2E: 'Volume Down',
                0x30: 'Volume Up',
                0x32: 'WWW Home',
                0x35: 'Keypad /',
                0x37: 'Prinen',
                0x38: 'Right Alt',
                0x46: 'Break (Ctrl-Pause)',
                0x47: 'Home',
                0x48: 'Up Arrow',
                0x49: 'Page Up',
                0x4B: 'Left Arrow',
                0x4D: 'Right Arrow',
                0x4F: 'End',
                0x50: 'Down Arrow',
                0x51: 'Page Down',
                0x52: 'Insert',
                0x53: 'Delete',
                0x5B: 'Left GUI',
                0x5C: 'Right GUI',
                0x5D: 'App',
                0x5E: 'Keyboard Power',
                0x5E: 'System Power',
                0x5F: 'System Sleep',
                0x63: 'System Wake',
                0x65: 'WWW Search',
                0x66: 'WWW Favorites',
                0x67: 'WWW Refresh',
                0x68: 'WWW Stop',
                0x69: 'WWW Forward',
                0x6A: 'WWW Back',
                0x6B: 'My Computer',
                0x6C: 'Mail',
                0x6D: 'Media Select',
            }[byte]
        except:
            return '???'

    def cs1_to_str(self, byte):
        try:
            return {
                0x01:   'Escape',
                0x02:   '1',
                0x03:   '2',
                0x04:   '3',
                0x05:   '4',
                0x06:   '5',
                0x07:   '6',
                0x08:   '7',
                0x09:   '8',
                0x0A:   '9',
                0x0B:   '0',
                0x0C:   '- _',
                0x0D:   '= +',
                0x0E:   'Backspace',
                0x0F:   'Tab',
                0x10:   'q',
                0x11:   'w',
                0x12:   'e',
                0x13:   'r',
                0x14:   't',
                0x15:   'y',
                0x16:   'u',
                0x17:   'i',
                0x18:   'o',
                0x19:   'p',
                0x1A:   '[ {',
                0x1B:   '] }',
                0x1C:   'Return',
                0x1D:   'Left Control',
                0x1E:   'a',
                0x1F:   's',
                0x20:   'd',
                0x21:   'f',
                0x22:   'g',
                0x23:   'h',
                0x24:   'j',
                0x25:   'k',
                0x26:   'l',
                0x27:   '; :',
                0x28:   '\' "',
                0x29:   '` ~',
                0x2A:   'Left Shift',
                0x2B:   '\\',
                0x2C:   'z',
                0x2D:   'x',
                0x2E:   'c',
                0x2F:   'v',
                0x30:   'b',
                0x31:   'n',
                0x32:   'm',
                0x33:   ', <',
                0x34:   '. >',
                0x35:   '/ ?',
                0x36:   'Right Shift',
                0x37:   'Keypad *',
                0x38:   'Left Alt',
                0x39:   'Space',
                0x3A:   'Caps Lock',
                0x3B:   'F1',
                0x3C:   'F2',
                0x3D:   'F3',
                0x3E:   'F4',
                0x3F:   'F5',
                0x40:   'F6',
                0x41:   'F7',
                0x42:   'F8',
                0x43:   'F9',
                0x44:   'F10',
                0x45:   'Num Lock',
                0x46:   'Scroll Lock',
                0x47:   'Keypad 7 Home',
                0x48:   'Keypad 8 Up',
                0x49:   'Keypad 9 PageUp',
                0x4A:   'Keypad -',
                0x4B:   'Keypad 4 Left',
                0x4C:   'Keypad 5',
                0x4D:   'Keypad 6 Right',
                0x4E:   'Keypad +',
                0x4F:   'Keypad 1 End',
                0x50:   'Keypad 2 Down',
                0x51:   'Keypad 3 PageDn',
                0x52:   'Keypad 0 Insert',
                0x53:   'Keypad . Delete',
                0x54:   'Unknown',
                0x55:   'Unknown',
                0x56:   'Europe 2',
                0x57:   'F11',
                0x58:   'F12',
                0x59:   'Keypad =',
                0x5A:   'Unknown',
                0x5B:   'Unknown',
                0x5C:   'PC9800 Keypad ,',
                0x5D:   'Unknown',
                0x5E:   'Unknown',
                0x5F:   'Unknown',
                0x60:   'Unknown',
                0x61:   'Unknown',
                0x62:   'Unknown',
                0x63:   'Unknown',
                0x64:   'F13',
                0x65:   'F14',
                0x66:   'F15',
                0x67:   'F16',
                0x68:   'F17',
                0x69:   'F18',
                0x6A:   'F19',
                0x6B:   'F20',
                0x6C:   'F21',
                0x6D:   'F22',
                0x6E:   'F23',
                0x6F:   'Unknown',
                0x70:   'Katakana/Hiragana',
                0x71:   'Unknown',
                0x72:   'Unknown',
                0x73:   'ろ (Ro)',
                0x74:   'Unknown',
                0x75:   'Unknown',
                0x76:   'F24 半角/全角',
                0x77:   'ひらがな',
                0x78:   'かたかな',
                0x79:   '変換',
                0x7A:   'Unknown',
                0x7B:   '無変変',
                0x7C:   'Unknown',
                0x7D:   '¥ (Yen)',
                0x7E:   'Keypad ,',
                0x7F:   'Unknown',
                0xAA:   'BAT OK',
                0xFC:   'BAT NG',
                0xFF:   'Overrun Error',
            }[byte]
        except:
            return '???'
