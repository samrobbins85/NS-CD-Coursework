import re
import sys
import itertools
import pygraphviz as pgv
import logging

logging.basicConfig(
    filename="parse.log",
    level=logging.DEBUG,
    format="%(levelname)s:%(message)s",
    filemode="w",
)

if len(sys.argv) != 2:
    print("You have given too many arguments")
    sys.exit(1)

G = pgv.AGraph(directed=False)

logging.info("Started the parsing")
try:
    f = open(sys.argv[1])
except:
    print("The file you have given is invalid")
    sys.exit(1)
file = f.read().split("\n")

# This merges together anything that goes onto a new line
i = 0
while not all((":" in line for line in file)):
    if ":" not in file[i]:
        file[i - 1] = file[i - 1] + file[i]
        file.pop(i)
    else:
        i += 1

for line in file:
    if line.startswith("variables"):
        variables = list(filter(None, line.split(":")[1].split()))
        logging.info("Variables in input file %s", variables)
    if line.startswith("constants"):
        constants = list(filter(None, line.split(":")[1].split()))
        logging.info("Constants in input file %s", constants)
    if line.startswith("predicates"):
        predicates = list(filter(None, line.split(":")[1].split()))
        altpredicates = list(filter(None, line.split(":")[1].split()))
        logging.info("Predicates in input file %s", predicates)
    if line.startswith("equality"):
        equality = list(filter(None, line.split(":")[1].split()))[0]
        logging.info("Equality symbol in input file, %s", equality)
    if line.startswith("connectives"):
        connectives = list(filter(None, line.split(":")[1].split()))
        logging.info("Connectives in input file %s", connectives)
    if line.startswith("quantifiers"):
        quantifiers = list(filter(None, line.split(":")[1].split()))
        logging.info("Quantifiers in input file %s", quantifiers)
    if line.startswith("formula"):
        formula = line.split(":")[1]
        logging.info("Formula in input file, %s", formula)

try:
    variables
    constants
    predicates
    equality
    connectives
    quantifiers
    formula
except NameError:
    logging.error("One of the required inputs was not in the file")
    sys.exit(1)


terminals = []
terminals += variables
terminals += constants
non_terminals = ["P", "V", "C", "E", "F", "O", "Q", "A"]

non_terminal_check = non_terminals + ["S"]
if any(item in variables for item in non_terminal_check):
    logging.error("A forbidden string has been used in variables")
    sys.exit(1)
if any(item in constants for item in non_terminal_check):
    logging.error("A forbidden string has been used in constants")
    sys.exit(1)
if any(item in connectives for item in non_terminal_check):
    logging.error("A forbidden string has been used in connectives")
    sys.exit(1)
if any(item in quantifiers for item in non_terminal_check):
    logging.error("A forbidden string has been used in quantifiers")
    sys.exit(1)
if equality in non_terminal_check:
    logging.error("The equality string is a forbidden string")
    sys.exit(1)

if any(item.isdigit() for item in variables):
    logging.error("A forbidden string has been used in variables")
    sys.exit(1)
if any(item.isdigit() for item in connectives):
    logging.error("A forbidden string has been used in connectives")
    sys.exit(1)
if any(item.isdigit() for item in quantifiers):
    logging.error("A forbidden string has been used in quantifiers")
    sys.exit(1)
if equality.isdigit():
    logging.error("The equality string is a forbidden string")
    sys.exit(1)


def get_predicate_production(predicates):
    logging.info("Getting the production for the predicates")
    for index, item in enumerate(predicates):
        number_parameters = item[item.find("[") + 1 : item.find("]")]
        text = item[0 : item.find("[")]
        predicates[index] = text + "("
        for i in range(0, int(number_parameters)):
            predicates[index] = predicates[index] + "V,"
        predicates[index] = predicates[index][:-1] + ")"
    return predicates


def get_equality_production(equality):
    logging.info("Getting the production for the equality symbol")
    valid_non_terminals = ["C", "V"]
    product = [p for p in itertools.product(valid_non_terminals, repeat=2)]
    equality_production = []
    for i in product:
        equality_production.append("(" + i[0] + equality + i[1] + ")")
    return equality_production


