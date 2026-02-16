#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar la tabla dbo.Factura
⚠️ ADVERTENCIA: Elimina TODOS los registros
"""

import pyodbc

CONNECTION_STRING = r'Driver={ODBC Driver 17 for SQL Server};Server=3431tajamarserver.database.windows.net;Database=facturas;UID=adm_alumno;PWD=Tajamar3431_;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

def clean_facturas():
    """Elimina todos los registros de la tabla Factura"""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Obtener cantidad de registros
        cursor.execute('SELECT COUNT(*) as total FROM dbo.Factura')
        total = cursor.fetchone()[0]
        
        if total == 0:
            print("✅ La tabla ya está vacía (0 registros)")
            conn.close()
            return
        
        print("=" * 80)
        print(f"⚠️  ADVERTENCIA: Vas a eliminar {total} registros")
        print("=" * 80)
        
        # Pedir confirmación
        respuesta = input(f"\n¿Estás seguro de que deseas eliminar {total} registros? (S/N): ").strip().upper()
        
        if respuesta != 'S':
            print("❌ Operación cancelada")
            conn.close()
            return
        
        # Eliminar registros
        cursor.execute('DELETE FROM dbo.Factura')
        conn.commit()
        
        # Resetear identity
        cursor.execute('DBCC CHECKIDENT ([dbo.Factura], RESEED, 0)')
        conn.commit()
        
        print(f"\n✅ Se han eliminado {total} registros correctamente")
        print("🔄 ID reiniciado a 0")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_facturas()
