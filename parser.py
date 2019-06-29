#############################################################################
# Copyright (C) 2019 Olaf Japp
#
# This file is part of Py2Dart.
#
#  Py2Dart is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Py2Dart is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Py2Dart. If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import ast, _ast
import sys

class Parser(ast.NodeVisitor):
    '''
    Python to Dart transpiler
    '''

    def __init__(self):
        self.inElse = False

    def parse(self, code):
        '''
        Parses the input files and traverses it node by node.
        '''
        tree = ast.parse(code)
        self.visit(tree, 0)

    def generic_visit(self, node, level):
        """Called if no explicit visitor function exists for a node."""
        sys.stderr.write("[Py2Dart Error] Unimplemented Type => " + "visit_" + node.__class__.__name__ + "\n")
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, level)
            elif isinstance(value, ast.AST):
                self.visit(value, level)
        return ""

    def visit(self, node, level):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, level)

    def visit_Name(self, node, level): 
        return node.id

    def visit_NameConstant(self, node, level):
        if node.value:
            return "true"
        else:
            return "false"

    def visit_Expr(self, node, level):
        return self.visit(node.value, level) + ";\n"

    def visit_Module(self, node, level):
        for n in node.body:
            code = self.visit(n, level)
            sys.stdout.write(code + "\n")

    def visit_Call(self, node, level):
        code = " " * level * 4 + self.visit(node.func, level)
        code += "("
        alen = len(node.args)
        i = 0
        while i < alen:
            code += self.visit(node.args[i], level)
            if (i + 1) < alen:
                code += ","
            i += 1

        for n in node.keywords:
            arg = n.arg
            value = self.visit(n.value, level)
        code += ")"
        return code

    def visit_Str(self, node, level):
        return '"' + node.s + '"'

    def visit_Import(self, node, level):
        sys.stderr.write("[Py2Dart Error] Not yet implemented => import\n")
        #code = " " * level * 4 + "import "
        #for name in node.names:
        #    code += name.name
        #return code + ";\n"
        return ""

    def visit_Subscript(self, node, level):
        if isinstance(node.slice, _ast.Index):
            listVar = self.visit(node.value, level)
            index = self.visit(node.slice.value, level)
            if isinstance(index, _ast.Num):
                index = (str(listVar) + ".length" + str(index)) if int(index) < 0 else index
            index = "[" + str(index) + "]"
            data = str(listVar) + index
            return data
        else:
            sys.stderr.write("[Py2Dart Error] Unimplemented Type => " + type(node.slice) + "\n")
            exit(-1)

    def visit_Attribute(self, node, level):
        value = self.visit(node.value, level)
        code = value + "." + node.attr
        return code

    def visit_Num(self, node, level):
        code = str(node.n)
        return code

    def visit_Assign(self, node, level):
        code = ""
        for target in node.targets:
            if isinstance(target, _ast.Attribute) or isinstance(target, _ast.Subscript):
                code += self.visit(target, level) + " = "
            else:
                code += " " * level * 4 + "var " + target.id + " = "
            code += self.visit(node.value, level) + ";\n"
        return code

    def visit_If(self, node, level):
        code = self.visit(node.test, level)

        if code == '__name__ == "__main__"':
            code = "void main() {\n"
        else:
            indent = ""
            if not self.inElse:
                indent += " " * level * 4
            code = indent + "if(" + code + ") {\n"
        for n in node.body:
            code += self.visit(n, level + 1)
        code += " " * level * 4 + "}\n"

        if len(node.orelse):
            code += " " * level * 4 + "else "
            if len(node.orelse) == 1 and isinstance(node.orelse[0], _ast.If):
                self.inElse = True
                code += self.visit(node.orelse[0], level)
                self.inElse = False
            else:
                code += "{\n"
                for n in node.orelse:
                    code += self.visit(n, level + 1)
                code += " " * level * 4 + "}\n"

        return code

    def visit_Eq(self, node, level):
        return "=="

    def visit_Lt(self, node, level):
        return "<"

    def visit_Gt(self, node, level):
        return ">"

    def visit_Div(self, node, level):
        return "/"

    def visit_BinOp(self, node, level):
        left = self.visit(node.left, level)
        op = self.visit(node.op, level)
        right = self.visit(node.right, level)
        exp = "(" + left + op + right + ")"
        return exp

    def visit_Return(self, node, level):
        code = " " * level * 4 + "return " + self.visit(node.value, level) + ";\n"
        return code

    def visit_Compare(self, node, level):
        left = self.visit(node.left, level)
        op = self.visit(node.ops[0], level)
        right = self.visit(node.comparators[0], level)
        code = left + " " + op + " " + right
        return code

    def visit_Try(self, node, level):
        code = " " * level * 4 + "try {\n"
        for n in node.body:
            code += self.visit(n, level + 1)
        code += " " * level * 4 + "}\n"

        for handler in node.handlers:
            code += " " * level * 4 + "catch "
            if handler.type:
                code += handler.type.id
            else:
                code += "(e)"
            code += "{\n"

            for n in handler.body:
                code += self.visit(n, level + 1)
            code += " " * level * 4 + "}\n"

        if len(node.finalbody):
            code += " " * level * 4 + "finally {\n"
            for n in node.finalbody:
                code += self.visit(n, level + 1)
            code +=  " " * level * 4 + "}\n"

        return code

    def visit_Pass(self, node, level):
        return ""

    def visit_FunctionDef(self, node, level):
        code = node.name + "("
        i = 0
        for arg in node.args.args:
            if i > 0:
                code += ","
            code += arg.arg
            i += 1
        code += ") {\n"
        for n in node.body:
            code += self.visit(n, 1)
        code += "}\n"
        return code