#!/usr/bin/env python3
"""
RAIOX AI - PIPELINE ESCALÁVEL DE EMBEDDINGS
Usa a API CLIP existente no staging para máxima robustez e escalabilidade
"""

import json
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RaioxEmbeddingPipeline:
    """Pipeline escalável para extração de embeddings usando API CLIP existente"""
    
    def __init__(self):
        self.staging_api_url = "http://45.55.128.141:8000"
        self.max_workers = 5  # Controle de concorrência
        self.retry_attempts = 3
        self.retry_delay = 2
        
    def extract_embedding_from_url(self, image_url, metadata):
        """Extrai embedding de uma imagem usando a API CLIP staging"""
        
        for attempt in range(self.retry_attempts):
            try:
                # Usar endpoint /upload da API existente
                files = {'file': ('temp.jpg', requests.get(image_url).content, 'image/jpeg')}
                headers = {'X-Client-ID': 'pipeline_embeddings'}
                
                response = requests.post(
                    f"{self.staging_api_url}/upload",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    # API retorna similar_implants, mas queremos o embedding
                    # Vamos usar uma abordagem diferente - endpoint direto
                    return self.extract_via_direct_processing(image_url, metadata)
                else:
                    logger.warning(f"Tentativa {attempt+1} falhou para {metadata['new_filename']}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"Tentativa {attempt+1} erro para {metadata['new_filename']}: {str(e)}")
                
            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay)
        
        return None
    
    def extract_via_direct_processing(self, image_url, metadata):
        """Processa imagem diretamente no staging via SSH otimizado"""
        
        try:
            # Script otimizado para execução única
            script = f'''
import torch
import clip
from PIL import Image
import requests
import io
import json

# Carregar modelo uma vez
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Processar imagem
response = requests.get("{image_url}", timeout=30)
image = Image.open(io.BytesIO(response.content))
if image.mode != 'RGB':
    image = image.convert('RGB')

image_input = preprocess(image).unsqueeze(0).to(device)

with torch.no_grad():
    image_features = model.encode_image(image_input)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    embedding = image_features.cpu().numpy()[0].tolist()

print(json.dumps({{"embedding": embedding, "size": len(embedding)}}))
'''
            
            # Executar no staging
            import subprocess
            result = subprocess.run([
                "ssh", "-i", "/home/ubuntu/.ssh/raiox_key",
                "root@45.55.128.141",
                f"cd /opt/raiox-app && python3 -c '{script}'"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                output = result.stdout.strip().split('\n')[-1]  # Última linha
                data = json.loads(output)
                
                # Adicionar embedding aos metadados
                metadata['embedding'] = data['embedding']
                metadata['embedding_size'] = data['size']
                
                return metadata
            else:
                logger.error(f"Erro SSH para {metadata['new_filename']}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Erro processamento direto {metadata['new_filename']}: {str(e)}")
            return None
    
    def process_batch(self, images_batch):
        """Processa lote de imagens com controle de erro"""
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter tarefas
            future_to_metadata = {
                executor.submit(self.extract_via_direct_processing, img['spaces_url'], img): img
                for img in images_batch
            }
            
            # Coletar resultados
            for future in as_completed(future_to_metadata):
                metadata = future_to_metadata[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.info(f"✓ {result['new_filename']} - {result['embedding_size']}D")
                    else:
                        logger.error(f"✗ {metadata['new_filename']} - Falhou")
                except Exception as e:
                    logger.error(f"✗ {metadata['new_filename']} - Exceção: {str(e)}")
        
        return results
    
    def run_pipeline(self):
        """Executa pipeline completo com estratégia escalável"""
        
        logger.info("🚀 INICIANDO PIPELINE ESCALÁVEL DE EMBEDDINGS")
        
        # Carregar metadados
        with open("/home/ubuntu/uploaded_images_metadata.json", 'r') as f:
            images_metadata = json.load(f)
        
        logger.info(f"📊 Total de imagens: {len(images_metadata)}")
        
        # Processar em lotes para escalabilidade
        batch_size = 10
        all_embeddings = []
        
        for i in range(0, len(images_metadata), batch_size):
            batch = images_metadata[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(images_metadata) + batch_size - 1) // batch_size
            
            logger.info(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} imagens)")
            
            batch_results = self.process_batch(batch)
            all_embeddings.extend(batch_results)
            
            # Salvar progresso incremental
            self.save_progress(all_embeddings, f"embeddings_progress_batch_{batch_num}.json")
            
            logger.info(f"✅ Lote {batch_num} concluído: {len(batch_results)}/{len(batch)} sucessos")
            
            # Pausa entre lotes para não sobrecarregar
            if i + batch_size < len(images_metadata):
                time.sleep(1)
        
        # Salvar resultado final
        final_file = "/home/ubuntu/embeddings_data_final.json"
        with open(final_file, 'w') as f:
            json.dump(all_embeddings, f, indent=2)
        
        # Relatório final
        self.generate_final_report(all_embeddings)
        
        return all_embeddings
    
    def save_progress(self, data, filename):
        """Salva progresso incremental"""
        filepath = f"/home/ubuntu/{filename}"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"💾 Progresso salvo: {filepath}")
    
    def generate_final_report(self, embeddings_data):
        """Gera relatório final detalhado"""
        
        total_processed = len(embeddings_data)
        
        # Resumo por fabricante
        fabricantes_count = {}
        for img in embeddings_data:
            fab = img['fabricante']
            fabricantes_count[fab] = fabricantes_count.get(fab, 0) + 1
        
        logger.info("🎯 PIPELINE CONCLUÍDO COM SUCESSO!")
        logger.info(f"📈 Total de embeddings extraídos: {total_processed}")
        logger.info("📊 Resumo por fabricante:")
        
        for fab, count in fabricantes_count.items():
            logger.info(f"   - {fab}: {count} embeddings")
        
        # Salvar relatório
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_processed": total_processed,
            "fabricantes_summary": fabricantes_count,
            "embedding_dimension": embeddings_data[0]['embedding_size'] if embeddings_data else 0,
            "status": "SUCCESS"
        }
        
        with open("/home/ubuntu/pipeline_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📋 Relatório salvo: /home/ubuntu/pipeline_report.json")

def main():
    """Função principal do pipeline"""
    pipeline = RaioxEmbeddingPipeline()
    embeddings = pipeline.run_pipeline()
    return embeddings

if __name__ == "__main__":
    embeddings = main()

