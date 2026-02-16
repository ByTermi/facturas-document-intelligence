#!/usr/bin/env python3
import json
from pathlib import Path

pdf_dir = Path(__file__).parent
for json_file in sorted(pdf_dir.glob("*.response.json")):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if data.get('documents') and data['documents'][0].get('fields'):
        fields = data['documents'][0]['fields']
        if 'Tarifa' in fields:
            tarifa = fields['Tarifa'].get('valueString', fields['Tarifa'].get('content', 'SIN VALOR'))
            print(f"✓ {json_file.name}: Tarifa = {tarifa}")
        else:
            print(f"✗ {json_file.name}: NO ENCONTRADO")
