import pdb
import curses
from curses import wrapper  
from curses.textpad import Textbox,rectangle

# Add here comments
# Document that
# Fix some problem related with readabilty of this text!

CH_CTRL_Q=b'^Q'
CH_CTRL_N=b'^N'
CH_CTRL_E=b'^E'
CH_CTRL_G=b'^G'
CH_ESC=b'^['
CH_UP=b'KEY_UP'
CH_DOWN=b'KEY_DOWN'
CH_LEFT=b'KEY_LEFT'
CH_RIGHT=b'KEY_RIGHT'
CH_ENTER=b'^J'
CH_DELETE=b'KEY_DC'
CH_BACKSPACE=b'KEY_BACKSPACE'

distance=34

help_menu={
    "Main":
        [["Save and close","CTRL+q"],
        [ "Create a new entry", "CTRL+n"],
        [ "Enter to enter mode","Enter"]],
    "Edit":
        [["Delete entry", "Delete"],
        [ "Select the entry", "Up, Down"], 
        [ "Edit the description", "Left"],
        [ "Edit the key", "Right"],
        [ "Quit edit mode", "CTRL+q"]],
    "Entering":
        [["Save description","Enter"],
        [ "Exit without saving", "CTRL+g"]],
    "Binding":
        [["Exit without saving", "CTRL+q"]]
}

default_entries={
    "0":"Other"
}

config={
    "window":{
        "height":18,
        "width":38,
        "textspace":2,
        "x":1,"y":1,
        "titlename":"[Entering : <Key>]",
        "title_x":2,
        "title_y":0,
        "colorscheme":0
    },
    "prompt":{
        "height":18,
        "width":40,
        "textspace":2,
        "x":40,"y":1,
        "titlename":"[Help]",
        "title_x":2,
        "title_y":0,
        "colorscheme":1
    },
    "textarea":{
        "height":3,
        "width":20,
        "x":2,
        "titlename":"[Entering]",
        "title_x":2,
        "title_y":0,
        "colorscheme":2
    },
    "bindwin":{
        "height":3,
        "width":20,
        "x":32,
        "titlename":"[Press key]",
        "title_x":2,
        "title_y":0,
        "colorscheme":2
    },
}

# ------------------------------------------------------

class Frame:

    def __init__(self, stdscr)->None:
        self.screen=stdscr
        self.screen.clear() 
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(True)
        curses.curs_set(0)
        self.color=dict()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.color[0]=curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        self.color[1]=curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.color[2]=curses.color_pair(3)
        self.window=dict()
        self.config=dict()

    def create_window(self, window_name:str, config:dict, default_y=1)->None:
        if "y" not in config: 
            corner_y=default_y
        else:
           corner_y=config["y"]
        self.window[window_name]=curses.newwin(config["height"], config["width"], corner_y, config["x"])
        self.config[window_name]=config
        self.window[window_name].bkgd(' ', self.color[config["colorscheme"]])

    def print_window(self, window_name:str, message:list, row_number=-1):
        line=1
        group=0
        window_width=self.config[window_name]["width"]
        for i in message:
            descr=i[0]
            keys="<"+i[1]+">"
            descr_len=len(descr)
            keys_len=len(keys)
            keys_y=window_width - 2 - keys_len
            if row_number >=0 and row_number==group:
                self.window[window_name].addstr(line, 2, descr, curses.A_REVERSE)
                self.window[window_name].addstr(line, keys_y, keys, curses.A_REVERSE)
            else:
                self.window[window_name].addstr(line, 2, descr)
                self.window[window_name].addstr(line, keys_y, keys)
            line+=1
            group+=1
        self.window[window_name].box()
        self.window[window_name].addstr(self.config[window_name]["title_y"], 
                self.config[window_name]["title_x"], self.config[window_name]["titlename"])
        self.window[window_name].refresh()

    def movewindow(self, window_name:str, x_position:int, y_position:int):
        self.window[window_name].mvwin(y_position, x_position)

    def get_text(self, window_name:str, shape:dict)->str:
        x_corner=shape["x"]  #+self.config[window_name].get("x")
        y_corner=shape["y"]  #+self.config[window_name].get("y")
        height=shape["h"]
        width=shape["w"]
        win=self.window[window_name].derwin(height, width, x_corner, y_corner)
        win.clear()
        win.refresh()
        box=Textbox(win)
        curses.echo()
        box.edit()
        text=box.gather()
        curses.noecho()
        return text.strip(" ")

    def get_keyname(self, window_name:str):
        self.window[window_name].clear()
        self.window[window_name].box()
        self.window[window_name].addstr(self.config[window_name]["title_y"], 
            self.config[window_name]["title_x"], self.config[window_name]["titlename"])
        self.window[window_name].addstr(1, 1, "Press the key!")
        self.window[window_name].refresh()
        self.window[window_name].keypad(True)
        key=self.window[window_name].getkey()
        str_key=str(key)
        self.window[window_name].addstr(1, 1, str_key)
        self.window[window_name].refresh()
        if not iskeyvalid(str_key):
            return ""
        return str_key

    def clear_window(self, window_name=None):
        if window_name is None:
            self.screen.clear()
        else:
            self.window[window_name].clear()

    def getkey(self, window_name:str):
        self.window[window_name].keypad(True)
        curses.raw()
        key=self.window[window_name].getch()
        curses.noraw()
        self.window[window_name].refresh()
        return key 
        
    def get_strkey(self, window_name:str):
        self.window[window_name].keypad(True)
        key=self.window[window_name].getkey()
        self.window[window_name].refresh()
        return key 

    def close(self)->None:
        curses.endwin()

