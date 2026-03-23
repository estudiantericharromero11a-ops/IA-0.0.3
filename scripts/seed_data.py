import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.queries import get_connection

def seed_data():
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Insertar datos de ejemplo
        cur.execute("""
            INSERT INTO campus (nombre, direccion, descripcion) VALUES
            ('Campus Principal', 'Calle 123', 'Campus principal de la universidad'),
            ('Campus Norte', 'Avenida 456', 'Campus norte')
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO bloques (nombre, descripcion, id_campus) VALUES
            ('Bloque A', 'Bloque administrativo', 1),
            ('Bloque B', 'Bloque académico', 1)
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO areas_funcionales (nombre_area, descripcion) VALUES
            ('Académica', 'Área para clases'),
            ('Administrativa', 'Área administrativa')
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO estado_instalacion (nombre_estado, descripcion) VALUES
            ('Activa', 'Instalación operativa'),
            ('Inactiva', 'Instalación fuera de servicio')
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO instalaciones (nombre, tipo_instalacion, piso, capacidad, id_bloque, id_area, id_estado) VALUES
            ('Aula 101', 'Aula', 1, 50, 1, 1, 1),
            ('Oficina 201', 'Oficina', 2, 10, 2, 2, 1)
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO materias (nombre, creditos, descripcion) VALUES
            ('Matemáticas', 3, 'Curso de matemáticas básicas'),
            ('Programación', 4, 'Introducción a la programación')
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO personas (nombre, documento, correo, telefono) VALUES
            ('Juan Pérez', '12345678', 'juan@univ.edu', '555-1234'),
            ('María García', '87654321', 'maria@univ.edu', '555-5678')
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO roles (nombre_rol, descripcion) VALUES
            ('Estudiante', 'Rol de estudiante'),
            ('Profesor', 'Rol de profesor'),
            ('Administrativo', 'Rol administrativo')
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO programas (nombre, tipo_programa, duracion_semestres) VALUES
            ('Ingeniería de Sistemas', 'Pregrado', 10),
            ('Administración', 'Pregrado', 8)
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO persona_rol (id_persona, id_rol) VALUES
            (1, 2),  -- Juan es profesor
            (2, 2)   -- María es profesora
            ON CONFLICT DO NOTHING;
        """)
        cur.execute("""
            INSERT INTO programa_materia (id_programa, id_materia) VALUES
            (1, 1),  -- Ingeniería tiene Matemáticas
            (1, 2)   -- Ingeniería tiene Programación
            ON CONFLICT DO NOTHING;
        """)
        conn.commit()
        print("Datos de ejemplo insertados exitosamente.")
    except Exception as e:
        conn.rollback()
        print(f"Error insertando datos: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_data()