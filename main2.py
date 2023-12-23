import re
import argparse


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

def cycle(arg, visited = None):
    """return all visited arguments, starting from arg,
        change is_cycle if there is a cycle in the graph

    Args:
        arg (str): the starting argument
        visited (list[str], optional): list of already visited arg. Defaults to None.

    Returns:
        list[str]: list of all visited arg
    """
    global is_cycle
    if not is_cycle:
        if visited is None:
            visited = []
        if arg not in visited:
            visited.append(arg)
        unvisited = []
        for n in dict_graph[arg]:
            if n in visited:
                is_cycle = True
                visited.append(n)
                break
            if n not in visited:
                unvisited.append(n)
        for arg in unvisited:
            cycle(arg, visited)
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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Argumentation Framework Solver")
    parser.add_argument("-p", choices=["VE-CO", "VE-ST", "DC-CO", "DS-CO", "DC-ST", "DS-ST"],
                        help="Problem type")
    parser.add_argument("-f", help="Path to the text file describing the AF")
    parser.add_argument("-a", nargs="+", help="Names of arguments in the query set or query argument")
    return parser.parse_args()

def load_data(file_path):
    get_graph(file_path)
    get_attack()
    get_defend()
    get_relation()
    conflict_free()
    #admissible()
    for arg1 in list_arg:
        cycle(arg1, visited=None)
    if is_cycle:
        grounded()
        complete()
        stable()                                
    else:
        well_founded()

def process_argument_VE(arg):
    return [] if arg == "[]" else arg.upper().split(',')

def process_argument_DCDS(arg):
    return arg.upper()

def main():
    global gr, st, pr, co, cf, ad, list_arg, dict_graph, dict_defend, dict_attack, dict_relation, is_cycle

    # Get command line arguments
    args = parse_arguments()

    # Load data from the file
    load_data(args.f)

    is_verify = False

    # Process different types of problems
    if args.p == "VE-CO":
        extension = co
        is_verify = True
    elif args.p == "VE-ST":
        extension = st
        is_verify = True
    elif args.p == "DC-CO":
        extension = cred(co)
    elif args.p == "DS-CO":
        extension = skep(co)
    elif args.p == "DC-ST":
        extension = cred(st)
    elif args.p == "DS-ST":
        extension = skep_stable(st)

    # Process the argument
    arg = process_argument_VE(args.a[0]) if is_verify else process_argument_DCDS(args.a[0])

    # Check if the argument is in the extension
    output = 'YES' if arg in extension else 'NO'

    # Display the result
    print(output)

if __name__ == "__main__":
    main()