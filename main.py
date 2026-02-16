#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import json
import re
from datetime import datetime
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

# Configuración
ENDPOINT = "https://discjnb22222.cognitiveservices.azure.com"
KEY = "3d7a4fc3a37e49de960d4038bc55bf1f"
MODEL_ID = "modelo_entrega_jnb"
CONNECTION_STRING = r'Driver={ODBC Driver 17 for SQL Server};Server=3431tajamarserver.database.windows.net;Database=facturas;UID=adm_alumno;PWD=Tajamar3431_;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
EMAIL_ALUMNO = "jaime.novillo@tajamar365.com"

# Campos esperados del modelo
CAMPOS_ESPERADOS = [
    "total", "Titular", "CIF/NIF", "Dirección de suministro:", "Comercializadora", 
    "CUPS", "Número Contrato", "Tipo", "Potencia contratada kW P1", "Potencia contratada kW P2",
    "Potencia contratada kW P3", "Potencia contratada kW P4", "Potencia contratada kW P5",
    "Potencia contratada kW P6", "Fecha Inicio", "Fecha Fin", "CP cliente", 
    "Poblacion cliente", "Provincia cliente", "Tarifa", "Consumo P1 kWh", 
    "Consumo P2 kWh", "Consumo P3 kWh", "Consumo P4 kWh", "Consumo P5 kWh", 
    "Consumo P6 kWh", "Días facturados", "Precio P1 kW/año", "Precio P2 kW/año", 
    "Precio P3 kW/año", "Precio P4 kW/año", "Precio P5 kW/año", "Precio P6 kW/año",
    "Precio P1 kW/día", "Precio P2 kW/día", "Precio P3 kW/día", "Precio P4 kW/día",
    "Precio P5 kW/día", "Precio P6 kW/día",
    "Precio E1 kWh", "Precio E2 kWh", "Precio E3 kWh", "Precio E4 kWh", 
    "Precio E5 kWh", "Precio E6 kWh", "NIF Comercializadora"
]

def _parse_number(text):
    """Convierte texto a número, manejando diferentes formatos"""
    if text is None: return None
    if isinstance(text, (int, float)): return float(text)
    try:
        clean = re.sub(r'[^\d.,-]', '', str(text))
        if ',' in clean and '.' in clean:
            clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            clean = clean.replace(',', '.')
        return float(clean) if clean else None
    except:
        return None

def extraer_valor_campo(field_data):
    """Extrae el valor de un campo con múltiples intentos"""
    if field_data is None:
        return None
    
    # Intentar campos directos
    for key in ['valueString', 'valueDate', 'valueNumber']:
        if key in field_data and field_data[key]:
            return field_data[key]
    
    # Intentar content
    if 'content' in field_data and field_data['content']:
        return field_data['content']
    
    # Intentar arrays
    if 'valueArray' in field_data and field_data['valueArray']:
        arr = field_data['valueArray']
        if isinstance(arr, list) and arr:
            item = arr[0]
            if isinstance(item, dict):
                for key in ['valueString', 'valueDate', 'valueNumber', 'content']:
                    if key in item and item[key]:
                        return item[key]
            else:
                return str(item)
    
    return None

def obtener_json_del_pdf(pdf_path):
    """Envía PDF a Azure y obtiene respuesta"""
    try:
        client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        request = AnalyzeDocumentRequest(bytes_source=pdf_data)
        poller = client.begin_analyze_document(model_id=MODEL_ID, body=request)
        result = poller.result(timeout=360)
        
        return result.as_dict()
    except Exception as e:
        print(f"❌ Error Azure: {e}")
        raise

