import re
import sys
import getopt


list_arg = []  # list of all nodes/args
dict_graph = {}  # contains the graph
dict_defend = {}  # contains all args defended by each args
dict_attack = {}  # contains all args attacking each args
dict_relation = {}  # contains all args in conflict with each args
is_cicle = False

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

def check_admissible(extension):
    """return True if extension is admissible, else return False

    Args:
        extension (list[str]): extension, list of arguments

    Returns:
        bool: True if extension is admissible, otherwise False
    """
    must_defend_against = list()
    # adds all arg that extension must defend itself against
    for arg in extension:
        for attacked_by in dict_attack[arg]:
            if attacked_by not in must_defend_against:
                must_defend_against.append(attacked_by)
    # remove all arg extension defend itself against
    for arg2 in extension:
        for arg3 in dict_graph[arg2]:
            if arg3 in must_defend_against:
                must_defend_against.remove(arg3)
    
    # if not empty, then extension it does not defend against the rest
    if must_defend_against:
        return False
    return True

def admissible():
    """adds all admissible extensions to ad
    """
    global ad
    for cf_extension in cf:
        if check_admissible(cf_extension):
            ad.append(cf_extension)

def check_stable_extension(extension):
    """return True if the conflict free extension is stable, 
        else return False

    Args:
        extension (list[str]): list of arguments

    Returns:
        bool: True if the extension is stable, otherwise False
    """
    all_arg = []
    for arg in extension:
        all_arg.append(arg)
        for value in dict_graph[arg]:
            if value not in all_arg:
                all_arg.append(value)
    if list_arg == sorted(all_arg):
        return True
    return False 
                    
def stable():
    """adds all stable extensions to st
    """
    global st
    if co == [[]]:
        pass
    else:
        for co_extension in co:
            if check_stable_extension(co_extension) and co_extension not in st:
                st.append(co_extension)

def defend(extension, arg):
    """return True if extension defends arg against all his attackers

    Args:
        extension (list[str]): list of arguments
        arg (str): argument not in the list

    Returns:
        bool: True if extension defends arg, otherwise False
    """
    list_attacked_arg = []  # list of all attacked arguments by extension
    for arg2 in extension:
        for attacked_arg in dict_graph[arg2]:  # for all arg attacked by arg2
            if attacked_arg not in list_attacked_arg:
                list_attacked_arg.append(attacked_arg)
    for attacked_arg2 in dict_attack[arg]:
        if attacked_arg2 not in list_attacked_arg:
            return False
    return True

def dung_cf(extension):
    """dung characteristic function

    Args:
        extension (list[str]): list of arg or empty list

    Returns:
        list[str]: list of arg or empty list
    """
    if extension == []:
        for key, value in dict_attack.items():
            if value == [] and key not in gr:
                extension.append(key)
    else:
        start_arg = extension[-1]
        path = dfs(start_arg)
        for arg2 in path:
            if arg2 not in extension and defend(extension, arg2):
                extension.append(arg2)
    return sorted(extension)

def complete():
    """adds all complete extension to co
    """
    global co
    gr_copy = gr[0].copy()
    if not gr_copy:
        co.append(gr_copy)
    for cf_extension in cf:
        cf_extension_copy = cf_extension.copy()
        is_not_co = True
        while is_not_co:
            cf_extension_copy = dung_cf(cf_extension_copy)
            if cf_extension_copy == dung_cf(cf_extension_copy):
                is_not_co = False
                if (check_complete(cf_extension_copy)
                    and inside(gr_copy, cf_extension_copy)
                    and cf_extension_copy not in co ):
                    co.append(cf_extension_copy)

def inside(extension1, extension2):
    """return True if all arg of extension1 are in extension2

    Args:
        extension1 (list[str]): contains the target arg
        extension2 (list[str]): may contain the target arg

    Returns:
        bool: return True if all args of extension are in extension2, otherwise False
    """
    for arg in extension1:
        if arg not in extension2:
            return False
    return True    

def check_complete(extension):
    """return True if extension is a complete extension, else return False

    Args:
        extension (list[str]): list of arg

    Returns:
        bool: True if extension is complete, otherwise False
    """
    if check_conflict_free(extension) and check_admissible(extension):
        for arg in extension:
            if not defend(extension, arg):
                return False
    else:
        return False
    return True

def cicle(arg, visited = None):
    """return all visited arguments, starting from arg,
        change is_cicle if there is a cycle in the graph

    Args:
        arg (str): the starting argument
        visited (list[str], optional): list of already visited arg. Defaults to None.

    Returns:
        list[str]: list of all visited arg
    """
    global is_cicle
    if not is_cicle:
        if visited is None:
            visited = []
        if arg not in visited:
            visited.append(arg)
        unvisited = []
        for n in dict_graph[arg]:
            if n in visited:
                is_cicle = True
                visited.append(n)
                break
            if n not in visited:
                unvisited.append(n)
        for arg in unvisited:
            cicle(arg, visited)
    return visited
       
