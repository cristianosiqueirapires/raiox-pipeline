#!/usr/bin/env python3
"""
Script para upload das imagens processadas para DigitalOcean Spaces
"""

import boto3
import os
import json
from dotenv import load_dotenv

def upload_to_digitalocean_spaces():
    """
    Faz upload das imagens processadas para DigitalOcean Spaces
    """
    
    # Configurações do DigitalOcean Spaces
    DO_SPACES_KEY = "DO00CVCTFVXPANB4DD9M"
    DO_SPACES_SECRET = "+nWSRpFnQ+MncvZKDdw/herwYQRo0YEvVHujg1YMmaA"
    DO_SPACES_BUCKET = "raiox-images"
    DO_SPACES_REGION = "nyc3"
    DO_SPACES_ENDPOINT = f"https://{DO_SPACES_REGION}.digitaloceanspaces.com"
    
    # Configurar cliente S3 para DigitalOcean Spaces
    s3_client = boto3.client(
        's3',
        endpoint_url=DO_SPACES_ENDPOINT,
        aws_access_key_id=DO_SPACES_KEY,
        aws_secret_access_key=DO_SPACES_SECRET,
        region_name=DO_SPACES_REGION
    )
    
    # Diretórios
    images_dir = "/home/ubuntu/implant_images"
    metadata_file = "/home/ubuntu/processed_images_metadata.json"
    
    # Carregar metadados
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    uploaded_images = []
    
    print(f"Iniciando upload de {len(metadata)} imagens para DigitalOcean Spaces...")
    
    for i, img_data in enumerate(metadata):
        filename = img_data['new_filename']
        local_path = img_data['path']
        
        # Definir caminho no Spaces (pasta referencia/)
        spaces_key = f"referencia/{filename}"
        
        try:
            # Upload do arquivo
            s3_client.upload_file(
                local_path,
                DO_SPACES_BUCKET,
                spaces_key,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            # Gerar URL pública
            public_url = f"{DO_SPACES_ENDPOINT}/{DO_SPACES_BUCKET}/{spaces_key}"
            
            # Adicionar URL aos metadados
            img_data['spaces_url'] = public_url
            img_data['spaces_key'] = spaces_key
            
            uploaded_images.append(img_data)
            
            print(f"{i+1:2d}/60 - {filename} -> {public_url}")
            
        except Exception as e:
            print(f"Erro no upload de {filename}: {str(e)}")
    
    # Salvar metadados atualizados com URLs
    updated_metadata_file = "/home/ubuntu/uploaded_images_metadata.json"
    with open(updated_metadata_file, 'w') as f:
        json.dump(uploaded_images, f, indent=2)
    
    print(f"\nUpload concluído!")
    print(f"Total de imagens enviadas: {len(uploaded_images)}")
    print(f"Metadados com URLs salvos em: {updated_metadata_file}")
    
    # Resumo por fabricante
    fabricantes_count = {}
    for img in uploaded_images:
        fab = img['fabricante']
        fabricantes_count[fab] = fabricantes_count.get(fab, 0) + 1
    
    print(f"\nResumo do upload por fabricante:")
    for fab, count in fabricantes_count.items():
        print(f"- {fab}: {count} imagens")
    
    return uploaded_images

if __name__ == "__main__":
    uploaded = upload_to_digitalocean_spaces()

