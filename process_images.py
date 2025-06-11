#!/usr/bin/env python3
"""
Script de processamento e padronização de nomenclatura de implantes
Baseado no Manual de Coleta e Padronização de Imagens Reais para o Raiox AI
"""

import os
import re
import shutil
from PIL import Image
import json

def analyze_and_rename_images():
    """
    Analisa as imagens coletadas e aplica nomenclatura padronizada
    Formato: FABRICANTE_MODELO_DIAMETRO.jpg
    """
    
    source_dir = "/home/ubuntu/upload/search_images"
    target_dir = "/home/ubuntu/implant_images"
    
    # Mapeamento de fabricantes
    fabricantes = {
        "nobel": "NOBEL",
        "nobelbiocare": "NOBEL", 
        "straumann": "STRAUMANN",
        "neodent": "NEODENT",
        "zimmer": "ZIMMER",
        "zimvie": "ZIMMER"
    }
    
    # Mapeamento de modelos
    modelos = {
        "replace": "REPLACE",
        "active": "ACTIVE",
        "conical": "CC",
        "bone": "BL",
        "bonelevel": "BL",
        "tapered": "BLT",
        "tissue": "TL",
        "drive": "DRIVE",
        "helix": "HELIX",
        "grand": "GRAND",
        "morse": "MORSE",
        "screw": "SCREW",
        "vent": "VENT"
    }
    
    # Padrão para extrair diâmetros
    diametro_pattern = re.compile(r'(\d+[.,]\d+)(?:mm|MM)')
    
    processed_images = []
    counter = 1
    
    print(f"Processando imagens de {source_dir}")
    
    for filename in os.listdir(source_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            source_path = os.path.join(source_dir, filename)
            
            # Analisar nome do arquivo e metadados
            fabricante = "UNKNOWN"
            modelo = "UNKNOWN" 
            diametro = "4.0mm"  # Padrão comum
            
            # Extrair fabricante baseado no nome do arquivo
            filename_lower = filename.lower()
            
            if "nobel" in filename_lower:
                fabricante = "NOBEL"
                if "replace" in filename_lower:
                    modelo = "REPLACE"
                elif "active" in filename_lower:
                    modelo = "ACTIVE"
                elif "conical" in filename_lower or "cc" in filename_lower:
                    modelo = "CC"
                    
            elif "straumann" in filename_lower:
                fabricante = "STRAUMANN"
                if "bone" in filename_lower and "level" in filename_lower:
                    if "tapered" in filename_lower or "blt" in filename_lower:
                        modelo = "BLT"
                    else:
                        modelo = "BL"
                elif "tissue" in filename_lower:
                    modelo = "TL"
                elif "blx" in filename_lower:
                    modelo = "BLX"
                    
            elif "neodent" in filename_lower:
                fabricante = "NEODENT"
                if "drive" in filename_lower:
                    modelo = "DRIVE"
                elif "helix" in filename_lower:
                    modelo = "HELIX"
                elif "grand" in filename_lower and "morse" in filename_lower:
                    modelo = "GRAND_MORSE"
                    
            elif "zimmer" in filename_lower or "zimvie" in filename_lower:
                fabricante = "ZIMMER"
                if "tapered" in filename_lower and "screw" in filename_lower:
                    modelo = "TSV"
                elif "screw" in filename_lower and "vent" in filename_lower:
                    modelo = "SCREW_VENT"
            
            # Extrair diâmetro se possível
            diametro_match = diametro_pattern.search(filename_lower)
            if diametro_match:
                diametro = diametro_match.group(1).replace(',', '.') + "mm"
            else:
                # Diâmetros comuns baseados no fabricante/modelo
                if fabricante == "STRAUMANN" and "2.9" in filename_lower:
                    diametro = "2.9mm"
                elif fabricante == "STRAUMANN" and "3.3" in filename_lower:
                    diametro = "3.3mm"
                elif fabricante == "STRAUMANN" and "4.1" in filename_lower:
                    diametro = "4.1mm"
                elif fabricante == "STRAUMANN" and "4.8" in filename_lower:
                    diametro = "4.8mm"
                elif fabricante == "NOBEL" and "3.5" in filename_lower:
                    diametro = "3.5mm"
                elif fabricante == "NOBEL" and "4.3" in filename_lower:
                    diametro = "4.3mm"
                elif fabricante == "ZIMMER" and "4.7" in filename_lower:
                    diametro = "4.7mm"
            
            # Criar nome padronizado
            new_name = f"{fabricante}_{modelo}_{diametro}_{counter:02d}.jpg"
            target_path = os.path.join(target_dir, new_name)
            
            try:
                # Converter e redimensionar imagem
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
                    "fabricante": fabricante,
                    "modelo": modelo,
                    "diametro": diametro,
                    "path": target_path
                })
                
                print(f"Processado: {filename} -> {new_name}")
                counter += 1
                
            except Exception as e:
                print(f"Erro processando {filename}: {str(e)}")
    
    # Salvar metadados
    metadata_file = "/home/ubuntu/processed_images_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(processed_images, f, indent=2)
    
    print(f"\nProcessamento concluído!")
    print(f"Total de imagens processadas: {len(processed_images)}")
    print(f"Metadados salvos em: {metadata_file}")
    
    return processed_images

if __name__ == "__main__":
    processed = analyze_and_rename_images()
    print(f"\nResumo por fabricante:")
    
    fabricantes_count = {}
    for img in processed:
        fab = img['fabricante']
        fabricantes_count[fab] = fabricantes_count.get(fab, 0) + 1
    
    for fab, count in fabricantes_count.items():
        print(f"- {fab}: {count} imagens")

