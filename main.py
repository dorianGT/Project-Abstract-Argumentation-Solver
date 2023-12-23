import argparse
import extension               


def parse_arguments():
    parser = argparse.ArgumentParser(description="Argumentation Framework Solver")
    parser.add_argument("-p", choices=["VE-CO", "VE-ST", "DC-CO", "DS-CO", "DC-ST", "DS-ST"],
                        help="Problem type")
    parser.add_argument("-f", help="Path to the text file describing the AF")
    parser.add_argument("-a", nargs="+", help="Names of arguments in the query set or query argument")
    return parser.parse_args()

def load_data(file_path):
    extension.graphe.get_graph(file_path)
    extension.graphe.get_attack()
    extension.graphe.get_defend()
    extension.graphe.get_relation()
    extension.graphe.conflict_free()
    #admissible()
    for arg1 in extension.graphe.list_arg:
        extension.cycle(arg1, visited=None)
    if extension.graphe.is_cycle:
        extension.grounded()
        extension.complete()
        extension.stable()                                
    else:
        extension.well_founded()

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
        extensions = extension.graphe.co
        is_verify = True
    elif args.p == "VE-ST":
        extensions = extension.graphe.st
        is_verify = True
    elif args.p == "DC-CO":
        extensions = extension.cred(extension.graphe.co)
    elif args.p == "DS-CO":
        extensions = extension.skep(extension.graphe.co)
    elif args.p == "DC-ST":
        extensions = extension.cred(extension.graphe.st)
    elif args.p == "DS-ST":
        extensions = extension.skep_stable(extension.graphe.st)

    # Process the argument
    arg = process_argument_VE(args.a[0]) if is_verify else process_argument_DCDS(args.a[0])

    list_set = []
    for ext in extensions:
        list_set.append(set(ext))
    extensions = list_set        
    arg = set(arg)

    # Check if the argument is in the extension
    output = 'YES' if arg in extensions else 'NO'
    # Display the result
    print(output)

if __name__ == "__main__":
    main()
