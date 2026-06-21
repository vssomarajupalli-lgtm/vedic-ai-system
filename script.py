import ast
import os
import json

def get_class_info(path):
    try:
        with open(path, 'r', encoding='utf-8') as f: src = f.read()
    except: return None
    module = ast.parse(src)
    classes = [n for n in module.body if isinstance(n, ast.ClassDef)]
    res = []
    for c in classes:
        doc = ast.get_docstring(c) or 'No doc'
        methods = [m.name for m in c.body if isinstance(m, ast.FunctionDef)]
        res.append({'name': c.name, 'doc': doc[:100].replace('\n',' '), 'methods': methods})
    return res

for d in ['backend/app/engines', 'backend/app/formulas']:
    for f in os.listdir(d):
        if f.endswith('.py') and f != '__init__.py':
            info = get_class_info(f'{d}/{f}')
            print(f'--- {f} ---')
            if info:
                for c in info: print(f'Class: {c["name"]} | Methods: {c["methods"]}')