def dfs(arg, visited=None):
    """recursively traverses the graph from a starting arg

    Args:
        arg (str): the starting argument
        visited (list[str], optional): list of already visited arg. Defaults to None.

    Returns:
        list[str]: list of all visited arg
    """
    if visited is None:
        visited = []
    if arg not in visited:
        visited.append(arg)
    unvisited = []
    for arg2 in dict_graph[arg]:
        if arg2 not in visited:
            unvisited.append(arg2)       
    for arg in unvisited:
        dfs(arg, visited)

    return visited       
       
def grounded():
    """for graph with cycle, using dung cf to find the grounded
        grounded added to gr
    """
    global gr
    gr_copy = gr.copy()
    
    is_not_gr = True
    while is_not_gr:
        gr_extension = dung_cf(gr_copy)
        if gr_extension == dung_cf(gr_extension):
            is_not_gr = False
            gr.append(gr_extension)  

def well_founded():
    """finds all sementics if there is no cycle in the graph
    """
    global gr, st, pr, co
    extension = []
    while True:
        extension = dung_cf(extension)
        if extension == dung_cf(extension):
            break
    
    gr = [sorted(extension)]
    st = gr.copy()
    pr = gr.copy()
    co = gr.copy()                        

def cred(sementics):
    """return the list of all accepted argument,
        an argument is credulously accepted, if he is present in at least in one extension of sementics

    Args:
        sementics (list[list[str]]): list of extension

    Returns:
        list[list[str]]: list of all credulously accepted argument
    """
    if sementics:
        tmp = set(sementics[0])
        for extension in sementics:
            tmp = set(tmp).union(set(extension))
        return list(sorted(tmp))
    return []
    
def skep(sementics):
    """return the list of all accepted argument,
        an argument is skeptically accepted, if he is present in all extension of sementics

    Args:
        sementics (list[list[str]]): list of extension

    Returns:
        list[list[str]]: list of all skeptically accepted argument
    """
    if sementics:
        tmp = set(sementics[0])
        if sementics == st and not st:
            tmp = list_arg.copy()
        else:
            for extension in sementics:
                tmp = set(tmp).intersection(set(extension))
        return list(sorted(tmp))
    return []

def skep_stable(sementics):
    """return the list of all stable skeptically accepted argument

    Args:
        sementics (list[list[str]]): list of extension

    Returns:
        list[list[str]]: list of all skeptically accepted argument
    """
    if not st:
        return list_arg
    return skep(sementics)                             
    
def string(extension):
    """displays the list in the requested way

    Args:
        extension (list[str]): _description_

    Returns:
        str: return the str that will be displayed
    """
    if extension == []:
        return []
    res = '[' + extension[0]
    for ind in range(1,len(extension)):
        res +=  ','
        res += extension[ind]
    res += ']'
    return res                             
    
def main(argv):
    """main method

    Args:
        argv (list[str]): contains all the parameters entered on the terminal
    """
    global gr, st, pr, co, cf, ad, list_arg, dict_graph, dict_defend, dict_attack, dict_relation, is_cicle 
    output = ''
    extension = list()
    
    opts, args = getopt.getopt(argv,"f:p:a:")

    tmp = opts[0]
    opts[0] = opts[1]
    opts[1] = tmp
    
    for opt, arg in opts:
        if opt == "-f":
            get_graph(arg)
            get_attack()
            get_defend()
            get_relation()
            conflict_free()
            #admissible()
            for arg1 in list_arg:
                cicle(arg1, visited=None)
            if is_cicle:
                grounded()
                complete()
                stable()                                
            else:
                well_founded()
           
        elif opt == "-p":
            if arg == "SE-CO":
                if co == [[]]:  # if co is equals to {∅}
                    output = 'NO'
                else:
                    extension = co[-1].copy()
                    output = string(extension)
            elif arg == "DC-CO":
                extension = cred(co)
                output = string(extension)
            elif arg == "DS-CO":
                extension = skep(co)
                output = string(extension)
            elif arg == "SE-ST":
                if st == []:  # if st is equals to ∅ 
                    output = 'NO'
                else:
                    extension = st[-1].copy()
                    output = string(extension)
            elif arg == "DC-ST":
                extension = cred(st)
                output = string(extension)
            elif arg == "DS-ST":
                extension = skep_stable(st)
                output = string(extension)
            elif arg== "VE-CO":
                extension = co
            elif arg== "VE-ST":
                extension = st

        elif opt == "-a":
            if arg == "[]":
                arg = []
            elif len(arg) > 1:
                arg = arg.upper().split(",")
            else:
                arg =arg.upper()
            if arg in extension:
                output = 'YES'
            if arg not in extension:
                output = 'NO'
    
    print(co)
    print(skep(co))
    print(cred(co))
    print(output, "\n")
                              
if __name__ == "__main__":
    main(sys.argv[1:])