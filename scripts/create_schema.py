import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.connection import get_conn, release_conn

DDL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.areas_funcionales
(
    id_area serial NOT NULL,
    nombre_area character varying(100) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT areas_funcionales_pkey PRIMARY KEY (id_area)
);

CREATE TABLE IF NOT EXISTS public.asignacion_instalaciones
(
    id_asignacion serial NOT NULL,
    id_instalacion integer,
    id_materia integer,
    dia_semana character varying(20) COLLATE pg_catalog."default",
    hora_inicio time without time zone,
    hora_fin time without time zone,
    id_persona integer,
    CONSTRAINT asignacion_instalaciones_pkey PRIMARY KEY (id_asignacion)
);

CREATE TABLE IF NOT EXISTS public.bloques
(
    id_bloque serial NOT NULL,
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    id_campus integer,
    CONSTRAINT bloques_pkey PRIMARY KEY (id_bloque)
);

CREATE TABLE IF NOT EXISTS public.campus
(
    id_campus serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    direccion character varying(150) COLLATE pg_catalog."default",
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT campus_pkey PRIMARY KEY (id_campus)
);

CREATE TABLE IF NOT EXISTS public.estado_instalacion
(
    id_estado serial NOT NULL,
    nombre_estado character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT estado_instalacion_pkey PRIMARY KEY (id_estado)
);

CREATE TABLE IF NOT EXISTS public.horario_instalacion
(
    id_horario serial NOT NULL,
    id_instalacion integer,
    dia_semana character varying(20) COLLATE pg_catalog."default",
    hora_apertura time without time zone,
    hora_cierre time without time zone,
    CONSTRAINT horario_instalacion_pkey PRIMARY KEY (id_horario)
);

CREATE TABLE IF NOT EXISTS public.instalaciones
(
    id_instalacion serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    tipo_instalacion character varying(50) COLLATE pg_catalog."default",
    piso integer,
    capacidad integer,
    id_bloque integer,
    id_area integer,
    id_estado integer,
    CONSTRAINT instalaciones_pkey PRIMARY KEY (id_instalacion)
);

CREATE TABLE IF NOT EXISTS public.materias
(
    id_materia serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    creditos integer,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT materias_pkey PRIMARY KEY (id_materia)
);

CREATE TABLE IF NOT EXISTS public.persona_rol
(
    id_persona integer NOT NULL,
    id_rol integer NOT NULL,
    CONSTRAINT persona_rol_pkey PRIMARY KEY (id_persona, id_rol)
);

CREATE TABLE IF NOT EXISTS public.personas
(
    id_persona serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    documento character varying(20) COLLATE pg_catalog."default",
    correo character varying(100) COLLATE pg_catalog."default",
    telefono character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT personas_pkey PRIMARY KEY (id_persona),
    CONSTRAINT personas_documento_key UNIQUE (documento)
);

CREATE TABLE IF NOT EXISTS public.programa_materia
(
    id_programa integer NOT NULL,
    id_materia integer NOT NULL,
    CONSTRAINT programa_materia_pkey PRIMARY KEY (id_programa, id_materia)
);

CREATE TABLE IF NOT EXISTS public.programas
(
    id_programa serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    tipo_programa character varying(50) COLLATE pg_catalog."default",
    duracion_semestres integer,
    CONSTRAINT programas_pkey PRIMARY KEY (id_programa)
);

CREATE TABLE IF NOT EXISTS public.roles
(
    id_rol serial NOT NULL,
    nombre_rol character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT roles_pkey PRIMARY KEY (id_rol)
);

ALTER TABLE IF EXISTS public.asignacion_instalaciones
    ADD CONSTRAINT asignacion_instalaciones_id_instalacion_fkey FOREIGN KEY (id_instalacion)
    REFERENCES public.instalaciones (id_instalacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.asignacion_instalaciones
    ADD CONSTRAINT asignacion_instalaciones_id_materia_fkey FOREIGN KEY (id_materia)
    REFERENCES public.materias (id_materia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.asignacion_instalaciones
    ADD CONSTRAINT fk_profesor FOREIGN KEY (id_persona)
    REFERENCES public.personas (id_persona) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.bloques
    ADD CONSTRAINT bloques_id_campus_fkey FOREIGN KEY (id_campus)
    REFERENCES public.campus (id_campus) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.horario_instalacion
    ADD CONSTRAINT horario_instalacion_id_instalacion_fkey FOREIGN KEY (id_instalacion)
    REFERENCES public.instalaciones (id_instalacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.instalaciones
    ADD CONSTRAINT instalaciones_id_area_fkey FOREIGN KEY (id_area)
    REFERENCES public.areas_funcionales (id_area) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.instalaciones
    ADD CONSTRAINT instalaciones_id_bloque_fkey FOREIGN KEY (id_bloque)
    REFERENCES public.bloques (id_bloque) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.instalaciones
    ADD CONSTRAINT instalaciones_id_estado_fkey FOREIGN KEY (id_estado)
    REFERENCES public.estado_instalacion (id_estado) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.persona_rol
    ADD CONSTRAINT persona_rol_id_persona_fkey FOREIGN KEY (id_persona)
    REFERENCES public.personas (id_persona) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.persona_rol
    ADD CONSTRAINT persona_rol_id_rol_fkey FOREIGN KEY (id_rol)
    REFERENCES public.roles (id_rol) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.programa_materia
    ADD CONSTRAINT programa_materia_id_materia_fkey FOREIGN KEY (id_materia)
    REFERENCES public.materias (id_materia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.programa_materia
    ADD CONSTRAINT programa_materia_id_programa_fkey FOREIGN KEY (id_programa)
    REFERENCES public.programas (id_programa) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
"""

def create_schema():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(DDL)
        conn.commit()
        print("Esquema ERD creado/actualizado exitosamente.")
    except Exception as e:
        conn.rollback()
        print(f"Error creando esquema: {e}")
        raise
    finally:
        cur.close()
        release_conn(conn)

if __name__ == "__main__":
    create_schema()