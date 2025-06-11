#!/usr/bin/env python3
"""
Script para popular a tabela implants no PostgreSQL com dados reais
"""
import json
import psycopg2
from psycopg2.extras import execute_values
import sys

def populate_implants_table():
    """Popula a tabela implants com dados dos embeddings gerados"""
    
    # Carregar dados dos embeddings
    embeddings_file = "/home/ubuntu/implants_embeddings.json"
    
    try:
        with open(embeddings_file, 'r') as f:
            implants_data = json.load(f)
        print(f"✅ Carregados {len(implants_data)} implantes do arquivo")
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo de embeddings: {e}")
        return False
    
    # Conectar ao PostgreSQL via SSH (conexão local no servidor)
    print("🔗 Conectando ao PostgreSQL...")
    
    try:
        # Usar conexão local no servidor PostgreSQL
        conn = psycopg2.connect(
            host='localhost',
            database='raiox',
            user='postgres',
            password='',  # Conexão local sem senha
            port=5432
        )
        cur = conn.cursor()
        print("✅ Conexão PostgreSQL estabelecida")
        
    except Exception as e:
        print(f"❌ Erro de conexão PostgreSQL: {e}")
        return False
    
    try:
        # Verificar se tabela existe e está vazia
        cur.execute("SELECT COUNT(*) FROM implants;")
        current_count = cur.fetchone()[0]
        print(f"📊 Registros atuais na tabela: {current_count}")
        
        if current_count > 0:
            print("⚠️  Tabela não está vazia. Limpando dados existentes...")
            cur.execute("DELETE FROM implants;")
            conn.commit()
            print("✅ Tabela limpa")
        
        # Preparar dados para inserção
        insert_data = []
        for implant in implants_data:
            insert_data.append((
                implant['name'],
                implant['manufacturer'],
                f"https://raiox-images.nyc3.digitaloceanspaces.com/referencia/{implant['image_filename']}",
                implant['embedding']
            ))
        
        # Inserir dados em lote
        print(f"💾 Inserindo {len(insert_data)} implantes...")
        
        insert_query = """
            INSERT INTO implants (name, manufacturer, image_url, embedding)
            VALUES %s
        """
        
        execute_values(
            cur,
            insert_query,
            insert_data,
            template=None,
            page_size=100
        )
        
        conn.commit()
        print("✅ Dados inseridos com sucesso!")
        
        # Verificar inserção
        cur.execute("SELECT COUNT(*) FROM implants;")
        final_count = cur.fetchone()[0]
        print(f"📊 Total de registros após inserção: {final_count}")
        
        # Mostrar alguns exemplos
        cur.execute("""
            SELECT id, name, manufacturer, 
                   CASE WHEN image_url IS NOT NULL THEN 'URL definida' ELSE 'URL nula' END as url_status,
                   array_length(embedding, 1) as embedding_dim
            FROM implants 
            LIMIT 5;
        """)
        
        examples = cur.fetchall()
        print("\n📋 Exemplos inseridos:")
        for row in examples:
            print(f"   ID: {row[0]}, Nome: {row[1]}, Fabricante: {row[2]}, URL: {row[3]}, Embedding: {row[4]}D")
        
        # Testar busca de similaridade
        print("\n🔍 Testando busca de similaridade...")
        test_embedding = implants_data[0]['embedding']  # Usar primeiro embedding como teste
        
        cur.execute("""
            SELECT id, name, manufacturer, embedding <-> %s::vector as distance
            FROM implants
            ORDER BY embedding <-> %s::vector
            LIMIT 3;
        """, (test_embedding, test_embedding))
        
        similar = cur.fetchall()
        print("📊 Resultados de busca de similaridade:")
        for row in similar:
            print(f"   ID: {row[0]}, Nome: {row[1]}, Fabricante: {row[2]}, Distância: {row[3]:.4f}")
        
        cur.close()
        conn.close()
        
        print("\n🎉 População da tabela implants concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante inserção: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando população da tabela implants...")
    
    success = populate_implants_table()
    
    if success:
        print("\n✅ MISSÃO CUMPRIDA! Tabela implants populada com dados reais!")
        sys.exit(0)
    else:
        print("\n❌ Falha na população da tabela!")
        sys.exit(1)

