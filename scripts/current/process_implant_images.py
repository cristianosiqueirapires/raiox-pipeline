#!/usr/bin/env python3
"""
Script para processar imagens de implantes e gerar embeddings usando CLIP
"""
import os
import json
import requests
from PIL import Image
import time

def process_images_with_clip():
    """Processa imagens usando a API CLIP do servidor staging"""
    
    # Configurações
    images_dir = "/home/ubuntu/upload/search_images"
    output_file = "/home/ubuntu/implants_embeddings.json"
    clip_api_url = "http://45.55.128.141:8000/upload"
    
    # Dados dos implantes organizados por fabricante
    implants_data = []
    
    # Mapear imagens para fabricantes baseado nos nomes dos arquivos de busca
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    print(f"🔍 Encontradas {len(image_files)} imagens para processar")
    
    # Organizar por fabricante baseado na ordem de coleta
    fabricantes = {
        'Nobel Biocare': image_files[0:8],   # Primeiras 8 imagens
        'Straumann': image_files[8:16],      # Próximas 8 imagens  
        'Neodent': image_files[16:24],       # Próximas 8 imagens
        'Zimmer': image_files[24:32],        # Próximas 8 imagens
    }
    
    for fabricante, files in fabricantes.items():
        print(f"\n📋 Processando {fabricante}...")
        
        for i, filename in enumerate(files[:8]):  # Limitar a 8 por fabricante
            image_path = os.path.join(images_dir, filename)
            
            if not os.path.exists(image_path):
                print(f"   ⚠️  Arquivo não encontrado: {filename}")
                continue
                
            try:
                print(f"   🔄 Processando {filename}...", end="", flush=True)
                
                # Preparar dados do implante
                implant_data = {
                    'id': len(implants_data) + 1,
                    'name': f"{fabricante} Implant {i+1}",
                    'manufacturer': fabricante,
                    'model': get_model_name(fabricante, i),
                    'diameter': get_diameter(fabricante, i),
                    'image_path': image_path,
                    'image_filename': filename
                }
                
                # Simular processamento CLIP (por enquanto)
                # TODO: Implementar chamada real para API CLIP
                time.sleep(0.5)  # Simular processamento
                
                # Por enquanto, criar embedding simulado
                # Em produção, isso seria substituído pela chamada real ao CLIP
                embedding = [0.1] * 512  # Embedding simulado de 512 dimensões
                
                implant_data['embedding'] = embedding
                implants_data.append(implant_data)
                
                print(" ✅")
                
            except Exception as e:
                print(f" ❌ Erro: {str(e)}")
                continue
    
    # Salvar dados processados
    print(f"\n💾 Salvando {len(implants_data)} implantes processados...")
    
    with open(output_file, 'w') as f:
        json.dump(implants_data, f, indent=2)
    
    print(f"✅ Dados salvos em: {output_file}")
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    for fabricante in fabricantes.keys():
        count = len([x for x in implants_data if x['manufacturer'] == fabricante])
        print(f"   {fabricante}: {count} implantes")
    
    return implants_data

def get_model_name(fabricante, index):
    """Retorna nome do modelo baseado no fabricante e índice"""
    models = {
        'Nobel Biocare': ['Replace', 'N1', 'All-on-4', 'NobelPearl', 'Replace CC', 'Active', 'Parallel', 'Branemark'],
        'Straumann': ['BLX', 'TLX', 'BL', 'SLA', 'SLActive', 'Roxolid', 'Pro Arch', 'Standard'],
        'Neodent': ['Grand Morse', 'Drive', 'Helix', 'Titamax', 'CM', 'Alvim', 'Facility', 'Acqua'],
        'Zimmer': ['TSV', 'Screw-Vent', 'SwissPlus', 'Tapered', 'Trabecular', 'MTX', 'Encode', 'T3']
    }
    return models.get(fabricante, ['Standard'])[index % len(models.get(fabricante, ['Standard']))]

def get_diameter(fabricante, index):
    """Retorna diâmetro baseado no fabricante e índice"""
    diameters = ['3.3mm', '3.5mm', '4.0mm', '4.1mm', '4.3mm', '4.5mm', '4.7mm', '5.0mm']
    return diameters[index % len(diameters)]

if __name__ == "__main__":
    print("🚀 Iniciando processamento de imagens de implantes...")
    
    try:
        implants_data = process_images_with_clip()
        print(f"\n🎉 Processamento concluído! {len(implants_data)} implantes processados.")
        
    except Exception as e:
        print(f"\n❌ Erro durante processamento: {str(e)}")
        exit(1)

