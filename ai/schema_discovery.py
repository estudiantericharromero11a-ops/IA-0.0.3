#!/usr/bin/env python3
"""
Auto-descubrimiento del esquema de la BD.
Lee automáticamente tablas, columnas y relaciones.
"""

import os
from dotenv import load_dotenv
import psycopg
from database.queries import get_connection

def obtener_esquema_completo():
    """Lee automáticamente el esquema de la BD."""
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Obtener todas las tablas
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                # dict_row returns dicts, so we access by key
                tablas = [row['table_name'] for row in cursor.fetchall()]

                # 2. Para cada tabla, obtener columnas y tipos
                esquema = {}
                for tabla in tablas:
                    cursor.execute("""
                        SELECT column_name, data_type, column_default, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position;
                    """, (tabla,))
                    
                    columnas = []
                    for row in cursor.fetchall():
                        columnas.append({
                            'nombre': row['column_name'],
                            'tipo': row['data_type'],
                            'default': row['column_default'],
                            'nullable': row['is_nullable'] == 'YES'
                        })
                    
                    esquema[tabla] = columnas

                return esquema

    except Exception as e:
        print(f"Error leyendo esquema: {type(e).__name__}: {e}")
        return {}

def obtener_relaciones():
    """Lee las relaciones (foreign keys) de la BD."""
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        tc.table_name, 
                        kcu.column_name,
                        ccu.table_name AS referenced_table_name,
                        ccu.column_name AS referenced_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY tc.table_name;
                """)
                
                relaciones = {}
                for row in cursor.fetchall():
                    tabla = row['table_name']
                    if tabla not in relaciones:
                        relaciones[tabla] = []
                    
                    relaciones[tabla].append({
                        'columna': row['column_name'],
                        'referencia_tabla': row['referenced_table_name'],
                        'referencia_columna': row['referenced_column_name']
                    })
                
                return relaciones

    except Exception as e:
        print(f"Error leyendo relaciones: {e}")
        return {}

def obtener_datos_muestra(tabla, limite=5):
    """Obtiene datos de ejemplo para una tabla."""
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {tabla} LIMIT {limite};")
                return cursor.fetchall()
    except:
        return []

if __name__ == "__main__":
    print("=== ESQUEMA AUTO-DESCUBIERTO ===\n")
    
    esquema = obtener_esquema_completo()
    relaciones = obtener_relaciones()
    
    # Mostrar esquema
    for tabla, columnas in esquema.items():
        print(f"\n📋 TABLA: {tabla}")
        for col in columnas:
            print(f"   - {col['nombre']}: {col['tipo']}")
        
        if tabla in relaciones:
            print(f"   🔗 Relaciones:")
            for rel in relaciones[tabla]:
                print(f"      {rel['columna']} → {rel['referencia_tabla']}.{rel['referencia_columna']}")
