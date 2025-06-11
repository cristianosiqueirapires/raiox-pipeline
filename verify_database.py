#!/usr/bin/env python3
"""
RAIOX AI - VERIFICAÇÃO DO BANCO DE DADOS
Verifica se a população foi bem-sucedida
"""

import psycopg2
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_database():
    """Verifica estado atual do banco de dados"""
    
    # Credenciais do PostgreSQL
    db_config = {
        "host": "159.65.183.73",
        "database": "raiox",
        "user": "raiox_user", 
        "password": "Xc7!rA2v9Z@1pQ3y",
        "port": 5432
    }
    
    try:
        # Conectar
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        logger.info("✅ Conectado ao PostgreSQL")
        
        # Verificar tabela implants
        cur.execute("SELECT COUNT(*) FROM implants;")
        total_implants = cur.fetchone()[0]
        
        logger.info(f"📊 Total de implantes na tabela: {total_implants}")
        
        if total_implants > 0:
            # Verificar estrutura
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'implants'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            logger.info("📋 Estrutura da tabela:")
            for col_name, col_type in columns:
                logger.info(f"   - {col_name}: {col_type}")
            
            # Verificar alguns registros
            cur.execute("""
                SELECT id, name, manufacturer, 
                       CASE WHEN embedding IS NOT NULL THEN 'SIM' ELSE 'NÃO' END as tem_embedding
                FROM implants 
                LIMIT 5;
            """)
            samples = cur.fetchall()
            
            logger.info("🔍 Amostras de dados:")
            for id, name, manufacturer, tem_embedding in samples:
                logger.info(f"   - ID {id}: {manufacturer} {name} (Embedding: {tem_embedding})")
            
            # Contagem por fabricante
            cur.execute("""
                SELECT manufacturer, COUNT(*) 
                FROM implants 
                GROUP BY manufacturer 
                ORDER BY COUNT(*) DESC;
            """)
            fabricantes = cur.fetchall()
            
            logger.info("📈 Por fabricante:")
            for manufacturer, count in fabricantes:
                logger.info(f"   - {manufacturer}: {count}")
            
            # Testar busca de similaridade
            cur.execute("SELECT embedding FROM implants WHERE embedding IS NOT NULL LIMIT 1;")
            sample_embedding = cur.fetchone()
            
            if sample_embedding:
                embedding = sample_embedding[0]
                cur.execute("""
                    SELECT name, manufacturer, embedding <-> %s::vector as distance
                    FROM implants
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <-> %s::vector
                    LIMIT 3;
                """, (embedding, embedding))
                
                similar = cur.fetchall()
                
                logger.info("🎯 Teste de busca de similaridade:")
                for name, manufacturer, distance in similar:
                    logger.info(f"   - {manufacturer} {name} (distância: {distance:.4f})")
            
            # Verificar índices
            cur.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'implants';
            """)
            indexes = cur.fetchall()
            
            logger.info("🔧 Índices criados:")
            for idx in indexes:
                logger.info(f"   - {idx[0]}")
            
            # Salvar relatório de verificação
            report = {
                "status": "SUCCESS",
                "total_implants": total_implants,
                "fabricantes": dict(fabricantes),
                "columns": [{"name": col[0], "type": col[1]} for col in columns],
                "indexes": [idx[0] for idx in indexes],
                "similarity_test": "PASSED" if sample_embedding else "NO_EMBEDDINGS"
            }
            
            with open("/home/ubuntu/database_verification.json", 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("✅ BANCO DE DADOS POPULADO COM SUCESSO!")
            logger.info("📋 Relatório salvo: /home/ubuntu/database_verification.json")
            
        else:
            logger.warning("⚠️ Tabela implants está vazia!")
            report = {"status": "EMPTY", "total_implants": 0}
            
            with open("/home/ubuntu/database_verification.json", 'w') as f:
                json.dump(report, f, indent=2)
        
        cur.close()
        conn.close()
        
        return total_implants > 0
        
    except Exception as e:
        logger.error(f"❌ Erro verificando banco: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_database()
    if success:
        print("✅ VERIFICAÇÃO CONCLUÍDA - BANCO POPULADO!")
    else:
        print("❌ VERIFICAÇÃO FALHOU - BANCO VAZIO OU ERRO!")

