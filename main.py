import argparse
import extension  

def parse_arguments():
    """Parse command line arguments.

    Returns:
        Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Argumentation Framework Solver")
    parser.add_argument("-p", choices=["VE-CO", "VE-ST", "DC-CO", "DS-CO", "DC-ST", "DS-ST"],
                        help="Problem type")
    parser.add_argument("-f", help="Path to the text file describing the AF")
    parser.add_argument("-a", nargs="+", help="Names of arguments in the query set or query argument")
    return parser.parse_args()

def load_graph(file_path):
    """Load the graph from a file.

    Args:
        file_path (str): Path to the text file describing the argumentation framework.
    """
    extension.graph.get_graph(file_path)

def get_data():
    """Perform main graph-related computations.

    This function includes retrieving attack, defend, conflict information,
    checking conflict-free status, detecting cycles, and computing grounded,
    complete, and stable extensions.

    Note: This is the main logic for handling graph-related computations.
    """

    # Retrieve attack, defend, and conflict information
    extension.graph.get_attack()
    extension.graph.get_defend()
    extension.graph.get_conflict()

    # Check conflict-free status
    extension.graph.conflict_free()

    # Perform cycle detection for each argument
    for arg1 in extension.graph.list_arg:
        extension.cycle(arg1, visited=None)

    # Check if a cycle is detected
    if extension.is_cycle:
        # Compute grounded, complete, and stable extensions if there is a cycle
        extension.grounded()
        extension.complete()
        extension.stable()
    else:
        # Compute well-founded extension if there is no cycle
        extension.well_founded()



def get_arguments_VE(arg):
    """Get arguments for VE-CO and VE-ST problems.

    Args:
        arg (str): Argument string

    Returns:
        list: Processed arguments
    """
    return [] if arg == "[]" else arg.upper().split(',')

def get_argument_DCDS(arg):
    """Get arguments for DC-CO, DS-CO, DC-ST, and DS-ST problems.

    Args:
        arg (str): Argument string

    Returns:
        str: Processed arguments
    """
    return arg.upper()


def main():
    global gr, st, pr, co, cf, ad, list_arg, dict_graph, dict_defend, dict_attack, dict_relation, is_cycle

    # Get command line arguments
    args = parse_arguments()

    # Load data from the file
    load_graph(args.f)

    # Get all data for the graph
    get_data()

    is_verify = False

    # Process different types of problems
    if args.p == "VE-CO":
        extensions = extension.co
        is_verify = True
    elif args.p == "VE-ST":
        extensions = extension.st
        is_verify = True
    elif args.p == "DC-CO":
        extensions = extension.cred(extension.co)
    elif args.p == "DS-CO":
        extensions = extension.skep(extension.co)
    elif args.p == "DC-ST":
        extensions = extension.cred(extension.st)
    elif args.p == "DS-ST":
        extensions = extension.skep_stable(extension.st)

    # Get the argument
    arg = get_arguments_VE(args.a[0]) if is_verify else get_argument_DCDS(args.a[0])

    # Convert the list of extensions to a list of sets
    list_set = []
    for ext in extensions:
        list_set.append(set(ext))
    extensions = list_set

    # Convert the argument to a set for comparison
    arg = set(arg)

    # Check if the argument is in the extension
    output = 'YES' if arg in extensions else 'NO'
    # Display the result
    print(output)

if __name__ == "__main__":
    main()
