#!/usr/bin/env python

# -----------------------------------------------------------------------------
# calcact.py
#
# Enhance simple calculator to use ParserAction
#
# -----------------------------------------------------------------------------

import sys
sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
import os
import copy

        
class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.rule_action=kw.get('rule_action')
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run_loop(self, ):
        while 1:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            yacc.parse(s)

    def run(self, text=None):
        
        if not text: self.run_loop()
        else:
            yacc.parse(text)


class Calc(Parser):

    tokens = (
        'NAME', 'NUMBER',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS',
        'LPAREN', 'RPAREN',
    )

    # Tokens

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EXP = r'\*\*'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'EXP'),
        ('right', 'UMINUS'),
    )

    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        self.rule_action(p, 'statement_assign')

    def p_statement_expr(self, p):
        'statement : expression'
        self.rule_action(p, 'statement_expr')

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression DIVIDE expression
                   | expression EXP expression
        """
        self.rule_action(p, 'expression_binop')

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        self.rule_action(p, 'expression_uminus')

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        self.rule_action(p, 'expression_group')

    def p_expression_number(self, p):
        'expression : NUMBER'
        self.rule_action(p, 'expression_number')

    def p_expression_name(self, p):
        'expression : NAME'
        self.rule_action(p, 'expression_name')
        
    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")
        

class ParserActions(object):
    def __init__(self, action_map={},):
        self.action_map=action_map
        
    def __call__(self, p, tag):
        try: action=self.action_map[tag]
        except:
            try: action=self.action_map['']
            except: return p
        p[0]=action(p)
        

class CalcActions(ParserActions):
    def __init__(self,):
        action_map={'statement_assign': self.set_name,
                    'statement_expr': self.print_result,
                    'expression_binop': self.calc_expr,
                    'expression_uminus': lambda p: -p[2],
                    'expression_group': lambda p: p[2],
                    'expression_number': lambda p: p[1],
                    'expression_name': self.exp_name,
                    }
        super().__init__(action_map=action_map)
        self.names=dict()
        
    def print_result(self, p):
        print("result: %s" % (p[1], ))
        
    def set_name(self, p):
        self.names[p[1]] = p[3]
        
    def calc_expr(self, p):
        if   p[2] == '+':  p[0] = p[1] + p[3]
        elif p[2] == '-':  p[0] = p[1] - p[3]
        elif p[2] == '*':  p[0] = p[1] * p[3]
        elif p[2] == '/':  p[0] = p[1] / p[3]
        elif p[2] == '**': p[0] = p[1] ** p[3]
        return p[0]
            
    def exp_name(self, p):
        try: p[0] = self.names[p[1]]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0
        return p[0]


class CountOpsActions(CalcActions):
    def __init__(self,):
        super().__init__()
        self.count_ops_in_expr=0
                
    def print_result(self, p):
        print("result: %s (ops count: %s)" % (p[1], self.count_ops_in_expr))
        self.count_ops_in_expr=0

    def calc_expr(self, p):
        result=super().calc_expr(p)
        self.count_ops_in_expr+=1
        return result

    
if __name__ == '__main__':
    calc = Calc(rule_action=CalcActions())
    calc.run("5*4*6")
    
    count = Calc(rule_action=CountOpsActions())
    count.run("5*4*6")
    
    # to switch back, parser needs to be reinitialized
    calc = Calc(rule_action=CalcActions())
    calc.run("2*3*4")
