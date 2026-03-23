import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.execute_query import ejecutar_sql
qs=[
    "SELECT DISTINCT nombre FROM instalaciones LIMIT 20",
    "SELECT nombre, piso, capacidad FROM instalaciones WHERE nombre ILIKE '%101%' OR nombre ILIKE '%lab%' LIMIT 20",
    "SELECT nombre, piso, capacidad FROM instalaciones ORDER BY nombre LIMIT 20"
]
for q in qs:
    r=ejecutar_sql(q)
    print('---', q)
    print(r)
