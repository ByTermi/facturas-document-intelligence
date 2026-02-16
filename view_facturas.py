#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ver el contenido de la tabla dbo.Factura
"""

import pyodbc
from tabulate import tabulate

CONNECTION_STRING = r'Driver={ODBC Driver 17 for SQL Server};Server=3431tajamarserver.database.windows.net;Database=facturas;UID=adm_alumno;PWD=Tajamar3431_;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

def view_facturas():
    """Muestra todos los registros de la tabla Factura"""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Obtener cantidad de registros
        cursor.execute('SELECT COUNT(*) as total FROM dbo.Factura')
        total = cursor.fetchone()[0]
        
        print("=" * 100)
        print(f"📊 TABLA: dbo.Factura ({total} registros)")
        print("=" * 100)
        
        # Obtener todos los registros
        cursor.execute('''
            SELECT 
                id_factura, Nombrefichero, Cliente, NumFactura, Tarifa, 
                [Potencia contratada kW P1], [Precio P1 kW/día], 
                [Consumo P1 kWh], [Base imponible]
            FROM dbo.Factura
            ORDER BY id_factura DESC
        ''')
        
        rows = cursor.fetchall()
        
        if rows:
            # Preparar tabla
            headers = ['ID', 'Archivo', 'Cliente', 'NumFactura', 'Tarifa', 
                      'kW P1', '€/kW/día P1', 'kWh P1', 'Total €']
            
            data = [
                [
                    row[0],
                    row[1],
                    row[2][:30] if row[2] else '-',
                    row[3],
                    row[4] or 'NULL',
                    f"{row[5]:.2f}" if row[5] is not None else '0.00',
                    f"{row[6]:.6f}" if row[6] is not None else '0.000000',
                    f"{row[7]}" if row[7] is not None else '0',
                    f"{row[8]:.2f}" if row[8] is not None else '0.00'
                ]
                for row in rows
            ]
            
            print(tabulate(data, headers=headers, tablefmt='grid'))
        else:
            print("❌ No hay registros en la tabla")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_facturas()