def iskeyvalid(key_name)->bool:
    if len(key_name) != 1:
        return False
    if key_name == "" or key_name is None:
        return False
    return True

def external_func(stdscr, data_entries:dict):
    root_screen=Frame(stdscr)
    root_screen.create_window("Entering", config["textarea"])
    root_screen.create_window("Binding", config["bindwin"])
    root_screen.create_window("Main", config["window"])
    root_screen.create_window("Prompt", config["prompt"])
    State = "Main"
    shape_text={
        "x":1,
        "y":1,
        "h":1,
        "w":18
    }
    row_number=0
    while State != "Quit":
        root_screen.clear_window()
#----------------------------------------------
        if State == "Main":
            root_screen.print_window("Main", data_entries)
            root_screen.print_window("Prompt", help_menu[State])
            key=root_screen.getkey("Main")
            if curses.keyname(key) == CH_CTRL_Q :
                State= "Quit"
            if curses.keyname(key) == CH_ENTER:
                root_screen.clear_window()
                root_screen.clear_window("Prompt")
                State= "Edit"
            if curses.keyname(key) == CH_CTRL_N:
                root_screen.clear_window()
                root_screen.clear_window("Prompt")
                row_number=len(data_entries)
                data_entries.append(["",""])
                State="Entering"
            continue
#----------------------------------------------
        if State == "Edit":
            root_screen.print_window("Main", data_entries, row_number)
            root_screen.print_window("Prompt", help_menu[State])
            key=root_screen.getkey("Main")
            if curses.keyname(key) == CH_CTRL_Q :
                root_screen.clear_window()
                root_screen.clear_window("Prompt")
                State= "Main"
            if curses.keyname(key) == CH_UP:
                if row_number > 0:
                    row_number-=1
                State= "Edit"
            if curses.keyname(key) == CH_DOWN:
                if row_number < len(data_entries)-1:
                    row_number+=1
                State= "Edit"
            if curses.keyname(key) == CH_LEFT:
                root_screen.clear_window()
                root_screen.clear_window("Prompt")
                State= "Entering"
            if curses.keyname(key) == CH_RIGHT:
                root_screen.clear_window()
                root_screen.clear_window("Prompt")
                State="Binding"
            if curses.keyname(key) == CH_DELETE:
                deleted_el=row_number
                if row_number==len(data_entries)-1:
                    row_number-=1     
                data_entries.pop(deleted_el)
                root_screen.clear_window("Main")
                State= "Edit"
            continue
#----------------------------------------------
        if State == "Entering":
            root_screen.print_window("Prompt", help_menu["Entering"])
            root_screen.movewindow("Entering", 2, row_number+1)
            root_screen.print_window("Entering", [])
            text=root_screen.get_text("Entering", shape_text)
            if text != "":
                data_entries[row_number][0]=text
                root_screen.clear_window()
                root_screen.clear_window("Main")
                root_screen.clear_window("Prompt")
                State= "Edit"
                continue
            if curses.keyname(key) == CH_CTRL_Q :
                root_screen.clear_window()
                root_screen.clear_window("Prompt")
                State= "Edit"
            continue
#----------------------------------------------
        if State == "Binding":
            root_screen.print_window("Prompt", help_menu[State])
            root_screen.movewindow("Binding", config["window"]["width"] - config["textarea"]["width"], row_number+1)
            root_screen.print_window("Binding", [["Please press the key",""]])
            key=root_screen.get_keyname("Binding")
            if key != "":
                data_entries[row_number][1]=key
                root_screen.clear_window()
                root_screen.clear_window("Main")
                root_screen.clear_window("Prompt")
                State= "Edit"
            continue
#----------------------------------------------
    root_screen.close()


#  wrapper(external_func, data_entries)
