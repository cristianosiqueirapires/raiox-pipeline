#!/usr/bin/env python3
"""
Script para extrair embeddings usando o servidor CLIP staging via SSH
"""

import json
import subprocess
import os

def extract_embeddings_via_staging():
    """
    Usa o servidor staging para extrair embeddings das imagens
    """
    
    # Carregar metadados das imagens
    metadata_file = "/home/ubuntu/uploaded_images_metadata.json"
    with open(metadata_file, 'r') as f:
        images_metadata = json.load(f)
    
    print(f"Extraindo embeddings de {len(images_metadata)} imagens via servidor staging...")
    
    # Criar script Python para executar no staging
    staging_script = """
import torch
import clip
from PIL import Image
import requests
import json
import io
import sys

def extract_embeddings(urls_data):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Carregando CLIP no dispositivo: {device}")
    
    model, preprocess = clip.load("ViT-B/32", device=device)
    print("Modelo CLIP carregado!")
    
    embeddings_data = []
    
    for i, img_data in enumerate(urls_data):
        url = img_data['spaces_url']
        filename = img_data['new_filename']
        
        try:
            # Baixar imagem
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"Erro baixando {filename}: HTTP {response.status_code}")
                continue
            
            # Processar imagem
            image = Image.open(io.BytesIO(response.content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Pré-processar para CLIP
            image_input = preprocess(image).unsqueeze(0).to(device)
            
            # Extrair embedding
            with torch.no_grad():
                image_features = model.encode_image(image_input)
                # Normalizar o vetor
                image_features /= image_features.norm(dim=-1, keepdim=True)
                # Converter para lista Python
                embedding = image_features.cpu().numpy()[0].tolist()
            
            # Adicionar embedding aos metadados
            img_data['embedding'] = embedding
            img_data['embedding_size'] = len(embedding)
            
            embeddings_data.append(img_data)
            
            print(f"{i+1:2d}/{len(urls_data)} - {filename} - OK ({len(embedding)}D)")
            
        except Exception as e:
            print(f"Erro processando {filename}: {str(e)}")
    
    return embeddings_data

if __name__ == "__main__":
    # Ler dados do stdin
    urls_data = json.loads(sys.stdin.read())
    embeddings = extract_embeddings(urls_data)
    
    # Salvar resultado
    with open('/tmp/embeddings_result.json', 'w') as f:
        json.dump(embeddings, f, indent=2)
    
    print(f"Embeddings salvos em /tmp/embeddings_result.json")
    print(f"Total processado: {len(embeddings)}")
"""
    
    # Salvar script temporário
    staging_script_file = "/tmp/extract_embeddings_staging.py"
    with open(staging_script_file, 'w') as f:
        f.write(staging_script)
    
    # Enviar script para o staging
    print("Enviando script para servidor staging...")
    scp_cmd = [
        "scp", "-i", "/home/ubuntu/.ssh/raiox_key",
        staging_script_file,
        "root@45.55.128.141:/tmp/"
    ]
    
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro enviando script: {result.stderr}")
        return None
    
    # Executar extração no staging
    print("Executando extração de embeddings no staging...")
    
    # Preparar dados para enviar
    json_data = json.dumps(images_metadata)
    
    ssh_cmd = [
        "ssh", "-i", "/home/ubuntu/.ssh/raiox_key",
        "root@45.55.128.141",
        f"cd /opt/raiox-app && echo '{json_data}' | python3 /tmp/extract_embeddings_staging.py"
    ]
    
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro executando no staging: {result.stderr}")
        print(f"Stdout: {result.stdout}")
        return None
    
    print("Extração concluída! Baixando resultado...")
    
    # Baixar resultado
    scp_download_cmd = [
        "scp", "-i", "/home/ubuntu/.ssh/raiox_key",
        "root@45.55.128.141:/tmp/embeddings_result.json",
        "/home/ubuntu/embeddings_data.json"
    ]
    
    result = subprocess.run(scp_download_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro baixando resultado: {result.stderr}")
        return None
    
    # Carregar e verificar resultado
    with open("/home/ubuntu/embeddings_data.json", 'r') as f:
        embeddings_data = json.load(f)
    
    print(f"\\nExtração concluída com sucesso!")
    print(f"Total de embeddings extraídos: {len(embeddings_data)}")
    
    # Resumo por fabricante
    fabricantes_count = {}
    for img in embeddings_data:
        fab = img['fabricante']
        fabricantes_count[fab] = fabricantes_count.get(fab, 0) + 1
    
    print(f"\\nResumo de embeddings por fabricante:")
    for fab, count in fabricantes_count.items():
        print(f"- {fab}: {count} embeddings")
    
    return embeddings_data

if __name__ == "__main__":
    embeddings = extract_embeddings_via_staging()

