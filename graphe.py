import re

list_arg = []  # list of all nodes/args
dict_graph = {}  # contains the graph
dict_defend = {}  # contains all args defended by each args
dict_attack = {}  # contains all args attacking each args
dict_relation = {}  # contains all args in conflict with each args
is_cycle = False

cf = []  # list of conflict free extensions
ad = []  # list of admissible extensions

#σ-extensions
gr = []  # grounded semantic
st = []  # stable semantic
co = []  # complete semantic

def get_graph(file_name):
    """extract nodes and arrows from the text file and modify dict_graph,
        keys are the nodes and the values are the lists of nodes attacked by the keys.

    Args:
        file_name (str): file's name, cointains the graph
    """
    global dict_graph, dict_defend, dict_attack, dict_relation
    with open(file_name) as my_file:
        for line in my_file.readlines():
            split_line = re.split("[(,).]",line)
            if split_line[0] == "arg":
                dict_graph[split_line[1]] = []
                dict_defend[split_line[1]] = []
                dict_attack[split_line[1]] = []
                dict_relation[split_line[1]] = []
                list_arg.append(split_line[1])
            elif split_line[0] == "att":
                if split_line[1] in list_arg and split_line[2] in list_arg:
                    dict_graph[split_line[1]].append(split_line[2]) 
                    dict_relation[split_line[1]].append(split_line[2])
                
def get_attack():
    """extract nodes and arrows from the text file and modify dict_attack,
        keys are the nodes and values are the lists of nodes that attack the keys.
    """
    global dict_attack
    for arg in list_arg:
        for attacked_arg in dict_graph[arg]:
            dict_attack[attacked_arg].append(arg)                

def get_relation():
    """extract nodes and arrows from the text file and modify dict_relation,
        keys are the nodes and values are the lists of nodes in conflict with the keys.
    """
    global dict_relation
    for arg in list_arg:
        for arg2 in dict_attack[arg]:
            if arg2 not in dict_relation[arg]:
                dict_relation[arg].append(arg2)               
                
def check_conflict_free(extension):
    """return True if the extension is conflict free,
        else return False

    Args:
        extension (list[str]): tuple of arguments

    Returns:
        bool: True if the extension is conflict free, otherwise False
    """
    for arg1 in extension:
        for arg2 in extension:
            if arg2 in dict_relation[arg1]:  # if arg2 is get_graphed by arg1
                return False
    return True

def conflict_free():
    """adds all extensions without conflict in cf

    """
    global cf
    all_extension = []
    combination(all_extension,0, list(), len(list_arg), list())
    cf = all_extension
   
def combination(liste2, ind, liste_tmp, size_liste, invalid_arg):
    """finds all conflict free extensions, adds them to liste2

    Args:
        liste2 (list[]): list of all conflict free extensions
        ind (int): index of the next arg in list_arg
        liste_tmp (list[str]): current extension, if conflict free, added to liste2
        size_liste (int): len of list_arg
        invalid_arg (list[str]): list of all args liste_tmp can't contain
    """
    tmp = liste_tmp.copy()
    invalid_arg_tmp = invalid_arg.copy()
    for i in range(ind, size_liste):
        if invalid_arg:  
        
            while i < size_liste and list_arg[i] in invalid_arg :
                i = i+1
                ind += 1
                
        if i >= size_liste:
            return
     
        tmp.append(list_arg[i])
        
        liste2.append(tmp.copy())
        for arg in dict_relation[list_arg[i]]:
            if arg not in invalid_arg_tmp:
                invalid_arg_tmp.append(arg)
        combination(liste2, i+1, tmp.copy(), size_liste,invalid_arg_tmp.copy())
        tmp = liste_tmp.copy()
        invalid_arg_tmp = invalid_arg.copy()   

def get_defend():
    """stores in a dictionary (dict_defend) the list of arguments defended by each arg
    """
    global dict_defend
    for arg in list_arg:
        for key, value in dict_graph.items():
            if arg != key and arg in value:  # if arg is attacked by key
                for key2, value2 in dict_graph.items():
                    if (key in value2  # if key is attacked by key2 / arg is defended by key2 
                        and arg not in dict_defend[key2]
                        and arg not in dict_relation[key2]):  # if arg is not attacking key2
                        dict_defend[key2].append(arg)     