valid_formulae = ["R", "E", "O", "A"]


def get_connective_production(connectives):
    logging.info("Getting the production for the connectives")
    if len(connectives) != 5:
        sys.exit(1)
    not_operator = connectives[-1]
    connectives = connectives[:-1]
    connective_production = []
    for item in connectives:
        connective_production.append("(F " + item + " F)")
    connective_production.append(not_operator + " F")
    return connective_production


quantifier_formula = ["Q V F"]


def generate_production_string(production, non_terminal):
    string = ""
    for i in production:
        string += i + "|"
    string = string[:-1]
    return non_terminal + "->" + string


terminal_string = "{"
for i in terminals:
    terminal_string += i + ","
terminal_string = terminal_string[:-1] + "}"

logging.info("Writing the grammar to the file grammar.txt")
f = open("grammar.txt", "w")

f.write("G={" + terminal_string + ",{R,V,C,E,F,O,Q,A},P,S} where P includes:\n")
f.write("S->F\n")
f.write(generate_production_string(get_predicate_production(predicates), "R") + "\n")
f.write(generate_production_string(variables, "V") + "\n")
f.write(generate_production_string(constants, "C") + "\n")
f.write(generate_production_string(get_equality_production(equality), "E") + "\n")
f.write(generate_production_string(valid_formulae, "F") + "\n")
f.write(generate_production_string(get_connective_production(connectives), "O") + "\n")
f.write(generate_production_string(quantifiers, "Q") + "\n")
f.write(generate_production_string(quantifier_formula, "A") + "\n")
f.close()
logging.info("Writing grammar successful")


def check_equality_in_formula(equality, constants, variables, formula):
    logging.info("Finding all the equality atoms in the formula")
    re_find = re.findall(r"\([^\(\)]*" + equality + "[^,\)]*\)", formula)
    valid_equalities = []
    for item in re_find:
        logging.info("Checking the validity of the atom %s", item)
        atom = item.replace("(", "")
        atom = atom.replace(")", "")
        atom = atom.split()
        if len(atom) != 3:
            logging.error("The equality atom, %s was incorrectly formatted", item)
            sys.exit(1)
        if atom[0] not in constants and atom[0] not in variables:
            logging.error(
                "The symbol %s in the atom %s is neither a constant nor a variable",
                atom[0],
                item,
            )
            sys.exit(1)
        if atom[2] not in constants and atom[2] not in variables:
            logging.error(
                "The symbol %s in the atom %s is neither a constant nor a variable",
                atom[2],
                item,
            )
            sys.exit(1)
        if atom[1] != equality:
            logging.error("The symbol %s is not the equality symbol", atom[1])
            sys.exit(1)
        logging.info("%s is valid", item)
        valid_equalities.append(item)
    return valid_equalities


def valid_predicates(predicates, variables, formula):
    logging.info("Finding the valid predicates in the formula")
    predicate_list = []
    for item in predicates:
        text = item[0 : item.find("[")]
        predicate_list.append(text)

    re_find = re.findall(r"[^\(\) ]+\([^\(\)]+\)", formula)
    for i in re_find:
        logging.info("Checking the validity of %s", i)
        predicate_text = re.sub(r"\([^)]*\)", "", i)
        if predicate_text not in predicate_list:
            logging.error(
                "The predicate symbol %s is not given in the language", predicate_text
            )
            sys.exit(1)
        inside_brackets = i[i.find("(") + 1 : i.find(")")]
        inside_brackets = inside_brackets.replace(" ", "")
        inside_brackets = inside_brackets.split(",")
        statement = predicate_text + "[" + str(len(inside_brackets)) + "]"
        if statement not in predicates:
            logging.error(
                "There is the wrong number of parameters for the predicate %s", i
            )
            sys.exit(1)
        if not all(item in variables for item in inside_brackets):
            logging.error("Not all the symbols inside %s are variables", i)
            sys.exit(1)
        logging.info("%s is valid", i)
    return re_find


