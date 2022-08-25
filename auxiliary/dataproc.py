import json

# This functions substitutes . instead ? and !
# After substitution text splits on sentences on dots
def getsentences(text_block:str)->list:
    text=text_block.replace('!', '.')
    text=text.replace('?', '.')
    text=text.split('.')
# This piece of code eliminate empty strings and trailing spaces
# in blocks with sentences.
    for el in enumerate(text):
        text[el[0]]=el[1].strip()
        if el[1]=='':
            text.pop(el[0])
    return text



def normsentence(sentence:str,line_length:int, number_of_line:int)->list:
    res=list()
    words=sentence.split(' ')
    textblocklist=list()
    text=""
    counter_row=0
    counter_symbols=0
    while len(words)>0:
        word=words.pop(0)
        if len(word)>line_length:
            print("Error, There is too long word in the text")
            exit()
        if (counter_symbols+len(word)+1)>line_length:
            if (counter_row+1)<number_of_line:
                counter_row+=1
            else:
                counter_row=0
                res.append(text)
                text="" 
            counter_symbols=0
        if counter_symbols==0 and counter_row==0:
            text=text+word
            counter_symbols=counter_symbols+len(word)
        else:
            text=text+' '+word
            counter_symbols=counter_symbols+1+len(word)
        
    res.append(text)
    return res


def get_segment(data_from_file:dict, n_segment:int,
        key_map:dict, text_list:list)->list:
    keys_from_file=list(data_from_file.keys())
    if n_segment in keys_from_file:
        words_with_keys =  data_from_file[n_segment]
    else:
        if len(text_list)-1 < n_segment:
            return list()
        words_with_keys=fill_default(text_list[n_segment], key_map)
    return words_with_keys


def split_list(double_list:list)->dict:
    res=dict()
    list_A=list()
    list_B=list()
    for el in double_list:
        list_A.append(el[0])
        list_B.append(el[1])
    res[0]=list_A
    res[1]=list_B
    return res

def write_marked_data(file_name:str, marked_data:dict):
   try:
       data_file=open(file_name, "w")
   except PermissionError:
       # Log it
       sys.exit()
   else:
       for el in marked_data.keys():
           tmp=dict()
           tmp[el]=marked_data[el]
           json.dump(tmp, data_file)
           data_file.write('\n')
       data_file.close()

def read_marked_data(file_name:str)->dict:
    res=list()
    store_dic=dict()
    text=""
    try:
        data_file=open(file_name, "r")
    except PermissionError:
        sys.exit()
    else:
        while True:
            text=data_file.readline()
            if  text == "":
                break
            text=text.strip("\n")
            res.append(text)
        data_file.close()
    while len(res)>0:
        line = res.pop(0)
        try:
            tmp_json=json.loads(line)
            number_line=int(list(tmp_json.keys())[0])
        except json.JSONDecodeError:
            # Log it
            sys.exit()
        except ValueError:
            # Log it
            sys.exit()
        else:
            store_dic[number_line]=tmp_json[str(number_line)]
    return store_dic

def to1d_list(tree_list:list)->list:
   res=list()
   for i in tree_list:
       if not isinstance(i, list):
           res.append(i)
       else:
           p=to1d_list(i)
           for el in p:
               res.append(el)
   return res

def addlist(first_list:list, second_list:list):
     for i in second_list:
         first_list.append(i)

def fill_default(word_list:list, marking:dict):
    marked_word_list=list()
    values=list(marking.values())
    for el in word_list:
        temp_list=list()
        temp_list.append(el)
        temp_list.append("<"+values[0]+">")
        marked_word_list.append(temp_list.copy())
    return marked_word_list

def key_map_to_list(data:dict, grid=(3,2))->list:
    res=list()
    temp_row=list()
    for i in data.keys():
        text="["+data[i]+"]"+" : "+"<"+str(i)+">"
        res.append(text)
    for i in range(grid[1]):
        temp_col=list()
        for j in range(grid[0]):
            if len(res)>0:
                temp_col.append(res.pop(0))
            else:
                temp_col.append("")
        a=temp_col.copy()
        temp_row.append(a)
    return temp_row

