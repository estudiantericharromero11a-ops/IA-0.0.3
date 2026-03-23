import os, re
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
imports = set()
std = {'os','sys','logging','argparse','warnings','pathlib','time','json','datetime','re','subprocess','typing','shutil','getpass','collections','operator','csv','math','random','io','functools','pprint','textwrap','itertools','threading','multiprocessing','inspect'}
project_modules = set([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])
for root, dirs, files in os.walk(base):
    if '.venv' in root or 'venv' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                for line in fh:
                    line_stripped = line.strip()
                    if not line_stripped or line_stripped.startswith('#'):
                        continue
                    m = re.match(r'^(?:from)\s+([\w\.]+)\s+import', line_stripped)
                    if m:
                        mod = m.group(1).split('.')[0]
                        imports.add(mod)
                        continue
                    m = re.match(r'^(?:import)\s+([\w\.]+)', line_stripped)
                    if m:
                        mod = m.group(1).split('.')[0]
                        imports.add(mod)
                        continue
non_std = sorted(x for x in imports if x not in std and x not in project_modules)
print('\n'.join(non_std))
