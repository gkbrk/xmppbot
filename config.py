import shlex
import ast
import os

values = {}

def read_config(config_file="config.txt"):
    with open(config_file) as conf:
        for line in conf:
            lex = list(shlex.shlex(line, punctuation_chars=True))
            if len(lex) > 2:
                name = lex[0]
                args = ' '.join(lex[2:])
                val = ast.literal_eval(args)
                os.environ[name] = str(val)
                values[name] = val
