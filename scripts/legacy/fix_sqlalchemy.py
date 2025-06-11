#!/usr/bin/env python3

# Script para corrigir usando SQLAlchemy ORM

import re

# Ler o arquivo
with open('/opt/raiox-app/app/main.py', 'r') as f:
    content = f.read()

# Adicionar imports necessários no topo do arquivo
if 'from sqlalchemy.orm import sessionmaker' not in content:
    # Encontrar a linha dos imports
    import_section = content.find('from sqlalchemy import')
    if import_section != -1:
        # Adicionar imports necessários
        new_imports = '''from sqlalchemy import create_engine, text, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
'''
        content = content.replace('from sqlalchemy import', new_imports + '\nfrom sqlalchemy import')

# Adicionar modelo SQLAlchemy
model_code = '''
# Modelo SQLAlchemy para implants
Base = declarative_base()

class Implant(Base):
    __tablename__ = 'implants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    manufacturer = Column(String(255))
    image_url = Column(Text)
    embedding = Column(Vector(512))
'''

# Inserir modelo após os imports
if 'class Implant(Base):' not in content:
    # Encontrar onde inserir o modelo
    app_creation = content.find('app = FastAPI(')
    if app_creation != -1:
        content = content[:app_creation] + model_code + '\n\n' + content[app_creation:]

# Nova função usando SQLAlchemy ORM
new_function = '''def find_similar_implants(query_vector, db, limit=3):
    """
    Encontra implantes similares com base em um vetor de consulta usando SQLAlchemy ORM.
    """
    try:
        from sqlalchemy.orm import sessionmaker
        
        # Criar sessão SQLAlchemy
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Usar SQLAlchemy ORM com pgvector
        similar_implants = session.query(Implant).order_by(
            Implant.embedding.l2_distance(query_vector.tolist())
        ).limit(limit).all()
        
        # Converter para lista de dicionários
        result = []
        for implant in similar_implants:
            result.append({
                "id": implant.id,
                "name": implant.name,
                "manufacturer": implant.manufacturer,
                "image_url": implant.image_url
            })
        
        session.close()
        return result
        
    except Exception as e:
        logger.error(f"Erro na busca de implantes similares: {str(e)}")
        return []'''

# Substituir a função problemática
pattern = r'def find_similar_implants\(query_vector, db, limit=3\):.*?return \[\]'
content = re.sub(pattern, new_function, content, flags=re.DOTALL)

# Salvar o arquivo
with open('/opt/raiox-app/app/main.py', 'w') as f:
    f.write(content)

print("Função corrigida usando SQLAlchemy ORM!")

