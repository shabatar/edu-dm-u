import ast

import pretty_printer


class VariablesCollector(ast.NodeVisitor):
    def __init__(self):
        self.current = 0
        self.ignored = {"self"}
        self.variables = {}
        self.renaming_context = False

    def __add_name(self, name):
        if not self.renaming_context:
            return

        if name not in self.ignored and name not in self.variables:
            self.variables[name] = self.current
            self.current += 1

    def visit_Assign(self, node):
        old_context = self.renaming_context
        self.renaming_context = True
        for target in node.targets:
            self.visit(target)
        self.renaming_context = old_context

    def visit_Name(self, node):
        self.__add_name(node.id)

    def visit_arguments(self, node):
        old_context = self.renaming_context
        self.renaming_context = True
        for arg in node.args:
            self.visit(arg)
        self.renaming_context = old_context

    def visit_arg(self, node):
        self.__add_name(node.arg)


class VariablesRenamer(ast.NodeTransformer):
    def __init__(self, variables):
        self.variables = variables

    def visit_Name(self, node):
        if node.id not in self.variables:
            return node
        new_name = "i" + str(self.variables[node.id])
        return ast.copy_location(ast.Name(id=new_name, ctx=node.ctx), node)

    def visit_arg(self, node):
        if node.arg not in self.variables:
            return node
        new_name = "i" + str(self.variables[node.arg])
        return ast.copy_location(ast.arg(arg=new_name, annotation=node.annotation), node)


def rename(code_ast):
    var_collector = VariablesCollector()
    var_collector.visit(code_ast)
    var_renamer = VariablesRenamer(var_collector.variables)
    var_renamer.visit(code_ast)


def process_code(code: str) -> (ast, str):
    try:
        code_ast = ast.parse(code)
    except SyntaxError:
        print("There was syntax error")
        return None

    rename(code_ast)

    result_code = pretty_printer.pretty(code_ast)

    return code_ast, result_code
