#!/usr/bin/env python3
"""
Script para poblar la tabla conocimiento con información detallada sobre
las tablas y columnas de la base de datos para mejorar la precisión de THANIA.
"""

import sys
import os
# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_conn
from ai.embeddings import get_embedding
from ai.schema_definitions import TABLAS_DEFINICIONES, RELACIONES_IMPORTANTES
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def poblar_contexto_bd():
    """
    Agrega información detallada sobre tablas y columnas a la base de conocimientos.
    """

    # Información detallada sobre cada tabla y columna
    contexto_bd = []

    # Información general sobre el esquema
    contexto_bd.append(
        "La base de datos universitaria contiene información completa sobre personas, instalaciones, programas académicos, horarios y roles. Cada tabla tiene un propósito específico y se relaciona con otras tablas mediante claves foráneas."
    )

    # Información detallada de cada tabla
    for nombre_tabla, definicion in TABLAS_DEFINICIONES.items():
        contexto_tabla = f"La tabla {nombre_tabla} {definicion['descripcion'].lower()}. "

        # Agregar información de columnas clave
        columnas_principales = []
        for nombre_col, desc_col in definicion["columnas"].items():
            if "identificador único" in desc_col or "clave primaria" in desc_col:
                columnas_principales.append(f"{nombre_col} es el identificador único")
            elif "clave foránea" in desc_col:
                columnas_principales.append(f"{nombre_col} referencia a otra tabla")

        if columnas_principales:
            contexto_tabla += "Columnas importantes: " + "; ".join(columnas_principales[:3]) + "."

        contexto_bd.append(contexto_tabla)

    # Relaciones importantes
    contexto_bd.append(
        "Relaciones clave: Los profesores se asignan a instalaciones mediante asignacion_instalaciones. Las instalaciones pertenecen a bloques y campus. Los programas académicos contienen múltiples materias. Las personas pueden tener diferentes roles."
    )

    # Consultas comunes por tipo
    contexto_bd.extend([
        "Para encontrar profesores: usar personas JOIN asignacion_instalaciones donde id_persona coincide.",
        "Para horarios de clases: consultar asignacion_instalaciones con dia_semana, hora_inicio y hora_fin.",
        "Para ubicación de instalaciones: usar instalaciones JOIN bloques JOIN campus.",
        "Para programas académicos: consultar programas JOIN programa_materia JOIN materias.",
        "Para roles administrativos: usar persona_rol JOIN roles JOIN personas.",
        "Para estado de instalaciones: consultar instalaciones JOIN estado_instalacion.",
        "Para horarios de apertura: usar horario_instalacion con dia_semana, hora_apertura y hora_cierre.",
        "Para capacidad de aulas: consultar instalaciones.capacidad filtrando por tipo_instalacion = 'aula'.",
        "Para materias por programa: usar programa_materia para relacionar programas con materias.",
        "Para personas por rol: usar persona_rol para asignar roles como profesor, estudiante o administrador."
    ])

    # Información específica sobre joins complejos
    contexto_bd.extend([
        "Join complejo para profesores con clases: personas p JOIN asignacion_instalaciones a ON p.id_persona = a.id_persona JOIN materias m ON a.id_materia = m.id_materia.",
        "Join para instalaciones completas: instalaciones i JOIN bloques b ON i.id_bloque = b.id_bloque JOIN campus c ON b.id_campus = c.id_campus JOIN areas_funcionales af ON i.id_area = af.id_area.",
        "Join para estudiantes en programas: personas p JOIN persona_rol pr ON p.id_persona = pr.id_persona JOIN roles r ON pr.id_rol = r.id_rol WHERE r.nombre_rol LIKE '%estudiante%'.",
        "Join para horario completo: asignacion_instalaciones a JOIN personas p ON a.id_persona = p.id_persona JOIN materias m ON a.id_materia = m.id_materia JOIN instalaciones i ON a.id_instalacion = i.id_instalacion."
    ])

    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Verificar registros existentes
        cursor.execute("SELECT COUNT(*) FROM conocimiento WHERE contenido LIKE '%tabla %' OR contenido LIKE '%columna %'")
        count_existente = cursor.fetchone()[0]

        logger.info(f"Registros existentes sobre BD: {count_existente}")

        # Insertar nuevo contexto
        inserts = 0
        for contenido in contexto_bd:
            # Verificar si ya existe contenido similar
            cursor.execute("SELECT id FROM conocimiento WHERE contenido = %s", (contenido,))
            if cursor.fetchone() is None:
                # Generar embedding
                embedding = get_embedding(contenido)

                # Insertar
                cursor.execute("""
                    INSERT INTO conocimiento (contenido, embedding)
                    VALUES (%s, %s)
                """, (contenido, embedding))

                inserts += 1
                logger.info(f"Agregado contexto BD: {contenido[:60]}...")

        conn.commit()

        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM conocimiento")
        count_final = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        logger.info(f"Proceso completado. {inserts} nuevos registros de contexto BD agregados.")
        logger.info(f"Total de registros en conocimiento: {count_final}")

        print(f"✅ Contexto de base de datos agregado exitosamente.")
        print(f"📊 Nuevos registros: {inserts}")
        print(f"📚 Total en base de conocimientos: {count_final}")

    except Exception as e:
        logger.error(f"Error poblando contexto BD: {e}")
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    poblar_contexto_bd()