equality_atoms = check_equality_in_formula(equality, constants, variables, formula)
predicate_atoms = valid_predicates(altpredicates, variables, formula)
count = 0
logging.info("Adding the equality atoms to the graph")
for item in equality_atoms:
    atom = item.replace("(", "")
    atom = atom.replace(")", "")
    atom = atom.split()
    G.add_node(str(count), color="red", label=atom[1])
    G.add_node(str(count) + "a", color="red", label=atom[0])
    G.add_node(str(count) + "b", color="red", label=atom[2])
    G.add_edge(str(count), str(count) + "a")
    G.add_edge(str(count), str(count) + "b")
    formula = formula.replace(item, str(count))
    count += 1
logging.info("Adding the predicate atoms to the graph")
for item in predicate_atoms:
    G.add_node(str(count), color="red", label=item)
    formula = formula.replace(item, str(count))
    count += 1


def rule3(connectives, formula):
    logging.info("Parsing all connectives on valid formulae")
    global count
    global G
    #     First get the not statements and replace them
    not_statements = re.findall(
        r"" + re.escape(connectives[-1]) + "[ ]+[0-9]+", formula
    )
    for item in not_statements:
        logging.info("Parsing %s", item)
        G.add_node(str(count), color="red", label=re.escape(connectives[-1]))
        G.add_edge(str(count), item.split()[1])
        formula = formula.replace(item, str(count))
        count += 1
    #     Now for some more stuff
    connective_statements = re.findall(r"\(+[ ]*[0-9]+[^)(]+[0-9]+[ ]*\)", formula)
    string_connective_statements = re.findall(
        r"\(+[ ]*[0-9]+[^)(]+[0-9]+[ ]*\)", formula
    )
    for index, item in enumerate(connective_statements):
        logging.info("Parsing %s", item)
        connective_statements[index] = item.replace("(", "")
        connective_statements[index] = (
            connective_statements[index].replace(")", "").split()
        )
        if len(connective_statements[index]) != 3:
            logging.error("%s is improperly formatted", item)
            sys.exit(1)
        if connective_statements[index][1] not in connectives:
            logging.error(
                "The connective %s used in %s is not a valid connective",
                connective_statements[index][1],
                item,
            )
            sys.exit(1)
    logging.info("Adding the connective statements to the tree")
    for index, item in enumerate(string_connective_statements):
        formula = formula.replace(item, str(count))
        G.add_node(
            str(count), color="red", label=re.escape(connective_statements[index][1])
        )
        G.add_edge(str(count), connective_statements[index][0])
        G.add_edge(str(count), connective_statements[index][2])
        count += 1
    return formula


def rule4(quantifiers, variables, formula):
    logging.info("Parsing all quantifiers on valid formulae")
    global count
    quantifier_statements = re.findall(r"[^ ()]+[ ]+[^ ()]+[ ]+[0-9]+", formula)
    quantifier_statements_string = re.findall(r"[^ ()]+[ ]+[^ ()]+[ ]+[0-9]+", formula)
    for index, item in enumerate(quantifier_statements):
        quantifier_statements[index] = quantifier_statements[index].split()
        if quantifier_statements[index][0].isdigit():
            quantifier_statements.pop(index)
            quantifier_statements_string.pop(index)
    for index, item in enumerate(quantifier_statements_string):
        logging.info("Parsing %s", item)
        tokens = item.split()
        if tokens[0] not in quantifiers:
            logging.error("%s in %s is not a quantifier", tokens[0], item)
            sys.exit(1)
        if tokens[1] not in variables:
            logging.error("%s in %s is not a variable", tokens[1], item)
            sys.exit(1)

        formula = formula.replace(item, str(count))
        G.add_node(
            str(count),
            color="red",
            label=re.escape(
                quantifier_statements[index][0] + " " + quantifier_statements[index][1]
            ),
        )
        G.add_edge(str(count), quantifier_statements[index][2])
        count += 1
    return formula


while True:
    test_formula = formula
    formula = rule3(connectives, formula)
    formula = rule4(quantifiers, variables, formula)
    if test_formula == formula:
        break
if formula.replace(" ", "").isdigit():
    logging.info("Formula is valid")
    logging.info("Writing the AST to file.png")
    G.layout(prog="dot")  # use dot
    G.draw("AST.png")
else:
    logging.error("Formula not valid")
    sys.exit(1)
