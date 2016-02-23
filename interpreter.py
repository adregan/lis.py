ex_program = '(begin (define r 10) (* pi (* r r)))'
ex_tokens = ['(', 'begin', '(', 'define', 'r', '10', ')', '(', '*', 'pi', '(', '*', 'r', 'r', ')', ')', ')']
ex_expressions = ['begin', ['define', 'r', 10], ['*', 'pi', ['*', 'r', 'r']]]

Symbol = str
List = list
Number = (int, float)

class Procedure(object):
    ''' A user defined Scheme procedure'''
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        return self if (var in self) else self.outer.find(var)

def tokenize(input):
    ''' tokenize: Str -> List
        takes a string and splits it into tokens on the whitespace
        >>> tokenize(ex_program)
        ['(', 'begin', '(', 'define', 'r', '10', ')', '(', '*', 'pi', '(', '*', 'r', 'r', ')', ')', ')']

    '''
    return input.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    ''' parse : Str -> List
        will take a program string, tokenize and parse expressions
        >>> assert parse(ex_program) == ex_expressions 
    '''
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    ''' read_from_tokens: List -> List
        will parse expressions from tokens
        >>> assert read_from_tokens(ex_tokens) == ex_expressions
    '''
    if len(tokens) == 0:
        raise SyntaxError('Unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        try:
            tokens.pop(0) #throw away closing paren
        except IndexError:
            print('Syntax Error: Missing ) {}'.format(' '.join(L)))
        return L
    elif token == ')':
        raise SyntaxError('Unexpected )')
    else:
        return atom(token)

def atom(token):
    ''' atom: Str -> [ Int | Float | Str ]
    '''
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

def standard_env():
    env = Env()
    import math, operator as op
    env.update(vars(math))
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        'abs': abs,
        'append': op.add,
        'apply': lambda fn, *x: fn(*x),
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, Symbol)
    })
    return env

global_env = standard_env()

def eval(x, env=global_env):
    ''' Evaluate an expression in an environment
        >>> eval(parse('(define _@_# 10)'))
        >>> eval(parse('_@_#'))
        10
    '''
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

def repl(prompt='lispy > '):
    while True:
        try:
            val = eval(parse(input(prompt)))
        except KeyError as err:
            print('Syntax Error: {}'.format(err))
            continue
        if val:
            try:
                print(schemestr(val))
            except SyntaxError as err:
                print('Syntax Error: {}'.format(err))
                continue

def schemestr(exp):
    ''' Convert python obj to readable string'''
    if isinstance(exp, list):
        return '(' + ' '.join([schemestr(x) for x in exp]) + ')'
    else:
        return str(exp)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