def extraer_datos_factura(result_json, nombre_fichero):
    """Extrae datos del JSON de Azure con CAPA 1 (campos) y CAPA 2 (fallback)"""
    
    # Inicializar diccionario
    datos = {campo: None for campo in CAMPOS_ESPERADOS}
    
    content = result_json.get('content', '')
    
    # ========== CAPA 1: CAMPOS ESTRUCTURADOS DE AZURE ==========
    if 'documents' in result_json and result_json['documents']:
        fields = result_json['documents'][0].get('fields', {})
        
        # Extraer cada campo del JSON estructurado
        for campo in CAMPOS_ESPERADOS:
            if campo in fields:
                valor = extraer_valor_campo(fields[campo])
                
                if valor is not None:
                    # Limpieza específica para cada tipo de campo
                    if campo in ['Provincia cliente', 'Poblacion cliente']:
                        valor = re.sub(r'[\[\]\(\)]', '', str(valor)).strip()
                    elif 'Potencia contratada' in campo:
                        # Extraer solo el número de "P1=22kW;"
                        m = re.search(r'(\d+(?:[.,]\d+)?)', str(valor))
                        if m:
                            valor = _parse_number(m.group(1))
                    elif 'Precio' in campo or 'Consumo' in campo or 'total' in campo:
                        valor = _parse_number(valor)
                    elif 'Número' in campo or 'CUPS' in campo or 'Contrato' in campo:
                        valor = str(valor).strip()
                    elif campo == 'NIF Comercializadora':
                        # Extraer solo el NIF válido, descartando texto extra como ".Dom"
                        m = re.match(r'^([A-Z]\d{7}[A-Z0-9]|\d{8}[A-Z])', str(valor))
                        if m:
                            valor = m.group(1)
                        else:
                            valor = None
                    
                    datos[campo] = valor
    
    # ========== CAPA 2: FALLBACK CON TEXTO PLANO (REGEX) ==========
    
    # Titular (si falta)
    if not datos['Titular']:
        m = re.search(r'Titular:\s*\n\s*([^\n]+)', content, re.IGNORECASE)
        if m:
            datos['Titular'] = m.group(1).strip()
    
    # CIF/NIF (si falta)
    if not datos['CIF/NIF']:
        # Buscar el patrón del NIF cliente (no comercializadora)
        nifs = re.findall(r'\b([A-Z][0-9]{7}[A-Z0-9]|[0-9]{8}[A-Z])\b', content)
        if nifs and nifs[0] != 'B39540760':  # No es NIF comercializadora
            datos['CIF/NIF'] = nifs[0]
    
    # Dirección (si falta)
    if not datos['Dirección de suministro:']:
        m = re.search(r'(?:Dirección|Adreça).*?:\s*\n\s*([^\n]+)', content, re.IGNORECASE)
        if m:
            datos['Dirección de suministro:'] = m.group(1).strip()
    
    # CUPS (si falta)
    if not datos['CUPS']:
        m = re.search(r'(ES\d{18,20}[A-Z0-9]+)', content.replace(' ', ''))
        if m:
            datos['CUPS'] = m.group(1)
    
    # Número Contrato (si falta)
    if not datos['Número Contrato']:
        m = re.search(r'(?:Contrato|contracte|Contrato d\'accés)[:\s]+(\d{9,})', content, re.IGNORECASE)
        if m:
            datos['Número Contrato'] = m.group(1)
    
    # Tipo/Tarifa (si falta)
    if not datos['Tipo']:
        m = re.search(r'(?:Tipo|Tipus):\s*([^\n]+)', content, re.IGNORECASE)
        if m:
            datos['Tipo'] = m.group(1).strip()
    
    if not datos['Tarifa']:
        # Buscar patrón de tarifa específico: X.XTA, X.XTD, etc.
        patrones = [
            r'\b([0-9]+\.[0-9]+\s*T[A-Z])\b',  # 3.0TD, 2.0TA con o sin espacios
            r'\b([0-9][.,][0-9]T[A-Z])\b',      # 2,0TD o 2.0TD
            r'Tarifa[:\s]+([^\n,\r]+?)(?:\n|,|$)',  # "Tarifa: XYZ"
            r'(?:Tarif|Tarif)a[:\s]*\n\s*([^\n]+)',  # Nueva línea después de Tarifa:
        ]
        for patron in patrones:
            m = re.search(patron, content, re.IGNORECASE)
            if m:
                valor = m.group(1).strip()
                # Validar que tenga forma de tarifa
                if re.search(r'[0-9]+[.,][0-9]T[A-Z]|[0-9]T[A-Z]', valor):
                    datos['Tarifa'] = valor
                    break
    
    # Potencias (si faltan)
    for i in range(1, 7):
        if not datos[f'Potencia contratada kW P{i}']:
            m = re.search(f'P{i}\\s*=\\s*([0-9.,]+)\\s*[kK][wW]', content)
            if m:
                datos[f'Potencia contratada kW P{i}'] = _parse_number(m.group(1))
    
    # Fechas (si faltan)
    if not datos['Fecha Inicio'] or not datos['Fecha Fin']:
        fechas = re.findall(r'(\d{2}[./]\d{2}[./]\d{4})', content)
        fechas_limpias = []
        for f in fechas:
            try:
                if '.' in f:
                    d = datetime.strptime(f, '%d.%m.%Y')
                else:
                    d = datetime.strptime(f, '%d/%m/%Y')
                fechas_limpias.append(d.strftime('%Y-%m-%d'))
            except:
                pass
        
        if len(fechas_limpias) >= 2 and not datos['Fecha Inicio']:
            datos['Fecha Inicio'] = fechas_limpias[0]
            datos['Fecha Fin'] = fechas_limpias[-1]
    
    # Calcular Días facturados (si falta)
    if not datos['Días facturados'] and datos['Fecha Inicio'] and datos['Fecha Fin']:
        try:
            d1 = datetime.strptime(datos['Fecha Inicio'], '%Y-%m-%d')
            d2 = datetime.strptime(datos['Fecha Fin'], '%Y-%m-%d')
            datos['Días facturados'] = (d2 - d1).days + 1
        except:
            pass
    
    # Precios anuales (si faltan)
    for i in range(1, 7):
        if not datos[f'Precio P{i} kW/año']:
            m = re.search(f'P{i}\\].*?([0-9.,]+)\\s*€/kW(?:año|any)', content, re.DOTALL)
            if m:
                datos[f'Precio P{i} kW/año'] = _parse_number(m.group(1))
    
    # Calcular Precio P1-P6 kW/día a partir de precios anuales
    for i in range(1, 7):
        if datos[f'Precio P{i} kW/año']:
            # Solo calcular si aún no está calculado
            if not datos[f'Precio P{i} kW/día']:
                datos[f'Precio P{i} kW/día'] = round(datos[f'Precio P{i} kW/año'] / 365, 6)
        else:
            # Si no hay precio anual, poner 0.0 en diario
            if not datos[f'Precio P{i} kW/día']:
                datos[f'Precio P{i} kW/día'] = 0.0
    
    # Consumos y precios energía (si faltan)
    bloques = re.findall(r'(?:Consumo|Consum)\s+\[P(\d)\]\s+([0-9.,]+)\s*kWh\s*x\s*([0-9.,]+)\s*€/kW[nh]', content)
    for p, cons, prec in bloques:
        if not datos[f'Consumo P{p} kWh']:
            datos[f'Consumo P{p} kWh'] = int(_parse_number(cons))
        if not datos[f'Precio E{p} kWh']:
            datos[f'Precio E{p} kWh'] = _parse_number(prec)
    
    # Comercializadora y NIF (si faltan)
    if not datos['Comercializadora']:
        if 'Repsol' in content:
            datos['Comercializadora'] = 'Repsol Comercializadora de Electricidad y Gas, S.L.U.'
    
    if not datos['NIF Comercializadora']:
        if 'Repsol' in content:
            datos['NIF Comercializadora'] = 'B39540760'
    
    return datos

