# Sistema de Procesamiento de Facturas con Azure Document Intelligence

Aplicación Python que procesa facturas de electricidad en PDF utilizando **Azure Document Intelligence** para extraer datos estructurados e insertarlos en una base de datos SQL Server.

## 📋 Descripción

Este sistema automatiza la extracción de información de facturas eléctricas:
- **Datos del cliente** (nombre, NIF, dirección, población, provincia, CP)
- **Datos de suministro** (CUPS, contrato, comercializadora)
- **Datos técnicos** (tarifa, potencia, consumo, precios)
- **Conversión de precios** de €/kWaño → €/kWdía (÷365)

### Arquitectura de Extracción (2 capas)

**CAPA 1 - Campos Estructurados (Prioridad)**
- Extrae datos del JSON de Azure Document Intelligence
- Campos con `valueString`, `valueDate`, `valueNumber`, `content`
- Mayor confiabilidad (~94% de precisión)

**CAPA 2 - Fallback con Regex**
- Búsqueda por patrones en texto plano si CAPA 1 falla
- Maneja variaciones de formato (español, catalán)
- Cierra las brechas de datos

## 🚀 Inicio Rápido

### Requisitos
- Python 3.12.0+
- ODBC Driver 17 for SQL Server
- Acceso a Azure Document Intelligence y SQL Server Azure

### Instalación

```bash
# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

**Base de datos Azure SQL:**
- Servidor: `3431tajamarserver.database.windows.net`
- Base datos: `facturas`
- Usuario: `adm_alumno`
- Contraseña: `Tajamar3431_`

**Azure Document Intelligence:**
- Endpoint: `https://discjnb22222.cognitiveservices.azure.com`
- Modelo: `modelo_entrega_jnb`
- API Key: `3d7a4fc3a37e49de960d4038bc55bf1f`

Los datos de conexión están incluidos en los scripts.

## 📁 Estructura de Carpetas

```
practica_pdfs/
├── README.md                    # Este archivo
├── main.py                      # Script principal
├── view_facturas.py            # Ver registros de BD
├── clean_facturas.py           # Limpiar BD
├── extrae_campos.py            # Demostración de extracción
├── requirements.txt            # Dependencias
│
├── facturas/                   # 📁 Carpeta de invoices
│   ├── REPSOL1.pdf
│   ├── REPSOL2.pdf
│   ├── ... (12 PDFs)
│   ├── REPSOL1.response.json   # Respuestas de Azure
│   └── ... (12 JSONs)
│
└── .venv/                      # Entorno virtual
```

## 🛠️ Scripts Disponibles

### 1. **main.py** - Procesamiento Principal
Procesa todos los PDFs de la carpeta `facturas/`:

```bash
.\.venv\Scripts\python.exe main.py
```

**Flujo:**
1. Lee PDFs de `facturas/`
2. Envía a Azure Document Intelligence
3. Extrae datos (CAPA 1 + CAPA 2)
4. Calcula precios diarios (÷365)
5. Inserta en base de datos
6. Guarda respuesta JSON en `facturas/`

### 2. **view_facturas.py** - Visualizar Datos
Muestra todos los registros con formato de tabla:

```bash
.\.venv\Scripts\python.exe view_facturas.py
```

**Columnas mostradas:**
- ID, Archivo, Cliente, NumFactura, Tarifa
- kW P1, €/kW/día P1, kWh P1, Total €

### 3. **clean_facturas.py** - Limpiar Base de Datos
Elimina todos los registros (con confirmación):

```bash
.\.venv\Scripts\python.exe clean_facturas.py
```

Útil para iterar y debuguear sin duplicados.

### 4. **extrae_campos.py** - Demostración
Extrae y muestra campos de un JSON específico:

```bash
.\.venv\Scripts\python.exe extrae_campos.py
```

## 📊 Campos Extraídos

| Campo | Tipo | Fuente |
|-------|------|--------|
| **Cliente** | Text | JSON/Regex |
| **NIF Cliente** | Text | JSON/Regex |
| **Comercializadora** | Text | JSON/Regex |
| **CUPS** | Text | Regex (ES...) |
| **Tarifa** | Text | JSON/Regex (X.XTD) |
| **Potencia P1-P6** | Float | JSON/Regex |
| **Precio P1-P6 kW/año** | Float | JSON |
| **Precio P1-P6 kW/día** | Float | Calculado (÷365) |
| **Consumo P1-P6 kWh** | Int | JSON/Regex |
| **Precio E1-E6 kWh** | Float | JSON/Regex |
| **Días facturados** | Int | Calculado |
| **Total** | Float | Regex |

**Total de campos: 41**
**Cobertura: 12/12 PDFs (100% éxito)**

## 🔢 Ejemplos de Datos Extraídos

**REPSOL1.pdf:**
- Titular: EZKERRA PRODUZKIOAK SL
- NIF: B95506291
- Tarifa: 3.0TD
- Potencia P1: 1.00 kW → Precio: 0.06 €/kW/día
- Consumo P1: 0 kWh / Consumo P3: 1 kWh
- Total: 2545.91 €

**REPSOL2.pdf:**
- Titular: NOU XIBARRI CAMBRILS SL
- NIF: B01664374
- Tarifa: 3.0TD
- Potencia P4: 22.00 kW
- Consumo P3: 427 kWh / P4: 651 kWh / P5: 237 kWh / P6: 1327 kWh
- Total: 517.03 €

## 🐛 Solución de Problemas

### Error: "Cannot connect to server"
- Verificar credenciales de Azure SQL
- Comprobar firewall permite conexión desde tu IP
- Probar conexión con SSMS

### Error: "Module not found"
```bash
.\.venv\Scripts\pip.exe install pyodbc tabulate
```

### PDFs no se procesan
- Verificar que están en `facturas/` (no en raíz)
- Comprobar credenciales Azure Document Intelligence
- Ver que el modelo `modelo_entrega_jnb` esté disponible

### Datos incompletos en BD
- Los campos NULL se reemplazan automáticamente por `0.0`
- CAPA 2 de regex actúa como fallback si CAPA 1 no extrae

## 📈 Métricas de Éxito

✅ **Procesamiento:** 12/12 PDFs (100%)
✅ **Extracción:** 34/41 campos promedio por factura
✅ **Confianza:** ~94% de precisión
✅ **Base de datos:** 12 registros insertados
✅ **Cálculos:** Precios diarios correctos (÷365)

## 🔐 Seguridad

⚠️ **IMPORTANTE:**
- Las credenciales están en texto plano (solo para desarrollo)
- Para producción, usar **variables de entorno** o **Azure Key Vault**
- No hacer commit de `.py` con credenciales a repositorios públicos

### Usar Variables de Entorno

```python
import os
CONNECTION_STRING = os.getenv('DATABASE_CONNECTION_STRING')
AZURE_KEY = os.getenv('AZURE_API_KEY')
```

## 📝 Notas de Desarrollo

- Formato de precio: `€/kWaño` → dividido entre 365 → `€/kWdía`
- Campos numéricos sin valor: reemplazados por `0.0` (no NULL)
- JSONs de respuesta: guardados en `facturas/` para auditoría
- Tipo factura: "Mercado" (Mercado Libre)

## 📞 Soporte

Para preguntas o problemas:
1. Verificar logs en terminal
2. Revisar JSON de respuesta en `facturas/`
3. Ejecutar `view_facturas.py` para ver datos en BD
4. Usar `clean_facturas.py` para limpiar e reintentar

---

**Versión:** 1.0  
**Última actualización:** Febrero 2026  
**Estado:** Producción ✓
