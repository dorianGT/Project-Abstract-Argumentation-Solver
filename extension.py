import graph

# σ-extensions
gr = []  # Grounded semantics
st = []  # Stable semantics
co = []  # Complete semantics

is_cycle = False  # Flag indicating the presence of a cycle

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
        for attacked_by in graph.dict_attack[arg]:
            if attacked_by not in must_defend_against:
                must_defend_against.append(attacked_by)
    # remove all arg extension defend itself against
    for arg2 in extension:
        for arg3 in graph.dict_graph[arg2]:
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
    for cf_extension in graph.cf:
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
        for value in graph.dict_graph[arg]:
            if value not in all_arg:
                all_arg.append(value)
    if graph.list_arg == sorted(all_arg):
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
        for attacked_arg in graph.dict_graph[arg2]:  # for all arg attacked by arg2
            if attacked_arg not in list_attacked_arg:
                list_attacked_arg.append(attacked_arg)
    for attacked_arg2 in graph.dict_attack[arg]:
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
        for key, value in graph.dict_attack.items():
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
    for cf_extension in graph.cf:
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
    if graph.check_conflict_free(extension) and check_admissible(extension):
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
        for n in graph.dict_graph[arg]:
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
    for arg2 in graph.dict_graph[arg]:
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
            tmp = graph.list_arg.copy()
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
        return graph.list_arg
    return skep(sementics)    
