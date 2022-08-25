#!/bin/python3
import sys
import getopt
import os
import json
import logging
from  auxiliary import maingui
import auxiliary.flogger
from auxiliary import dataproc as dp
from auxiliary.pycurses import wrapper,external_func

command_line="s:d:c:al:v:h"


config={"-s":"",
        "-v":"error",
        "-d":"structure.json",
        "-a":False,
        "-l":"ERROR",
        "-c":"import_word.conf"
}

# The size of text block (maximal value)
text_window={
        "width":54,
        "height":16
        }

def getconfig(command_list: list, conf: dict)->None:
    res=list()
    try:
        option, args = getopt.getopt(command_list, command_line)   
    except getopt.GetoptError:
        # log ERROR here
        logger.info(f"getconfig: {command_list}")
        print("There is an error in the command!")
        print("Please use -h for help")
        exit()
    if len(args)>1:
        # log ERROR here
        logger.info(f"Wrong parameters: {args}")
        print("Wrong parameters of argument!") 
        exit()
    if len(args)==1:
        logger.debug(f"File for input: {args}")
        conf['-s']=args 
    # log debug here
    logger.debug(f"Options: {option}")
    for c in option:
        if c[0]=='-h':
            print("Use -s to point the source file")     
            print("The key -d point to the file where is stored vocabulary")
            print("The key -a is used to append data to the existing file")
            exit()
        else:
# -s passing key with file name (raw text)
            if c[0]=='-s':
                conf['-s']=c[1]
# -d pass destianation file for storing data and its config
            if c[0]=='-d':
                conf['-d']=c[1]
# -c pass file name with config(default value "import_word.json")
            if c[0]=='-c':
                conf['-c']=c[1]
            if c[0]=='-v':
                possible_value=['debug', 'info', 'warning', 'error', 'critical']
                if c[1] in possible_value:
                    conf['-v']=c[1]
                else:
                    print("Please use one of this value with key \'-v\':")
                    print("\'debug\',\'info\',\'warning\',\'error\',\'critical\'")
                    exit()
# -a pass key for creating new destiantion file(default value - False)
            if c[0]=='-a':
                conf['-a']=True
            
# ------------------------------------------------

def create_json(filename:str):
    json_struct={
        "structure":{
            "pointer":0,
            "sentence":0,
            "marking": dict()
            }
    }
    head_filename=filename+".list"
    logger.debug(f"File for saving data: {head_filename}")
    json_struct["structure"]["data_list"]=head_filename
    marking=[["Other", "0"]]
    wrapper(external_func, marking)
    temp_dict=dict()
    for i in marking:
        temp_dict[i[1]]=i[0]
    json_struct["structure"]["marking"]=temp_dict
    logger.debug(f"JSON structure {json_struct}")
    with open(filename, "w") as f:
        json.dump(json_struct, f)

# ------------------------------------------------

def checkconfig(conf: dict)->bool:
    res= True
# Checking parameters passed with -a : boolean
    if type(conf['-a'])!=bool:
        # log this with debug
        logger.debug(f"checkconfig argument {conf}")
        print("""Parameter 'create new structure' should be boolean""")
        return False

# Checking parameters passed with -s : correct filename
    if conf['-s']!='':
        if not os.path.isfile(conf['-s']):
            # log this with debug
            logger.debug(f"Configuration does not containe a filename {conf.get('-s')}")
            print(""" The parameter -s should containe neme of existing file or be empty!""")
            return False
# Checking parameters passed with -d : correct filename
    if os.path.isfile(conf['-d']):
        # log this with debug
        logger.debug(f"Configuration file 'conf[\'-d\']' {conf.get('-d')}")
        # print(os.path.isfile(conf['-d']))
        if conf['-a']:
            # log this with debug
            logger.debug("Such file already exists!")
            print("Such file already exists!")
            return False 
        return True
    else:
        if not conf['-a']:
            # log this with debug
            logger.debug("Such file already exists!")
            print("Such file already exists!")
            print("There is no such file!")
            return False
        else:
           create_json(conf['-d'])            
            
    return res

# ------------------------------------------------

if __name__=="__main__":
    command_list=sys.argv[1:]
    argv=sys.argv[1:]
    # log argv with info
    logger=auxiliary.flogger.create_logger(name="default_logger", level=config['-v'])
    getconfig(command_list, config)
    text=list()
    text_list=list()
    if not checkconfig(config):
        # log this with debug 
        print("Wrong configuration!")
        exit()
    if config['-s']!='':
        with open(config['-s'], '+r') as f:
            temp=f.readlines()
        text_list=temp.copy()
    else:
        for line in sys.stdin:
            text_list.append(line.strip('\n'))
    logger.debug(f"The length of sentence is {len(text_list)}")
    raw_sentences=list()
    for line in text_list:
        temp_list=dp.getsentences(line)
        for el in temp_list:
            raw_sentences.append(el)
    width=int(text_window['width'])
    height=int(text_window['height'])
    
    for i in reversed(range(len(raw_sentences))):
        temp_list=list()
        sent=raw_sentences.pop(i)
        temp_list=dp.normsentence(sent, width, height)
        # log this with info
        for l in range(len(temp_list)):
           raw_sentences.insert(i+l,temp_list[l])
    wrapper(auxiliary.maingui.mainmenu, config["-d"] ,raw_sentences, config['-v'])   





