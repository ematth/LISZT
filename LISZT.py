import urwid, sys, sc3nb as scn

global PALETTE
PALETTE = [
    ('title', 'light cyan', '', 'bold'),
    ('header', 'light cyan', '', 'standout'),
    ('body', 'light gray', '', 'standout'),
    ('highlight', 'white', '', 'standout'),
    ('normal', 'black', 'light gray', 'standout'),
    ('comment', 'dark green', '', 'standout'),
    ('comment_focus', 'light green', '', 'standout')
]


class EditListWalker(urwid.SimpleFocusListWalker):
    def __init__(self, contents=None):
        # Initialize with empty list if no contents provided
        lines = contents if contents else [""]
        # Create Edit widgets for each line
        self.widgets = [urwid.AttrMap(
            urwid.Edit("", line),
            "comment",
            "comment_focus"
        ) if line.startswith('//') else urwid.AttrMap(
            urwid.Edit("", line),
            "body",
            "highlight"x
        ) for line in lines]
        
        super().__init__(self.widgets)
        
    def get_text(self):
        # Get text from all Edit widgets
        return [w.base_widget.get_edit_text() for w in self]
    
    def set_text(self, text):
        # Split text into lines and update widgets
        lines = text.split('\n')
        self.clear()
        for line in lines:
            self.append(urwid.AttrMap(
                urwid.Edit("", line),
                "default",
                "highlight",
            ))
    
    def get_focused_text(self):
        # Get text from currently focused widget
        widget, pos = self.get_focus()
        return widget.base_widget.get_edit_text()
    
    def highlight_focus(self):
        # Highlight current focus
        for w in self:
            w.set_attr_map({None: "default"})
        widget, pos = self.get_focus()
        widget.set_attr_map({None: "highlight"})
    
    def insert_line(self, pos, text=""):
        # Insert new line at specified position
        self.insert(pos, urwid.AttrMap(
            urwid.Edit("", text),
            "default",
            "highlight"
        ))

# Example usage:
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
        return sc
    
    def get_cursor(self):
        f = self.walker.get_focus()
        line, pos = f[-1], f[0].base_widget.edit_pos
        return (line, pos)

    def handle_input(self, key):

        if key in ('up', 'down', 'left', 'right'):
            """
            This case causes the editor to not crash
            when the user moves the cursor beyond the linebox. 
            """
            pass

        elif key in ('meta up', 'meta down', 'meta left', 'meta right'):
            if 'up' in key:
                self.walker.set_focus(0)
            elif 'down' in key:
                self.walker.set_focus(len(self.walker) - 1)
            else:
                line = self.walker.get_focus()[-1]
                if 'left' in key:
                    self.walker.widgets[line].base_widget.edit_pos = 0
                elif 'right' in key:
                    self.walker.widgets[line].base_widget.edit_pos = len(self.walker.widgets[line].base_widget.get_edit_text())

        elif key == 'backspace':
            # Key left on hold for text editing
            pass

        elif key == 'meta x':
            # Stop all sounds
            sc.server.free_all()
            self.set_footer('-> Free All')

        elif key == 'meta r':
            # Reboot SC
            sc.server.quit()
            sc.server.boot(console_logging=False, )
            self.set_footer('-> SC Rebooted!')

        elif key == 'meta s':
            with open(self.fname, 'w') as f:
                f.write('\n'.join(self.walker.get_text()))
            self.set_footer('File saved!')

        elif key == 'enter':
            pos = self.walker.get_focus()[1]
            self.walker.insert_line(pos + 1)

        elif key == 'meta c':
            self.set_footer(f'Cursor -> {self.get_cursor()}')

        elif key == 'meta h':
            # open popup box
            HELP = [
            "---------",
            "* LISZT *",
            "---------",
            "alt + q: Quit",
            "alt + s: Save",
            "alt + c: Cursor position",
            "alt + ,: Evaluate current line",
            "alt + .: Evaluate current block",
            "alt + r: Reboot SC",
            "alt + x: Free all sounds",
            "alt + h: Help",
            "---------",
            "Press alt + h to close this dialog."]
            if not self.help_dialog:
                self.help_dialog = True
                self.set_footer([i+'\n' for i in HELP])
            else:
                self.help_dialog = False
                self.set_footer('')
            
        elif key == 'meta ,':
            try:
                result = sc.lang.cmdg(self.walker.get_focused_text(), verbose=False)
                self.set_footer(f'-> {result}')
            except:
                self.set_footer('-> Error!')

        elif key == 'meta .':
            text = self.walker.get_text()
            cursor = self.get_cursor()
            idx = len(''.join(text[i] for i in range(cursor[0]))) + cursor[1]
            text2 = '\n'.join(text)
            string = "".join(text2[text2.rfind('(\n', 0, idx):text2.find('\n)', idx)+2])

            if '(\n' in string and '\n)' in string:
                try:
                    result = sc.lang.cmdg(string, verbose=False)
                    self.set_footer(f'-> "{result}"')
                except:
                    self.set_footer(text)
            else:
                self.set_footer(f'-> Error!')

        elif key == 'meta q': # 'esc' is mapped to any non-handled key?? WTF?
            raise urwid.ExitMainLoop()
        
        elif 'meta' in key:
            self.set_footer(f'-> {key} not found')
        
    def set_header(self, text):
        self.box.original_widget.header = urwid.AttrMap(urwid.Text(text), 'header')

    def set_footer(self, text):
        self.box.original_widget.footer = urwid.AttrMap(urwid.Text(text), 'header')

    def __init__(self, fname):
        self.fname = fname

        self.help_dialog = False

        # read lines from file
        if not self.fname.endswith('.scd'):
            self.fname += '.scd'
        try:
            with open(self.fname, 'r') as f:
                lines = f.readlines()
            lines = [line.replace('\t', '    ').replace('\n', '') for line in lines]
        except:
            print(f'File {self.fname} not found!')
            exit()
        
        # graphical stuff
        self.walker = EditListWalker(lines)
        self.listbox = urwid.ListBox(self.walker)
        self.footer = urwid.AttrMap(urwid.Text("----------------------------------------------------------\n LISZT: Lightweight Interface for SuperCollider Zen Tasks\n----------------------------------------------------------"), 'header')
        self.frame = urwid.Frame(body=self.listbox, footer=self.footer)
        self.box = urwid.LineBox(self.frame, title=self.fname, title_attr='title', title_align='left')

        print('starting up SC...')
        global sc
        sc = self.boot()
        print('startup completed!')
        
        loop = urwid.MainLoop(self.box, PALETTE, unhandled_input=self.handle_input, handle_mouse=True, pop_ups=True)
        loop.run()

if __name__ == "__main__":
    app = App(sys.argv[1])