def guardar_en_base_datos(datos, nombre_fichero):
    """Inserta datos en SQL Server"""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Campos numéricos que deben ser 0.0 si son None
        campos_numericos = [
            'Potencia contratada kW P1', 'Potencia contratada kW P2', 'Potencia contratada kW P3',
            'Potencia contratada kW P4', 'Potencia contratada kW P5', 'Potencia contratada kW P6',
            'Días facturados', 'Precio P1 kW/día', 'Precio P2 kW/día', 'Precio P3 kW/día',
            'Precio P4 kW/día', 'Precio P5 kW/día', 'Precio P6 kW/día',
            'Precio E1 kWh', 'Precio E2 kWh', 'Precio E3 kWh', 'Precio E4 kWh', 'Precio E5 kWh', 'Precio E6 kWh',
            'Consumo P1 kWh', 'Consumo P2 kWh', 'Consumo P3 kWh', 'Consumo P4 kWh', 'Consumo P5 kWh', 'Consumo P6 kWh',
            'total'
        ]
        
        # Reemplazar None por 0.0 en campos numéricos
        for campo in campos_numericos:
            if datos[campo] is None:
                datos[campo] = 0.0
        
        query = """
        INSERT INTO [dbo].[Factura] (
            CorreoAlumno, Nombrefichero, NumFactura, FechaFactura, Cliente, [NIF cliente],
            Comercializadora, [NIF comercializadora], [Diercción cliente], [Población cliente],
            [Provincia cliente], [CP cliente], Tarifa, [Potencia contratada kW P1], [Potencia contratada kW P2],
            [Potencia contratada kW P3], [Potencia contratada kW P4], [Potencia contratada kW P5],
            [Potencia contratada kW P6], [Días factura], [Precio P1 kW/día], [Precio P2 kW/día], [Precio P3 kW/día],
            [Precio P4 kW/día], [Precio P5 kW/día], [Precio P6 kW/día],
            [Precio E1 kWh], [Precio E2 kWh], [Precio E3 kWh], [Precio E4 kWn], [Precio E5 kWh], [Precio E6 kWh],
            [Consumo P1 kWh], [Consumo P2 kWh], [Consumo P3 kWh], [Consumo P4 kWh], [Consumo P5 kWh], [Consumo P6 kWh],
            [Base imponible], TipoFactura, CUPS, Contrato
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        
        params = (
            EMAIL_ALUMNO, 
            nombre_fichero,
            datos['Número Contrato'],
            datos['Fecha Fin'] or datetime.now().date(),
            datos['Titular'],
            datos['CIF/NIF'],
            datos['Comercializadora'],
            datos['NIF Comercializadora'] or 'N/A',
            (datos['Dirección de suministro:'] or 'No especificada')[:150],
            datos['Poblacion cliente'],
            datos['Provincia cliente'],
            datos['CP cliente'],
            datos['Tarifa'],
            datos['Potencia contratada kW P1'],
            datos['Potencia contratada kW P2'],
            datos['Potencia contratada kW P3'],
            datos['Potencia contratada kW P4'],
            datos['Potencia contratada kW P5'],
            datos['Potencia contratada kW P6'],
            datos['Días facturados'],
            datos['Precio P1 kW/día'],
            datos['Precio P2 kW/día'],
            datos['Precio P3 kW/día'],
            datos['Precio P4 kW/día'],
            datos['Precio P5 kW/día'],
            datos['Precio P6 kW/día'],
            datos['Precio E1 kWh'],
            datos['Precio E2 kWh'],
            datos['Precio E3 kWh'],
            datos['Precio E4 kWh'],
            datos['Precio E5 kWh'],
            datos['Precio E6 kWh'],
            datos['Consumo P1 kWh'],
            datos['Consumo P2 kWh'],
            datos['Consumo P3 kWh'],
            datos['Consumo P4 kWh'],
            datos['Consumo P5 kWh'],
            datos['Consumo P6 kWh'],
            datos['total'],
            'Mercado',
            datos['CUPS'],
            datos['Número Contrato']
        )
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        print(f"  ✅ {nombre_fichero}: Insertado exitosamente")
        return True
        
    except Exception as e:
        print(f"  ❌ {nombre_fichero}: Error SQL - {e}")
        return False

def main():
    """Procesa todos los PDFs del directorio"""
    pdf_dir = Path(__file__).parent / "facturas"
    archivos = sorted(list(pdf_dir.glob("*.pdf")))
    
    print("=" * 80)
    print("PROCESAMIENTO DE FACTURAS - AZURE DOCUMENT INTELLIGENCE (Mejorado)")
    print("=" * 80)
    print(f"📄 Se encontraron {len(archivos)} archivo(s) PDF\n")
    
    aciertos = 0
    errores = 0
    
    for idx, pdf in enumerate(archivos, 1):
        print(f"\n[{idx}/{len(archivos)}] Procesando: {pdf.name}")
        print("-" * 80)
        
        try:
            # Obtener respuesta de Azure
            print(f"  🔄 Enviando a Azure Document Intelligence...")
            result = obtener_json_del_pdf(str(pdf))
            
            # Guardar JSON de respuesta
            json_file = pdf.parent / f"{pdf.stem}.response.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  💾 JSON guardado en {json_file.name}")
            
            # Extraer datos
            print(f"  📊 Extrayendo datos...")
            datos = extraer_datos_factura(result, pdf.name)
            
            # Mostrar algunos datos extraídos
            print(f"    ✓ Total: {datos['total']}")
            print(f"    ✓ Titular: {datos['Titular']}")
            print(f"    ✓ CUPS: {datos['CUPS']}")
            print(f"    ✓ Fecha: {datos['Fecha Fin']}")
            
            # Guardar en BD
            print(f"  💾 Guardando en base de datos...")
            if guardar_en_base_datos(datos, pdf.name):
                aciertos += 1
            else:
                errores += 1
                
        except Exception as e:
            print(f"  ❌ Error procesando {pdf.name}: {e}")
            errores += 1
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Procesadas correctamente: {aciertos}/{len(archivos)}")
    print(f"❌ Errores: {errores}/{len(archivos)}")
    print("=" * 80)

if __name__ == "__main__":
    main()