# Parser.py
import sys
import Lexer
import todot

class Parser:
    """Analyseur syntaxique pour Jack -> AST (dict/list)."""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)

    def look(self):
        return self.lexer.look()

    def look2(self):
        return self.lexer.look2()

    # ---------------- Top-level ----------------
    def jackclass(self):
        self.process('class')
        className = self.className()
        self.process('{')
        classVarDecs = []
        subroutineDecs = []
        while self.look() is not None and self.look()['token'] != '}':
            tk = self.look()['token']
            if tk in ('static', 'field'):
                classVarDecs.append(self.classVarDec())
            elif tk in ('constructor', 'function', 'method'):
                subroutineDecs.append(self.subroutineDec())
            else:
                self.error(self.look())
        self.process('}')
        return {'type': 'class', 'name': className, 'classVarDec': classVarDecs, 'subroutineDec': subroutineDecs}

    # ---------------- Declarations ----------------
    def classVarDec(self):
        kind = self.lexer.next()['token']
        print(kind)
        t = self.type()
        names = [self.varName()]
        while self.look() is not None and self.look()['token'] == ',':
            self.process(',')
            names.append(self.varName())
        self.process(';')
        return {'type': 'classVarDec', 'kind': kind, 'varType': t, 'names': names}

    def type(self):
        tk = self.look()
        if tk['token'] in ('int', 'char', 'boolean'):
            self.process(tk['token'])
            return {'type': 'type', 'name': tk['token']}
        else:
            return self.className()

    def subroutineDec(self):
        kind = self.lexer.next()['token']
        if self.look()['token'] == 'void':
            self.process('void')
            rettype = {'type': 'type', 'name': 'void'}
        else:
            rettype = self.type()
        name = self.subroutineName()
        self.process('(')
        params = self.parameterList()
        self.process(')')
        body = self.subroutineBody()
        return {'type': 'subroutineDec', 'subKind': kind, 'returnType': rettype, 'name': name, 'paramList': params, 'body': body}

    def parameterList(self):
        params = []
        if self.look()['token'] == ')':
            return params
        t = self.type()
        vn = self.varName()
        params.append({'type': 'parameter', 'varType': t, 'name': vn})
        while self.look() is not None and self.look()['token'] == ',':
            self.process(',')
            t = self.type()
            vn = self.varName()
            params.append({'type': 'parameter', 'varType': t, 'name': vn})
        return params

    def subroutineBody(self):
        self.process('{')
        varDecs = []
        while self.look() is not None and self.look()['token'] == 'var':
            varDecs.append(self.varDec())
        stmts = self.statements()
        self.process('}')
        return {'type': 'subroutineBody', 'varDec': varDecs, 'statements': stmts}

    def varDec(self):
        self.process('var')
        t = self.type()
        names = [self.varName()]
        while self.look() is not None and self.look()['token'] == ',':
            self.process(',')
            names.append(self.varName())
        self.process(';')
        return {'type': 'varDec', 'varType': t, 'names': names}

    # ---------------- Identifiers ----------------
    def className(self):
        tk = self.lexer.next()
        return {'type': 'className', 'name': tk['token']}

    def subroutineName(self):
        tk = self.lexer.next()
        return {'type': 'subroutineName', 'name': tk['token']}

    def varName(self):
        tk = self.lexer.next()
        return {'type': 'varName', 'name': tk['token']}

    # ---------------- Statements ----------------
    def statements(self):
        stmts = []
        while self.look() is not None and self.look()['token'] in ('let', 'if', 'while', 'do', 'return'):
            stmts.append(self.statement())
        return stmts

    def statement(self):
        tk = self.look()['token']
        if tk == 'let':
            return self.letStatement()
        elif tk == 'if':
            return self.ifStatement()
        elif tk == 'while':
            return self.whileStatement()
        elif tk == 'do':
            return self.doStatement()
        elif tk == 'return':
            return self.returnStatement()
        else:
            self.error(self.look())

    def letStatement(self):
        self.process('let')
        var = self.varName()
        index = None
        if self.look() is not None and self.look()['token'] == '[':
            self.process('[')
            index = self.expression()
            self.process(']')
        self.process('=')
        expr = self.expression()
        self.process(';')
        return {'type': 'letStatement', 'var': var, 'index': index, 'expr': expr}

    def ifStatement(self):
        self.process('if')
        self.process('(')
        cond = self.expression()
        self.process(')')
        self.process('{')
        thens = self.statements()
        self.process('}')
        elses = None
        if self.look() is not None and self.look()['token'] == 'else':
            self.process('else')
            self.process('{')
            elses = self.statements()
            self.process('}')
        return {'type': 'ifStatement', 'cond': cond, 'then': thens, 'else': elses}

    def whileStatement(self):
        self.process('while')
        self.process('(')
        cond = self.expression()
        self.process(')')
        self.process('{')
        body = self.statements()
        self.process('}')
        return {'type': 'whileStatement', 'cond': cond, 'body': body}

    def doStatement(self):
        self.process('do')
        call = self.subroutineCall()
        self.process(';')
        return {'type': 'doStatement', 'call': call}

    def returnStatement(self):
        self.process('return')
        expr = None
        if self.look() is not None and self.look()['token'] != ';':
            expr = self.expression()
        self.process(';')
        return {'type': 'returnStatement', 'expr': expr}

    # ---------------- Expressions ----------------
    def expression(self):
        left = self.term()
        while self.look() is not None and self.look()['token'] in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            op = self.op()
            right = self.term()
            left = {'type': 'binaryExpression', 'left': left, 'op': op, 'right': right}
        return left

    def term(self):
        tk = self.look()
        if tk['type'] == 'IntegerConstant':
            self.lexer.next()
            return {'type': 'integerConstant', 'value': int(tk['token'])}
        if tk['type'] == 'StringConstant':
            self.lexer.next()
            s = tk['token'][1:-1]
            return {'type': 'stringConstant', 'value': s}
        if tk['type'] == 'keyword' and tk['token'] in ('true', 'false', 'null', 'this'):
            self.lexer.next()
            return {'type': 'keywordConstant', 'value': tk['token']}
        if tk['token'] == '(':
            self.process('(')
            expr = self.expression()
            self.process(')')
            return expr
        if tk['token'] in ('-', '~'):
            op = self.unaryOp()
            operand = self.term()
            return {'type': 'unaryExpression', 'op': op, 'term': operand}
        if tk['type'] == 'identifier':
            id_tok = self.lexer.next()
            id_node = {'type': 'varName', 'name': id_tok['token']}
            if self.look() is not None and self.look()['token'] == '[':
                self.process('[')
                idx = self.expression()
                self.process(']')
                return {'type': 'arrayAccess', 'var': id_node, 'index': idx}
            if self.look() is not None and self.look()['token'] in ('(', '.'):
                return self._subroutineCall_from_identifier(id_node)
            return id_node
        self.error(tk)

    def _subroutineCall_from_identifier(self, id_node):
        if self.look()['token'] == '(':
            self.process('(')
            args = self.expressionList()
            self.process(')')
            return {'type': 'subroutineCall', 'callType': 'simple', 'name': id_node, 'args': args}
        elif self.look()['token'] == '.':
            self.process('.')
            subName = self.subroutineName()
            self.process('(')
            args = self.expressionList()
            self.process(')')
            return {'type': 'subroutineCall', 'callType': 'qualified', 'caller': id_node, 'name': subName, 'args': args}
        else:
            self.error(self.look())

    def subroutineCall(self):
        id_node = {'type': 'classvarName', 'name': self.lexer.next()['token']}
        if self.look() is not None and self.look()['token'] == '(':
            self.process('(')
            args = self.expressionList()
            self.process(')')
            return {'type': 'subroutineCall', 'callType': 'simple', 'name': id_node, 'args': args}
        elif self.look() is not None and self.look()['token'] == '.':
            self.process('.')
            subName = self.subroutineName()
            self.process('(')
            args = self.expressionList()
            self.process(')')
            return {'type': 'subroutineCall', 'callType': 'qualified', 'caller': id_node, 'name': subName, 'args': args}
        else:
            self.error(self.look())

    def expressionList(self):
        exprs = []
        if self.look() is not None and self.look()['token'] != ')':
            exprs.append(self.expression())
            while self.look() is not None and self.look()['token'] == ',':
                self.process(',')
                exprs.append(self.expression())
        return exprs

    def op(self):
        return self.lexer.next()['token']

    def unaryOp(self):
        return self.lexer.next()['token']
        
    def process(self, token_str):
        tok = self.lexer.next()
        if tok is None or tok['token'] != token_str:
            self.error(tok)
        return tok


    def error(self, tok):
        if tok is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError line={tok['line']} col={tok['col']}: {tok['token']}")
        exit()

# ---------------- Main ----------------
if __name__ == "__main__":
    file = sys.argv[1]
    parser = Parser(file)