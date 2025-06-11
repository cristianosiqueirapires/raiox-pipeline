#!/usr/bin/env python3

# Script para corrigir o problema dos %% duplicados no main.py

import re

# Ler o arquivo
with open('/opt/raiox-app/app/main.py', 'r') as f:
    content = f.read()

# Função corrigida que evita o problema dos %% duplicados
new_function = '''def find_similar_implants(query_vector, db, limit=3):
    """
    Encontra implantes similares com base em um vetor de consulta.
    
    Args:
        query_vector: Vetor de embedding da imagem de consulta
        db: Sessão do banco de dados
        limit: Número máximo de implantes a retornar
        
    Returns:
        Lista de implantes similares
    """
    try:
        # Converter array para formato PostgreSQL
        vector_str = str(query_vector.tolist()).replace('[', '{').replace(']', '}')
        
        # SQL direto sem parâmetros problemáticos
        sql = f"""
            SELECT id, name, manufacturer, image_url
            FROM implants
            ORDER BY embedding <-> '{vector_str}'::vector
            LIMIT {limit}
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            
            implants = []
            for row in result:
                implants.append({
                    "id": row[0],
                    "name": row[1],
                    "manufacturer": row[2],
                    "image_url": row[3]
                })
            
            return implants
    except Exception as e:
        logger.error(f"Erro na busca de implantes similares: {str(e)}")
        return []'''

# Encontrar e substituir a função
pattern = r'def find_similar_implants\(query_vector, db, limit=3\):.*?return \[\]'
content = re.sub(pattern, new_function, content, flags=re.DOTALL)

# Salvar o arquivo
with open('/opt/raiox-app/app/main.py', 'w') as f:
    f.write(content)

print("Função find_similar_implants corrigida com sucesso!")

