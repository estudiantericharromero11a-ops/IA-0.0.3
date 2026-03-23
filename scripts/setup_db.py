#!/usr/bin/env python3
"""
Script para configurar la base de datos: crear esquema y poblar datos iniciales.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.queries import get_connection

def setup_database():
    """Ejecuta el script SQL para crear el esquema completo de la base de datos."""

    schema_path = os.path.join(os.path.dirname(__file__), 'create_schema.sql')

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()

        print("✅ Esquema de base de datos creado exitosamente")
        return True

    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {schema_path}")
        return False
    except Exception as e:
        print(f"❌ Error creando esquema: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Configurando base de datos...")
    if setup_database():
        print("✅ Base de datos configurada. Ahora ejecuta:")
        print("   python scripts/poblar_conocimiento.py")
    else:
        print("❌ Error en configuración")
        sys.exit(1)
    datos_ejemplo = [
        "Tabla personas: id_persona, nombre, documento, correo, telefono",
        "Tabla asignacion_instalaciones: id_asignacion, id_instalacion, id_materia, dia_semana, hora_inicio, hora_fin, id_persona",
        "Tabla materias: id_materia, nombre, creditos, descripcion",
        "Tabla instalaciones: id_instalacion, nombre, tipo_instalacion, piso, capacidad, id_bloque, id_area, id_estado",
        "Tabla campus: id_campus, nombre, direccion, descripcion",
        "Tabla bloques: id_bloque, nombre, descripcion, id_campus",
        "Tabla areas_funcionales: id_area, nombre_area, descripcion",
        "Tabla estado_instalacion: id_estado, nombre_estado, descripcion",
        "Tabla horario_instalacion: id_horario, id_instalacion, dia_semana, hora_apertura, hora_cierre",
        "Tabla programas: id_programa, nombre, tipo_programa, duracion_semestres",
        "Tabla programa_materia: id_programa, id_materia",
        "Tabla roles: id_rol, nombre_rol, descripcion",
        "Tabla persona_rol: id_persona, id_rol"
    ]
    
    from ai.embeddings import get_embedding
    for texto in datos_ejemplo:
        embedding = get_embedding(texto)
        cursor.execute("INSERT INTO conocimiento (contenido, embedding) VALUES (%s, %s)", (texto, embedding))
    
    conn.commit()
    cursor.close()
    release_conn(conn)
    print("Base de datos configurada y poblada.")

if __name__ == "__main__":
    setup_database()