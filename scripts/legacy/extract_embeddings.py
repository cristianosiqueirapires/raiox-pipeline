#!/usr/bin/env python3
"""
Script para extrair embeddings CLIP das imagens no servidor staging
"""

import json
import requests
import torch
import clip
from PIL import Image
import io
import numpy as np

def extract_embeddings_on_staging():
    """
    Extrai embeddings CLIP das imagens usando o servidor staging
    """
    
    # Carregar metadados das imagens
    metadata_file = "/home/ubuntu/uploaded_images_metadata.json"
    with open(metadata_file, 'r') as f:
        images_metadata = json.load(f)
    
    print(f"Extraindo embeddings de {len(images_metadata)} imagens...")
    
    # Carregar modelo CLIP localmente para teste
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Usando dispositivo: {device}")
    
    try:
        model, preprocess = clip.load("ViT-B/32", device=device)
        print("Modelo CLIP carregado com sucesso!")
    except Exception as e:
        print(f"Erro carregando CLIP: {e}")
        return None
    
    embeddings_data = []
    
    for i, img_data in enumerate(images_metadata):
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
            
            print(f"{i+1:2d}/60 - {filename} - Embedding extraído ({len(embedding)} dimensões)")
            
        except Exception as e:
            print(f"Erro processando {filename}: {str(e)}")
    
    # Salvar embeddings
    embeddings_file = "/home/ubuntu/embeddings_data.json"
    with open(embeddings_file, 'w') as f:
        json.dump(embeddings_data, f, indent=2)
    
    print(f"\nExtração concluída!")
    print(f"Total de embeddings extraídos: {len(embeddings_data)}")
    print(f"Dados salvos em: {embeddings_file}")
    
    # Resumo por fabricante
    fabricantes_count = {}
    for img in embeddings_data:
        fab = img['fabricante']
        fabricantes_count[fab] = fabricantes_count.get(fab, 0) + 1
    
    print(f"\nResumo de embeddings por fabricante:")
    for fab, count in fabricantes_count.items():
        print(f"- {fab}: {count} embeddings")
    
    return embeddings_data

if __name__ == "__main__":
    # Instalar dependências se necessário
    try:
        import clip
    except ImportError:
        print("Instalando dependências...")
        import subprocess
        subprocess.run(["pip3", "install", "git+https://github.com/openai/CLIP.git"], check=True)
        import clip
    
    embeddings = extract_embeddings_on_staging()

