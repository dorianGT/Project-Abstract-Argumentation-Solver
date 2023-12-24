import re

list_arg = []  # List of all nodes/arguments
dict_graph = {}  # Contains the graph
dict_defend = {}  # Contains all arguments defended by each argument
dict_attack = {}  # Contains all arguments attacking each argument
dict_conflict = {}  # Contains all arguments in conflict with each argument

cf = []  # List of conflict-free extensions
ad = []  # List of admissible extensions


def get_graph(file_name):
    """
    Extract nodes and arrows from the text file and modify dict_graph,
    keys are the nodes and the values are the lists of nodes attacked by the keys.

    Args:
        file_name (str): file's name, contains the graph
    """
    global dict_graph, dict_defend, dict_attack, dict_conflict

    # Open the file
    with open(file_name) as my_file:
        # Read each line in the file
        for line in my_file.readlines():
            # Split the line based on ",", ".", or "("
            split_line = re.split("[(,).]", line)

            # Check if the line represents an argument
            if split_line[0] == "arg":
                # Initialize dictionaries for the argument
                dict_graph[split_line[1]] = []
                dict_defend[split_line[1]] = []
                dict_attack[split_line[1]] = []
                dict_conflict[split_line[1]] = []
                list_arg.append(split_line[1])
            # Check if the line represents an attack
            elif split_line[0] == "att":
                # Verify that the arguments exist in the list of arguments
                if split_line[1] in list_arg and split_line[2] in list_arg:
                    # Update dictionaries with attack information
                    dict_graph[split_line[1]].append(split_line[2])
                    dict_conflict[split_line[1]].append(split_line[2])

                
def get_attack():
    """
    Populate dict_attack based on the attack relationships in the graph.
    """
    global dict_attack

    # Iterate through each argument
    for arg in list_arg:
        # Iterate through arguments attacked by the current argument
        for attacked_arg in dict_graph[arg]:
            dict_attack[attacked_arg].append(arg)

def get_conflict():
    """
    Populate dict_conflict based on the conflict relationships in the graph.
    """
    global dict_conflict

    # Iterate through each argument
    for arg in list_arg:
        # Iterate through arguments attacking the current argument
        for arg2 in dict_attack[arg]:
            # Add arg2 to dict_conflict if not already present
            if arg2 not in dict_conflict[arg]:
                dict_conflict[arg].append(arg2)

def get_defend():
    """
    Populate dict_defend based on the defend relationships in the graph.
    """
    global dict_defend

    # Iterate through each argument
    for arg in list_arg:
        # Iterate through all arguments in the graph
        for key, value in dict_graph.items():
            # Check if arg is attacked by the current key
            if arg != key and arg in value:
                # Iterate through all arguments in the graph again
                for key2, value2 in dict_graph.items():
                    # Check if the current key is attacked by key2 and arg is not attacking key2
                    if key in value2 and arg not in dict_defend[key2] and arg not in dict_conflict[key2]:
                        dict_defend[key2].append(arg)

def check_conflict_free(extension):
    """
    Check if an extension is conflict-free.

    Args:
        extension (list): List of arguments representing an extension.

    Returns:
        bool: True if the extension is conflict-free, False otherwise.
    """
    for arg1 in extension:
        for arg2 in extension:
            # Check if arg2 is in conflict with arg1
            if arg2 in dict_conflict[arg1]:
                return False
    return True

def conflict_free():
    """
    Generate all conflict-free extensions and store them in the global variable cf.
    """
    global cf
    all_extensions = []
    generate_combinations(all_extensions, len(list_arg))
    cf = all_extensions

def generate_combinations(result, size_list, index=0, current_combination=[], invalid_args=[]):
    """
    Recursively generate all combinations of arguments, avoiding conflicts.

    Args:
        result (list): List to store generated combinations.
        size_list (int): Size of list_arg.
        index (int): Current index in the list_arg.
        current_combination (list): Current combination being generated.
        invalid_args (list): Arguments that should be avoided in the current combination.
    """
    tmp = current_combination.copy()
    invalid_args_tmp = invalid_args.copy()

    for i in range(index, size_list):
        # Skip invalid arguments
        while i < size_list and list_arg[i] in invalid_args:
            i += 1

        if i >= size_list:
            return

        tmp.append(list_arg[i])
        result.append(tmp.copy())

        # Update invalid_args for the next recursive call
        for arg in dict_conflict[list_arg[i]]:
            if arg not in invalid_args_tmp:
                invalid_args_tmp.append(arg)

        generate_combinations(result, size_list, i + 1, tmp.copy(), invalid_args_tmp.copy())
        tmp = current_combination.copy()
        invalid_args_tmp = invalid_args.copy()


