import argparse

class ArgumentationFrameworkSolver:
    def __init__(self, af_file):
        self.arguments = set()
        self.attacks = set()
        self.load_af(af_file)

    def load_af(self, af_file):
        with open(af_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('arg'):
                    self.arguments.add(line.split('(')[1].split(')')[0])
                elif line.startswith('att'):
                    attack = line.split('(')[1].split(')')[0].split(',')
                    self.attacks.add((attack[0], attack[1]))

    def check_conflict_free(self, query_set):
        for arg1 in query_set:
            for arg2 in query_set:
                if arg1 != arg2 and (arg1, arg2) in self.attacks:
                    return False
        return True

    def check_admissible(self, query_set):
        # Check for conflicts in the query_set
        if not self.check_conflict_free(query_set):
            return False
        
        must_defend_against = list()
        
        # Add all arguments that the extension must defend itself against
        for arg in query_set:
            for attacker, attacked_arg in self.attacks:
                if arg == attacked_arg and not attacker in must_defend_against:
                    must_defend_against.append(attacker)
        
        # Remove all arguments that the extension defends against
        for arg in query_set:
            for attacker, attacked_arg in self.attacks:
                if arg == attacker and attacked_arg in must_defend_against:
                    must_defend_against.remove(attacked_arg)
        
        # If the list is not empty, then the extension does not defend against the remaining arguments
        if must_defend_against:
            return False
        return True
    
    def defend(self, query_set, arg):
        for attacker, attacked_arg in self.attacks:
            # Check if the current attacker is attacking the given argument
            if attacked_arg == arg:
                # Check if there is an element in the query_set that attacks the current attacker
                if not any((defender, attacker) in self.attacks for defender in query_set):
                    return False  # The argument cannot be defended against the attacker
        return True  # The argument is defended against all its attackers in the query_set



    def is_complete_extension(self, query_set):
        # Check if the query_set is admissible
        if self.check_admissible(query_set):
            # Check if the extension is complete
            for arg in self.arguments:
                if self.defend(query_set, arg) and arg not in query_set:
                    return False  # There is an argument defended outside the extension, not complete
            return True  # All arguments are defended within the extension, complete
        else:
            return False  # Not admissible, not complete


    def is_stable_extension(self, query_set):
        # Implement logic to check if query_set is a stable extension
        pass

    def is_credulously_accepted_complete(self, query_argument):
        # Implement logic to check if query_argument is credulously accepted for complete extensions
        pass

    def is_skeptically_accepted_complete(self, query_argument):
        # Implement logic to check if query_argument is skeptically accepted for complete extensions
        pass

    def is_credulously_accepted_stable(self, query_argument):
        # Implement logic to check if query_argument is credulously accepted for stable extensions
        pass

    def is_skeptically_accepted_stable(self, query_argument):
        # Implement logic to check if query_argument is skeptically accepted for stable extensions
        pass

def main():
    parser = argparse.ArgumentParser(description="Argumentation Framework Solver")
    parser.add_argument("-p", choices=["VE-CO", "VE-ST", "DC-CO", "DS-CO", "DC-ST", "DS-ST"],
                        help="Problem type")
    parser.add_argument("-f", help="Path to the text file describing the AF")
    parser.add_argument("-a", nargs="+", help="Names of arguments in the query set or query argument")
    args = parser.parse_args()

    solver = ArgumentationFrameworkSolver(args.f)

    if args.p == "VE-CO":
        result = solver.is_complete_extension(args.a)
        print("YES" if result else "NO")
    elif args.p == "VE-ST":
        result = solver.is_stable_extension(args.a)
        print("YES" if result else "NO")
    elif args.p == "DC-CO":
        result = solver.is_credulously_accepted(args.a[0])
        print("YES" if result else "NO")
    elif args.p == "DS-CO":
        result = solver.is_skeptically_accepted(args.a[0])
        print("YES" if result else "NO")

if __name__ == "__main__":
    main()
