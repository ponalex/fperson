# coding: utf8
import curses
import sys
import json
from curses import wrapper
from auxiliary.dataproc import *
from auxiliary.flogger import create_logger


name1="win_prompt"
name2="sentences"
name3="data_list"

window_shape={
    "win_prompt":{
        "height":5,
        "width":58,
        "textspace":1,
        "x":1,"y":1,
        "titlename":"[Keys]",
        "title_x":2,
        "title_y":0,
        "colorscheme":1
        },
    "sentences":{
        "height":18,
        "width":58,
        "textspace":1,
        "x":1,"y":7,
        "titlename":"[text_on_side_panelext]",
        "title_x":2,
        "title_y":0,
        "colorscheme":1
        },
    "data_list":{
        "height":24,
        "width":20,
        "textspace":1,
        "x":60,"y":1,
        "titlename":"[Marked list]",
        "title_x":2,
        "title_y":0,
        "colorscheme":2
        }
    }


class CWindow:
    
    def __init__(self, config:dict, keypad=False, color_pair=None):
        self.height      = config["height"]
        self.width       = config["width"]
        self.x_position  = config["x"]
        self.y_position  = config["y"]
        self.titlename   = config["titlename"]
        self.x_title     = config["title_x"]
        self.y_title     = config["title_y"]
        self.textspace   = config["textspace"]
        if color_pair == None:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            self.colorscheme = curses.color_pair(1)
        else:
            self.colorscheme = color_pair
        self.window=curses.newwin(self.height, self.width, self.y_position, self.x_position)
#        self.window.box()
        self.window.bkgd(' ', self.colorscheme)
        self.window.keypad(keypad)


    def add_textblock(self, message:list, pointer=-1):
        self.window.clear()
        words=message.copy()
        line_length=self.width-2-2*self.textspace
        #logging.debug(line_length)
        initial_x=1+self.textspace
        initial_y=1
        counter=0
        m_line=""
        while len(words)>0:
            word=words.pop(0)
            if len(word)>line_length:
                #logging.debug("text_on_side_panelhe string is too long.")
                #logging.debug(len(word))
                #logging.debug(word)
                sys.exit()
            if (len(m_line)+1+len(word))>line_length:
                initial_x=1+self.textspace
                initial_y+=1
                m_line=word
            else:
                if len(m_line)==0:
                    m_line=word
                else:
                    m_line=m_line+" "+word
            if counter == pointer:
                self.window.addstr(initial_y, initial_x, word, curses.A_REVERSE)
            else:
                self.window.addstr(initial_y, initial_x, word)
            initial_x=initial_x+1+len(word)
            counter+=1

    def add_textgrid(self, message:list, pointer=(-1, -1), x_padding=1, y_padding=0, center=False):
        printed_text=list()
        if isinstance(message[0],str):
            n_col=1
            n_line=len(message)
            printed_text.append(message)
        else:
            n_col=len(message)
            n_line=len(message[0])
            printed_text=message.copy()
        max_length_line = (self.width - 2 - 2 * x_padding - x_padding*(n_col-1))//n_col 
        max_n_lines = self.height - 2 - 2 * y_padding - y_padding*(n_line-1)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!! Log here
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if max_n_lines <=0:
            sys.exit()
        x_coor=1+x_padding
        num_col=0
        shift=0
        self.window.clear()
        self.window.box()
        self.window.addstr(self.y_title, self.x_title, self.titlename )
        self.window.refresh()
        for column in printed_text:
            y_coor=1+y_padding
            num_row=0
            for line in column:
                if center:
                    shift = (max_length_line-len(line))//2
                if num_col==pointer[0] and num_row==pointer[1]:
                    self.window.addstr(y_coor, x_coor+shift, line, curses.A_REVERSE)
                else:
                    self.window.addstr(y_coor, x_coor+shift, line)
                #self.window.addstr(y_coor, x_coor, line)
                y_coor=y_coor+1+y_padding
                num_row+=1
            x_coor=x_coor  + x_padding + max_length_line
            num_col+=1
        self.window.refresh()

    def get_strkey(self, keypad=False)->str:
        self.window.refresh()
        self.window.keypad(keypad)
        key=self.window.getkey()
        self.window.refresh()
        return key

    def refresh_window(self):
        self.window.box()
        self.window.addstr(self.y_title, self.x_title, self.titlename )
        self.window.refresh()

# # ***********************************************************************
# data_text is the name of file which containes configuration of keys 
# and pointers to the segments and word in these segments
# marked _list is the list for marking which containes list of segments

