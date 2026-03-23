#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de ejemplo.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.queries import ejecutar_query

def poblar_datos_ejemplo():
    """Inserta datos de ejemplo en las tablas principales."""

    queries = [
        # Campus
        """
        INSERT INTO campus (nombre, direccion, descripcion) VALUES
        ('Campus Principal', 'Calle Universidad 123', 'Campus principal de la universidad'),
        ('Campus Norte', 'Avenida Norte 456', 'Campus norte con facultad de ingeniería')
        ON CONFLICT DO NOTHING;
        """,

        # Bloques
        """
        INSERT INTO bloques (nombre, descripcion, id_campus) VALUES
        ('Bloque A', 'Edificio administrativo', 1),
        ('Bloque B', 'Aulas de clases', 1),
        ('Bloque C', 'Laboratorios', 2)
        ON CONFLICT DO NOTHING;
        """,

        # Áreas funcionales
        """
        INSERT INTO areas_funcionales (nombre_area, descripcion) VALUES
        ('Aula', 'Espacio para clases teóricas'),
        ('Laboratorio', 'Espacio para prácticas'),
        ('Oficina', 'Espacio administrativo')
        ON CONFLICT DO NOTHING;
        """,

        # Estados de instalación
        """
        INSERT INTO estado_instalacion (nombre_estado, descripcion) VALUES
        ('Disponible', 'Instalación disponible para uso'),
        ('En mantenimiento', 'Instalación en mantenimiento'),
        ('Ocupada', 'Instalación actualmente en uso')
        ON CONFLICT DO NOTHING;
        """,

        # Instalaciones
        """
        INSERT INTO instalaciones (nombre, tipo_instalacion, piso, capacidad, id_bloque, id_area, id_estado) VALUES
        ('Aula 101', 'Aula', 1, 50, 2, 1, 1),
        ('Aula 102', 'Aula', 1, 40, 2, 1, 1),
        ('Laboratorio 201', 'Laboratorio', 2, 25, 3, 2, 1),
        ('Oficina 301', 'Oficina', 3, 5, 1, 3, 1)
        ON CONFLICT DO NOTHING;
        """,

        # Roles
        """
        INSERT INTO roles (nombre_rol, descripcion) VALUES
        ('Profesor', 'Docente de la universidad'),
        ('Estudiante', 'Estudiante matriculado'),
        ('Administrativo', 'Personal administrativo')
        ON CONFLICT DO NOTHING;
        """,

        # Personas
        """
        INSERT INTO personas (nombre, documento, correo, telefono) VALUES
        ('Dr. Juan Pérez', '12345678', 'juan.perez@universidad.edu', '555-0101'),
        ('Dra. María García', '87654321', 'maria.garcia@universidad.edu', '555-0102'),
        ('Carlos López', '11223344', 'carlos.lopez@universidad.edu', '555-0103')
        ON CONFLICT DO NOTHING;
        """,

        # Persona-Rol
        """
        INSERT INTO persona_rol (id_persona, id_rol) VALUES
        (1, 1), (2, 1), (3, 2)
        ON CONFLICT DO NOTHING;
        """,

        # Materias
        """
        INSERT INTO materias (nombre, creditos, descripcion) VALUES
        ('Matemáticas', 3, 'Curso de matemáticas básicas'),
        ('Física', 4, 'Principios de física'),
        ('Programación', 3, 'Introducción a la programación'),
        ('Base de Datos', 3, 'Diseño y administración de bases de datos')
        ON CONFLICT DO NOTHING;
        """,

        # Programas
        """
        INSERT INTO programas (nombre, tipo_programa, duracion_semestres) VALUES
        ('Ingeniería de Sistemas', 'Pregrado', 10),
        ('Administración', 'Pregrado', 8)
        ON CONFLICT DO NOTHING;
        """,

        # Programa-Materia
        """
        INSERT INTO programa_materia (id_programa, id_materia) VALUES
        (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 4)
        ON CONFLICT DO NOTHING;
        """,

        # Asignación de instalaciones (ejemplo de horario)
        """
        INSERT INTO asignacion_instalaciones (id_instalacion, id_materia, dia_semana, hora_inicio, hora_fin, id_persona) VALUES
        (1, 1, 'Lunes', '08:00', '10:00', 1),
        (1, 2, 'Martes', '10:00', '12:00', 2),
        (2, 3, 'Miércoles', '14:00', '16:00', 1),
        (3, 4, 'Jueves', '08:00', '11:00', 2)
        ON CONFLICT DO NOTHING;
        """
    ]

    for i, query in enumerate(queries, 1):
        try:
            result = ejecutar_query(query)
            if 'error' in result:
                print(f"❌ Error en query {i}: {result['error']}")
            else:
                print(f"✅ Query {i} ejecutado correctamente")
        except Exception as e:
            print(f"❌ Error ejecutando query {i}: {e}")

if __name__ == "__main__":
    print("🔄 Poblando base de datos con datos de ejemplo...")
    poblar_datos_ejemplo()
    print("✅ Proceso completado")