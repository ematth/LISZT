import numpy as np, urwid as u, sc3nb as scn
import sys, time, os

global PALETTE
PALETTE = [
    ('title', 'light cyan', '', 'bold'),
    ('body', 'black', 'light gray', 'standout'),
    ('header', 'light cyan', '', 'standout'),
    ('highlight', 'black', 'dark green', 'standout'),
    ('normal', 'black', 'light gray', 'standout'),
]

class newFrame(u.Frame):
    def __init__(self, body, footer):
        self.body = body
        return super().__init__(body=self.body, footer=footer)

    def set_header(self, text):
        self.header = u.AttrMap(u.Text(text), 'header')

    def set_footer(self, text):
        self.footer = u.AttrMap(u.Text(text), 'header')


class TextEditor(u.Edit):
    def keypress(self, size, key):
        if key == 'meta s':
            self.save(self.fname)
            FRAME.set_footer('File saved!')
            return None
        
        # cursor movement
        elif key == 'meta r':
            FRAME.set_footer('r')

        # cursor position
        elif key == 'meta c':
            text = "".join(self.get_text()[0])
            cursor = self.get_cursor_coords([len(text)])
            FRAME.set_footer(f'Cursor -> {cursor}')
        
        # single-line evaluation
        elif key == 'meta ,':
            text = self.get_text()[0]
            cursor = self.get_cursor_coords([len("".join(text))])
            # highlight the line to be run, sleep for 1 second, then remove highlight
            current_line = text.split('\n')[cursor[1]]


            try:
                result = sc.lang.cmdg(current_line, verbose=False)
                FRAME.set_footer(f'-> "{result}"')
            except:
                FRAME.set_footer(f'-> Error!')
            return None
        
        # multi-line evaluation
        elif key == 'meta .':
            # Fix this shitty code at some point!
            text = self.get_text()[0].split('\n')
            cursor = self.get_cursor_coords([len("".join(self.get_text()[0]))])
            idx = len(''.join([text[i] for i in range(cursor[1])])) + cursor[0]
            text= "".join(self.get_text()[0])
            string = "".join(text[text.rfind('(\n', 0, idx):text.find('\n)', idx)+2])
            # with open('temp.txt', 'w') as f:
            #     f.write(string)

            if '(\n' in string and '\n)' in string:
                try:
                    result = sc.lang.cmdg(string, verbose=False)
                    FRAME.set_footer(f'-> "{result}"')
                except:
                    FRAME.set_footer(text)
            else:
                FRAME.set_footer(f'-> Error!')
            return None
        
        return super().keypress(size, key)
    
    def save(self, fname):
        with open(fname, 'w') as f:
            f.write(self.edit_text)

    def __init__(self, lines, fname):
        self.fname = fname
        self.lines = lines
        super().__init__(edit_text=''.join(lines), multiline=True)
        self.set_edit_pos(0)
    

class App:

    def boot(self):
        sc = scn.startup(start_server=False)
        sc.lang.cmds(
            r"""
                "sc3nb - Registering OSC /return callback".postln;
                // NetAddr.useDoubles = true;
                r = r ? ();
                r.callback = { arg code, ip, port;
                    var result = code.interpret;
                    var addr = NetAddr.new(ip, port);
                    var prependSize = { arg elem;
                        if (elem.class == Array){
                            elem = [elem.size] ++ elem.collect(prependSize);
                        }{
                            elem;
                        };
                    };
                    var msgContent = prependSize.value(result);
                    addr.sendMsg(^replyAddress, msgContent);
                    result;  // result should be returned
                };""",
            pyvars={"replyAddress": "/return"},
        )
        sc.start_server()
        sc.server.volume = scn.amp_to_db(0.5)
        FRAME.set_footer(f'volume -> {str(scn.db_to_amp(sc.server.volume))}')
        return sc
    
    def unhandled_input(self, key):
        if key in ('esc', 'meta q'):
            sc.server.quit()
            raise u.ExitMainLoop()
        
        elif key == 'meta k':
            if scn.db_to_amp(sc.server.volume) > 0.0:
                sc.server.volume = scn.amp_to_db(round(scn.db_to_amp(sc.server.volume) - 0.05, 2))
            FRAME.set_footer(str(scn.db_to_amp(sc.server.volume)))

        elif key == 'meta l':
            if scn.db_to_amp(sc.server.volume) < 1.0:
                sc.server.volume = scn.amp_to_db(round(scn.db_to_amp(sc.server.volume) + 0.05), 2)
            FRAME.set_footer(str(scn.db_to_amp(sc.server.volume)))

        elif key == 'meta b':
            sc.server.blip()
            FRAME.set_footer('Blip!')

        elif key == 'meta m':
            if sc.server.muted:
                sc.server.unmute()
                FRAME.set_footer('Unmuted!')
            else:
                sc.server.mute()
                FRAME.set_footer('Muted!')

    def __init__(self, fname):
        with open(fname, 'r') as f:
            lines = f.readlines()
            
        lines = [line.replace('\t', '    ') for line in lines]

        lines = TextEditor(lines, fname)

        ftitle: str = fname.split('/')[-1]
        footer = u.AttrMap(u.Text("Use arrow keys to move, 'alt+q' or 'esc' to quit"), 'header')
        filler = u.LineBox(lines, 
            title=ftitle, 
            title_attr='title',
            title_align='left')
        
        # Global call to frame for updating interface
        global FRAME
        FRAME = newFrame(body=filler, footer=footer)

        # Global call to supercollider via sc.server or sc.lang
        print('starting up SC...')
        global sc
        sc = self.boot()
        print('startup completed!')

        loop = u.MainLoop(FRAME, palette=PALETTE, unhandled_input=self.unhandled_input, handle_mouse=True)
        loop.run()


if __name__ == "__main__":
    app = App(sys.argv[1])

