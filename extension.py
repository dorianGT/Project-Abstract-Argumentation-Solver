import graph

# σ-extensions
gr = []  # Grounded semantics
st = []  # Stable semantics
co = []  # Complete semantics

is_cycle = False  # Flag indicating the presence of a cycle

def check_admissible(extension):
    """Check if an extension is admissible.

    Args:
        extension (list[str]): List of arguments in the extension.

    Returns:
        bool: True if the extension is admissible, otherwise False.
    """
    must_defend_against = list()

    # Add all arguments that the extension must defend itself against
    for arg in extension:
        for attacked_by in graph.dict_attack[arg]:
            if attacked_by not in must_defend_against:
                must_defend_against.append(attacked_by)

    # Remove all arguments that the extension defends itself against
    for arg2 in extension:
        for arg3 in graph.dict_graph[arg2]:
            if arg3 in must_defend_against:
                must_defend_against.remove(arg3)

    # If the list is not empty, the extension does not defend against some arguments
    if must_defend_against:
        return False

    return True

def admissible():
    """Identify and add all admissible extensions to the global variable ad.
    """
    global ad
    for cf_extension in graph.cf:
        if check_admissible(cf_extension):
            ad.append(cf_extension)

def check_stable_extension(extension):
    """Check if a conflict-free extension is stable.

    Args:
        extension (list[str]): List of arguments.

    Returns:
        bool: True if the extension is stable, otherwise False.
    """
    all_arguments = []

    # Traverse each argument in the extension
    for arg in extension:
        all_arguments.append(arg)

        # Traverse all arguments attacked by the current argument
        for value in graph.dict_graph[arg]:
            # If the attacked argument is not already in the list, add it
            if value not in all_arguments:
                all_arguments.append(value)

    # Check if all arguments in the graph are included in the extension
    if graph.list_arg == sorted(all_arguments):
        return True

    return False

def stable():
    """Identify and add all stable extensions to the global variable st.
    """
    global st
    if co == [[]]:
        pass
    else:
        for co_extension in co:
            if check_stable_extension(co_extension) and co_extension not in st:
                st.append(co_extension)

def defend(extension, arg):
    """Check if an extension defends a given argument against all its attackers.

    Args:
        extension (list[str]): List of arguments.
        arg (str): Argument not in the list.

    Returns:
        bool: True if the extension defends the argument, otherwise False.
    """
    list_attacked_arg = []

    # List all attacked arguments by the extension
    for arg2 in extension:
        for attacked_arg in graph.dict_graph[arg2]:
            if attacked_arg not in list_attacked_arg:
                list_attacked_arg.append(attacked_arg)

    # Check if the extension defends the argument against all its attackers
    for attacked_arg2 in graph.dict_attack[arg]:
        if attacked_arg2 not in list_attacked_arg:
            return False

    return True

def dung_cf(extension):
    """Dung's characteristic function.

    Args:
        extension (list[str]): List of arguments or empty list.

    Returns:
        list[str]: List of arguments or empty list.
    """
    if extension == []:
        # If the extension is empty, add all arguments that are not attacked by any other argument
        for key, value in graph.dict_attack.items():
            if value == [] and key not in gr:
                extension.append(key)
    else:
        start_arg = extension[-1]
        path = dfs(start_arg)

        # Add all arguments in the path that are not already in the extension and are defensible
        for arg2 in path:
            if arg2 not in extension and defend(extension, arg2):
                extension.append(arg2)

    return sorted(extension)

def complete():
    """Identify and add all complete extensions to the global variable co.
    """
    global co
    gr_copy = gr[0].copy()

    # If the grounded extension is empty, add it to the complete extensions
    if not gr_copy:
        co.append(gr_copy)

    for cf_extension in graph.cf:
        cf_extension_copy = cf_extension.copy()
        is_not_co = True

        while is_not_co:
            # Update the extension using Dung's characteristic function
            cf_extension_copy = dung_cf(cf_extension_copy)

            if cf_extension_copy == dung_cf(cf_extension_copy):
                is_not_co = False

                # Check if the extension is complete and inside the grounded extension
                if (check_complete(cf_extension_copy)
                        and inside(gr_copy, cf_extension_copy)
                        and cf_extension_copy not in co):
                    co.append(cf_extension_copy)


