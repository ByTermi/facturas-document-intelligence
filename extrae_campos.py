#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

# Campos que queremos extraer
CAMPOS = [
    "total",
    "Titular",
    "CIF/NIF",
    "Dirección de suministro:",
    "Comercializadora",
    "CUPS",
    "Número Contrato",
    "Tipo",
    "Potencia contratada kW P1",
    "Potencia contratada kW P2",
    "Potencia contratada kW P3",
    "Potencia contratada kW P4",
    "Potencia contratada kW P5",
    "Potencia contratada kW P6",
    "Fecha Inicio",
    "Fecha Fin",
    "CP cliente",
    "Poblacion cliente",
    "Provincia cliente",
    "Tarifa",
    "Consumo P1 kWh",
    "Consumo P2 kWh",
    "Consumo P3 kWh",
    "Consumo P4 kWh",
    "Consumo P5 kWh",
    "Consumo P6 kWh",
    "Días facturados",
    "Precio P1 kW/año",
    "Precio P2 kW/año",
    "Precio P3 kW/año",
    "Precio P4 kW/año",
    "Precio P5 kW/año",
    "Precio P6 kW/año",
    "Precio P1 kW/día",
    "Precio E1 kWh",
    "Precio E2 kWh",
    "Precio E3 kWh",
    "Precio E6 kWh",
    "Precio E4 kWh",
    "Precio E5 kWh",
    "NIF Comercializadora"
]

def extraer_valores(archivo_json):
    """
    Extrae los valores de los campos del archivo JSON de respuesta
    """
    with open(archivo_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # La estructura es: data['documents'][0]['fields']
    if 'documents' not in data or not data['documents']:
        print("❌ No se encontraron documentos en el JSON")
        return
    
    fields = data['documents'][0].get('fields', {})
    
    print("=" * 80)
    print("EXTRACCIÓN DE VALORES - REPSOL2.pdf")
    print("=" * 80)
    print()
    
    # Diccionario para almacenar los valores extraidos
    valores_extraidos = {}
    
    for campo in CAMPOS:
        if campo in fields:
            field_data = fields[campo]
            
            # Intentar obtener el valor en múltiples formatos
            valor = None
            tipo = None
            
            # Primero intentar formatos directos
            if 'valueString' in field_data and field_data['valueString']:
                valor = field_data['valueString']
                tipo = 'string'
            elif 'valueDate' in field_data and field_data['valueDate']:
                valor = field_data['valueDate']
                tipo = 'date'
            elif 'valueNumber' in field_data and field_data['valueNumber'] is not None:
                valor = field_data['valueNumber']
                tipo = 'number'
            elif 'content' in field_data and field_data['content']:
                valor = field_data['content']
                tipo = 'content'
            
            # Si aún no tiene valor, buscar en sustitutos
            if valor is None:
                # Algunos campos pueden ser arrays de objetos
                if 'valueArray' in field_data and field_data['valueArray']:
                    valor_array = field_data['valueArray']
                    if valor_array and isinstance(valor_array, list) and valor_array[0]:
                        item = valor_array[0]
                        if isinstance(item, dict):
                            if 'valueString' in item:
                                valor = item['valueString']
                            elif 'content' in item:
                                valor = item['content']
                            elif 'valueNumber' in item:
                                valor = item['valueNumber']
                        else:
                            valor = str(item)
                    tipo = 'array'
            
            # Si no hay valor, mostrar el tipo del campo
            if valor is None:
                tipo_campo = field_data.get('type', 'unknown')
                print(f"❓ {campo:40} | Tipo: {tipo_campo:10} | [Sin valor extraible]")
            else:
                valores_extraidos[campo] = valor
                confianza = field_data.get('confidence', 'N/A')
                confianza_str = f"{confianza:.1%}" if isinstance(confianza, (int, float)) else str(confianza)
                print(f"✓ {campo:40} | {str(valor):30} | Confianza: {confianza_str}")
        else:
            print(f"✗ {campo:40} | [NO ENCONTRADO EN JSON]")
    
    print()
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Campos encontrados: {len(valores_extraidos)}/{len(CAMPOS)}")
    print()
    
    # Mostrar un diccionario ordenado de valores
    print("Diccionario de valores extraidos:")
    print("{")
    for campo in CAMPOS:
        if campo in valores_extraidos:
            valor = valores_extraidos[campo]
            if isinstance(valor, str):
                print(f'    "{campo}": "{valor}",')
            else:
                print(f'    "{campo}": {valor},')
    print("}")
    
    return valores_extraidos


if __name__ == "__main__":
    # Ruta del archivo JSON
    archivo_json = Path(__file__).parent / "REPSOL2.response.json"
    
    if archivo_json.exists():
        valores = extraer_valores(str(archivo_json))
    else:
        print(f"❌ Archivo no encontrado: {archivo_json}")
