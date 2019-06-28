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

    def parse(self, code):
        '''
        Parses the input files and traverses it node by node.
        '''
        tree = ast.parse(code)
        self.visit(tree)

    def generic_visit(self, node):
        print("gen:      'visit_" + node.__class__.__name__ + "' is missing")
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Name(self, node): 
        return node.id

    def visit_Expr(self, node):
        return self.visit(node.value) + ";\n"

    def visit_Module(self, node):
        for n in node.body:
            code = self.visit(n)
            sys.stdout.write(code + "\n")

    def visit_Call(self, node):
        code = self.visit(node.func)
        code += "("
        alen = len(node.args)
        i = 0
        while i < alen:
            code += self.visit(node.args[i])
            if (i + 1) < alen:
                code += ","
            i += 1

        for n in node.keywords:
            arg = n.arg
            value = self.visit(n.value)
        code += ")"
        return code

    def visit_Str(self, node):
        return '"' + node.s + '"'

    def visit_Import(self, node):
        code = "import "
        for name in node.names:
            code += name.name
        return code

    def visit_Subscript(self, node):
        if isinstance(node.slice, _ast.Slice):
            return "(todo: slice)"
        elif isinstance(node.slice, _ast.Index):
            listVar = self.visit(node.value)
            index = self.visit(node.slice.value)
            if isinstance(index, _ast.Num):
                index = (str(listVar) + ".length" + str(index)) if int(index) < 0 else index
            index = "[" + str(index) + "]"
            data = str(listVar) + index
            return data
        else:
            sys.stderr.write("[Py2Dart Error] Unimplemented Type => " + type(node.slice))
            exit(-1)

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        code = value + "." + node.attr
        return code

    def visit_Num(self, node):
        code = str(node.n)
        return code

    def visit_Assign(self, node):
        code = ""
        for target in node.targets:
            if isinstance(target, _ast.Attribute) or isinstance(target, _ast.Subscript):
                code += self.visit(target) + " = "
            else:
                code += "var " + target.id + " = "
            code += self.visit(node.value) + ";"
        return code

    def visit_If(self, node):
        code = self.visit(node.test)
        code = "if(" + code + ") {\n"
        for n in node.body:
            code += self.visit(n)
        code += "}"

        if len(node.orelse):
            code += "\nelse "
            if len(node.orelse) == 1 and isinstance(node.orelse[0], _ast.If):
                code += self.visit(node.orelse[0])
            else:
                code += "{\n"
                for n in node.orelse:
                    code += self.visit(n)
                code += "}"
        return code

    def visit_Eq(self, node):
        return "=="

    def visit_Lt(self, node):
        return "<"

    def visit_Gt(self, node):
        return ">"

    def visit_Compare(self, node):
        left = self.visit(node.left)
        op = self.visit(node.ops[0])
        right = self.visit(node.comparators[0])
        code = left + " " + op + " " + right
        return code

    def visit_Try(self, node):
        code = "try {\n"
        for n in node.body:
            code += self.visit(n)
        code += "\n}\n"

        for handler in node.handlers:
            code += "catch " + handler.type.id + "{\n"
            if isinstance(handler.name, _ast.Name):
                code += " catch(" + handler.name.id + ")"

            for n in handler.body:
                code += self.visit(n)
            code += "}\n"

        if len(node.finalbody):
            code += "finally {\n"
            for n in node.finalbody:
                code += self.visit(n)
            code += "}"

        return code