def mainmenu(stdscr, data_text:str, text_list:list, loging_level='debug'):
    w_logger=create_logger(name="curses_logger", level=loging_level)
# Reading data from the structure file
    with open(data_text, "r") as structure_file:
        structure=json.load(structure_file)
    # Logging
    w_logger.debug(f"JSON data from file: {structure}")
    segment=structure["structure"]["sentence"]
    pointer=structure["structure"]["pointer"]
    result_file = structure["structure"]["data_list"]
    key_map = structure["structure"]["marking"]
# Key list is used to mark text (it contains key)
    key_list=key_map_to_list(key_map)
    key_list_str=list()
    for el in key_map.keys():
        key_list_str.append(str(el))
# Check if file exists if not then create empty one
    try: 
        file_marked_data=open(result_file, "r")
        file_marked_data.close()
    except FileNotFoundError:
        data_file=open(result_file, "x")
        data_file.close()
        w_logger.info(f"The file({result_file}) was not found, therefore was created.")

    # Dictionary containes lists
    # Add empty string at the begining data_from file
    # Before saving remove them
    data_from_file=read_marked_data(result_file)
    data_from_file[-1]=[["","<>"],["","<>"]]
    
    # Add here conditions: if segment is written in file use them 
    mainwindow=stdscr
    curses.curs_set(0)
    win_prompt=CWindow(window_shape[name1])
    win_text=CWindow(window_shape[name2])
    win_side=CWindow(window_shape[name3])
    win_text.refresh_window()

    key=""
    while key != "KEY_BACKSPACE":
# segment from text_list
        keys_from_file=list(data_from_file.keys())
        if segment not in keys_from_file:
            sentence=text_list[segment]
            #logging.debug("sentence")
            #logging.debug(sentence)
            word_list=sentence.split(" ")
            #logging.debug(f"word list(add to marked word list) {segment}")
            #logging.debug(word_list)
            marked_word_list = fill_default(word_list, key_map)
            data_from_file[segment]=marked_word_list
            #logging.debug(data_from_file[segment])
        else:
            marked_word_list=data_from_file[segment]
            word_list=(split_list(marked_word_list))[0]
# Fill the data from 
        side_text_segment=data_from_file[segment-1].copy()[-2:]
        #logging.debug(f"word list(take from marked word list) segment : {segment}")
        #logging.debug(side_text_segment)
        addlist(side_text_segment, marked_word_list)

        #addlist(side_text_segment, data_from_file[segment+1])
        text_on_side_panel = to1d_list(side_text_segment[pointer:pointer+5])
# Show the windows
# window side shows -2 : pointer : 2 with descriptions
        win_side.add_textgrid(text_on_side_panel,y_padding=1, pointer=(0, 4), center=True)
        win_prompt.add_textgrid(key_list,y_padding=0, pointer=(-1, -1), center=True)
        #logging.debug("---------")
        #logging.debug(word_list)
        win_text.add_textblock(word_list, pointer)
# ----------------------------------------------------------
        win_text.refresh_window()
        win_side.refresh_window()
        win_prompt.refresh_window()
        key = win_prompt.get_strkey(keypad=True)
        w_logger.debug(f"The {key} was pressed!")
        if key == "KEY_IC":
# Save file    
            data_to_save=data_from_file.copy()
            data_to_save.pop(-1)
            write_marked_data(result_file, data_to_save)
            w_logger.debug(f"Data was saved in file{result_file}")
        if key in key_list_str:
            marked_word_list[pointer][1]= "<"+key_map[key]+">"
        if key == "KEY_UP":
            if pointer<len(word_list)-1:
                pointer+=1
                continue
            else:
# Call another block from data
                if segment < len(text_list)-1:
                    segment+=1
                    pointer=0
                    w_logger.debug(f"The segment was set to {segment} and pointer was droped to zero")
                    continue
# current_segment = get_segment(data_from_file, segment ,key_map, text_list)
        if key == "KEY_DOWN":
            if pointer>0:
                pointer-=1
                continue
            else:
# Call another block from data
                if segment > 0:
                    segment-=1
# current_segment = get_segment(data_from_file, segment ,key_map, text_list)
                    pointer=len(data_from_file[segment])-1
                    w_logger.debug(f"The segment was droppped to zero and pointer was set to {pointer}")
                    continue
# Save file and exit
    w_logger.debug(f"The 'Backspace' was pressed. The length of the dictionary is {len(data_from_file)-1}")
    data_from_file.pop(-1)
    write_marked_data(result_file, data_from_file)
    curses.endwin()