def inside(extension1, extension2):
    """Check if all arguments of extension1 are in extension2.

    Args:
        extension1 (list[str]): Contains the target arguments.
        extension2 (list[str]): May contain the target arguments.

    Returns:
        bool: True if all arguments of extension1 are in extension2, otherwise False.
    """
    for arg in extension1:
        if arg not in extension2:
            return False

    return True  

def check_complete(extension):
    """Check if an extension is complete.

    Args:
        extension (list[str]): List of arguments.

    Returns:
        bool: True if the extension is complete, otherwise False.
    """
    if graph.check_conflict_free(extension) and check_admissible(extension):
        for arg in extension:
            if not defend(extension, arg):
                return False
    else:
        return False
    return True

def cycle(arg, visited=None):
    """Identify all visited arguments starting from a given argument,
       and change is_cycle if there is a cycle in the graph.

    Args:
        arg (str): The starting argument.
        visited (list[str], optional): List of already visited arguments. Defaults to None.

    Returns:
        list[str]: List of all visited arguments.
    """
    global is_cycle

    # Check if there is already a cycle in the graph
    if not is_cycle:
        if visited is None:
            visited = []

        # Add the current argument to the visited list
        if arg not in visited:
            visited.append(arg)

        unvisited = []

        # Check each neighbor of the current argument
        for n in graph.dict_graph[arg]:
            # If the neighbor is already visited, there is a cycle
            if n in visited:
                is_cycle = True
                visited.append(n)
                break
            # If the neighbor is not visited, add it to the unvisited list
            if n not in visited:
                unvisited.append(n)

        # Recursively traverse the unvisited neighbors
        for arg in unvisited:
            cycle(arg, visited)

    return visited


def dfs(arg, visited=None):
    """Recursively traverse the graph from a starting argument.

    Args:
        arg (str): The starting argument.
        visited (list[str], optional): List of already visited arguments. Defaults to None.

    Returns:
        list[str]: List of all visited arguments.
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
    """For graphs with cycles, use Dung's characteristic function to find the grounded extension.
       The grounded extension is added to the global variable gr.
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
    """Find all semantics if there is no cycle in the graph.
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

def cred(semantics):
    """Return the list of all credulously accepted arguments.
    
    An argument is credulously accepted if it is present in at least one extension of semantics.

    Args:
        semantics (list[list[str]]): List of extensions.

    Returns:
        list[list[str]]: List of all credulously accepted arguments.
    """
    if semantics:
        tmp = set(semantics[0])
        for extension in semantics:
            tmp = set(tmp).union(set(extension))
        return list(sorted(tmp))
    return []

def skep(semantics):
    """Return the list of all skeptically accepted arguments.
    
    An argument is skeptically accepted if it is present in all extensions of semantics.

    Args:
        semantics (list[list[str]]): List of extensions.

    Returns:
        list[list[str]]: List of all skeptically accepted arguments.
    """
    if semantics:
        tmp = set(semantics[0])
        if semantics == st and not st:
            tmp = graph.list_arg.copy()
        else:
            for extension in semantics:
                tmp = set(tmp).intersection(set(extension))
        return list(sorted(tmp))
    return []

def skep_stable(semantics):
    """Return the list of all stable skeptically accepted arguments.

    Args:
        semantics (list[list[str]]): List of extensions.

    Returns:
        list[list[str]]: List of all skeptically accepted arguments.
    """
    # If there are no stable extensions (st is empty), return the list of all arguments in the graph
    if not st:
        return graph.list_arg

    # If there are stable extensions, use the skeptically accepted function (skep) on the given semantics
    return skep(semantics)
