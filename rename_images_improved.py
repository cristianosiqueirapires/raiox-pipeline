#!/usr/bin/env python3
"""
Script melhorado de nomenclatura baseado na ordem das buscas realizadas
"""

import os
import shutil
from PIL import Image
import json

def rename_images_by_search_order():
    """
    Renomeia imagens baseado na ordem das buscas realizadas:
    1-8: Nobel Biocare Replace
    9-16: Straumann Bone Level  
    17-24: Neodent Drive
    25-32: Zimmer
    """
    
    source_dir = "/home/ubuntu/upload/search_images"
    target_dir = "/home/ubuntu/implant_images"
    
    # Limpar diretório de destino
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    
    # Obter lista de arquivos ordenada
    files = sorted([f for f in os.listdir(source_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    
    processed_images = []
    
    # Definir mapeamento baseado na ordem das buscas
    mappings = [
        # Nobel Biocare Replace (primeiros 8)
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "4.3mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "3.5mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "4.0mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "4.3mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "5.0mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "4.3mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "3.5mm"},
        {"fabricante": "NOBEL", "modelo": "REPLACE", "diametro": "4.0mm"},
        
        # Straumann Bone Level (próximos 8)
        {"fabricante": "STRAUMANN", "modelo": "BL", "diametro": "3.3mm"},
        {"fabricante": "STRAUMANN", "modelo": "BLT", "diametro": "2.9mm"},
        {"fabricante": "STRAUMANN", "modelo": "BLX", "diametro": "4.5mm"},
        {"fabricante": "STRAUMANN", "modelo": "BLT", "diametro": "2.9mm"},
        {"fabricante": "STRAUMANN", "modelo": "BL", "diametro": "4.1mm"},
        {"fabricante": "STRAUMANN", "modelo": "BL", "diametro": "4.8mm"},
        {"fabricante": "STRAUMANN", "modelo": "BL", "diametro": "3.3mm"},
        {"fabricante": "STRAUMANN", "modelo": "TLX", "diametro": "4.1mm"},
        
        # Neodent (próximos 8)
        {"fabricante": "NEODENT", "modelo": "GRAND_MORSE", "diametro": "4.0mm"},
        {"fabricante": "NEODENT", "modelo": "DRIVE", "diametro": "3.5mm"},
        {"fabricante": "NEODENT", "modelo": "HELIX", "diametro": "4.0mm"},
        {"fabricante": "NEODENT", "modelo": "DRIVE", "diametro": "4.3mm"},
        {"fabricante": "NEODENT", "modelo": "TITAMAX", "diametro": "3.75mm"},
        {"fabricante": "NEODENT", "modelo": "GRAND_MORSE", "diametro": "4.0mm"},
        {"fabricante": "NEODENT", "modelo": "DRIVE", "diametro": "3.5mm"},
        {"fabricante": "NEODENT", "modelo": "HELIX", "diametro": "4.0mm"},
        
        # Zimmer (próximos 8)
        {"fabricante": "ZIMMER", "modelo": "TSV", "diametro": "4.7mm"},
        {"fabricante": "ZIMMER", "modelo": "TSV", "diametro": "4.7mm"},
        {"fabricante": "ZIMMER", "modelo": "TSV", "diametro": "4.7mm"},
        {"fabricante": "ZIMMER", "modelo": "SCREW_VENT", "diametro": "4.0mm"},
        {"fabricante": "ZIMMER", "modelo": "TSV", "diametro": "4.7mm"},
        {"fabricante": "ZIMMER", "modelo": "SWISS_PLUS", "diametro": "4.1mm"},
        {"fabricante": "ZIMMER", "modelo": "TSV", "diametro": "3.7mm"},
        {"fabricante": "ZIMMER", "modelo": "SCREW_VENT", "diametro": "5.0mm"}
    ]
    
    print(f"Processando {len(files)} imagens...")
    
    for i, filename in enumerate(files):
        if i >= len(mappings):
            # Para imagens extras, usar padrão genérico
            mapping = {"fabricante": "GENERIC", "modelo": "IMPLANT", "diametro": "4.0mm"}
        else:
            mapping = mappings[i]
        
        source_path = os.path.join(source_dir, filename)
        
        # Criar nome padronizado
        new_name = f"{mapping['fabricante']}_{mapping['modelo']}_{mapping['diametro']}_{i+1:02d}.jpg"
        target_path = os.path.join(target_dir, new_name)
        
        try:
            # Processar imagem
            with Image.open(source_path) as img:
                # Converter para RGB se necessário
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar para 224x224 (padrão CLIP)
                img_resized = img.resize((224, 224), Image.Resampling.LANCZOS)
                
                # Salvar
                img_resized.save(target_path, 'JPEG', quality=95)
            
            processed_images.append({
                "original_filename": filename,
                "new_filename": new_name,
                "fabricante": mapping['fabricante'],
                "modelo": mapping['modelo'],
                "diametro": mapping['diametro'],
                "path": target_path,
                "search_order": i + 1
            })
            
            print(f"{i+1:2d}. {filename} -> {new_name}")
            
        except Exception as e:
            print(f"Erro processando {filename}: {str(e)}")
    
    # Salvar metadados
    metadata_file = "/home/ubuntu/processed_images_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(processed_images, f, indent=2)
    
    print(f"\nProcessamento concluído!")
    print(f"Total de imagens processadas: {len(processed_images)}")
    print(f"Metadados salvos em: {metadata_file}")
    
    # Resumo por fabricante
    fabricantes_count = {}
    for img in processed_images:
        fab = img['fabricante']
        fabricantes_count[fab] = fabricantes_count.get(fab, 0) + 1
    
    print(f"\nResumo por fabricante:")
    for fab, count in fabricantes_count.items():
        print(f"- {fab}: {count} imagens")
    
    return processed_images

if __name__ == "__main__":
    processed = rename_images_by_search_order()

