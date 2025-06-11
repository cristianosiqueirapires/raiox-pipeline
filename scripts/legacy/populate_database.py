#!/usr/bin/env python3
"""
RAIOX AI - POPULAÇÃO DA TABELA IMPLANTS
Script escalável para inserir embeddings no PostgreSQL com pgvector
"""

import json
import psycopg2
from psycopg2.extras import execute_values
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RaioxDatabasePopulator:
    """Populador escalável da tabela implants"""
    
    def __init__(self):
        # Credenciais do PostgreSQL
        self.db_config = {
            "host": "159.65.183.73",
            "database": "raiox",
            "user": "raiox_user", 
            "password": "Xc7!rA2v9Z@1pQ3y",
            "port": 5432
        }
    
    def connect_database(self):
        """Conecta ao banco PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            logger.info("✅ Conectado ao PostgreSQL com sucesso!")
            return conn
        except Exception as e:
            logger.error(f"❌ Erro conectando ao PostgreSQL: {str(e)}")
            return None
    
    def prepare_database(self, conn):
        """Prepara banco de dados e tabela"""
        try:
            cur = conn.cursor()
            
            # Verificar se pgvector está instalado
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("✅ Extensão pgvector verificada")
            
            # Limpar tabela existente
            cur.execute("DELETE FROM implants;")
            logger.info("🧹 Tabela implants limpa")
            
            # Verificar estrutura da tabela
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'implants'
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            logger.info("📋 Estrutura da tabela implants:")
            for col_name, col_type in columns:
                logger.info(f"   - {col_name}: {col_type}")
            
            conn.commit()
            cur.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro preparando banco: {str(e)}")
            return False
    
    def insert_embeddings(self, conn, embeddings_data):
        """Insere embeddings na tabela implants"""
        try:
            cur = conn.cursor()
            
            # Preparar dados para inserção
            insert_data = []
            
            for img_data in embeddings_data:
                # Extrair informações
                name = f"{img_data['modelo']} {img_data['diametro']}"
                manufacturer = img_data['fabricante']
                image_url = img_data['spaces_url']
                embedding = img_data['embedding']
                
                insert_data.append((name, manufacturer, image_url, embedding))
            
            # Inserção em lote usando execute_values (mais eficiente)
            insert_query = """
                INSERT INTO implants (name, manufacturer, image_url, embedding)
                VALUES %s
            """
            
            execute_values(
                cur,
                insert_query,
                insert_data,
                template="(%s, %s, %s, %s::vector)",
                page_size=100  # Processar em lotes de 100
            )
            
            conn.commit()
            
            # Verificar inserção
            cur.execute("SELECT COUNT(*) FROM implants;")
            count = cur.fetchone()[0]
            
            logger.info(f"✅ {count} implantes inseridos com sucesso!")
            
            cur.close()
            return count
            
        except Exception as e:
            logger.error(f"❌ Erro inserindo dados: {str(e)}")
            conn.rollback()
            return 0
    
    def create_indexes(self, conn):
        """Cria índices para otimizar buscas"""
        try:
            cur = conn.cursor()
            
            # Índice para busca vetorial (HNSW é mais eficiente para grandes volumes)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS implants_embedding_hnsw_idx
                ON implants
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            # Índices para buscas por fabricante
            cur.execute("""
                CREATE INDEX IF NOT EXISTS implants_manufacturer_idx
                ON implants (manufacturer);
            """)
            
            # Índice para buscas por nome
            cur.execute("""
                CREATE INDEX IF NOT EXISTS implants_name_idx
                ON implants (name);
            """)
            
            conn.commit()
            logger.info("✅ Índices criados para otimização de buscas")
            
            cur.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro criando índices: {str(e)}")
            return False
    
    def test_similarity_search(self, conn):
        """Testa busca de similaridade"""
        try:
            cur = conn.cursor()
            
            # Pegar um embedding de exemplo
            cur.execute("SELECT embedding FROM implants LIMIT 1;")
            sample_embedding = cur.fetchone()[0]
            
            # Testar busca de similaridade
            cur.execute("""
                SELECT name, manufacturer, embedding <-> %s::vector as distance
                FROM implants
                ORDER BY embedding <-> %s::vector
                LIMIT 3;
            """, (sample_embedding, sample_embedding))
            
            results = cur.fetchall()
            
            logger.info("🔍 Teste de busca de similaridade:")
            for name, manufacturer, distance in results:
                logger.info(f"   - {manufacturer} {name} (distância: {distance:.4f})")
            
            cur.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro testando busca: {str(e)}")
            return False
    
    def generate_database_report(self, conn):
        """Gera relatório do banco de dados"""
        try:
            cur = conn.cursor()
            
            # Estatísticas gerais
            cur.execute("SELECT COUNT(*) FROM implants;")
            total_implants = cur.fetchone()[0]
            
            # Contagem por fabricante
            cur.execute("""
                SELECT manufacturer, COUNT(*) 
                FROM implants 
                GROUP BY manufacturer 
                ORDER BY COUNT(*) DESC;
            """)
            fabricantes_stats = cur.fetchall()
            
            # Verificar índices
            cur.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename = 'implants';
            """)
            indexes = cur.fetchall()
            
            logger.info("📊 RELATÓRIO DO BANCO DE DADOS:")
            logger.info(f"   Total de implantes: {total_implants}")
            logger.info("   Por fabricante:")
            for manufacturer, count in fabricantes_stats:
                logger.info(f"     - {manufacturer}: {count}")
            
            logger.info("   Índices criados:")
            for index_name, table_name in indexes:
                logger.info(f"     - {index_name}")
            
            # Salvar relatório
            report = {
                "total_implants": total_implants,
                "fabricantes_stats": dict(fabricantes_stats),
                "indexes": [idx[0] for idx in indexes],
                "status": "DATABASE_READY",
                "scalability": "Preparado para 10K+ implantes"
            }
            
            with open("/home/ubuntu/database_report.json", 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("📋 Relatório salvo: /home/ubuntu/database_report.json")
            
            cur.close()
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro gerando relatório: {str(e)}")
            return None
    
    def run_population_pipeline(self):
        """Executa pipeline completo de população"""
        
        logger.info("🚀 INICIANDO POPULAÇÃO DA TABELA IMPLANTS")
        
        # Carregar dados de embeddings
        try:
            with open("/home/ubuntu/embeddings_production_ready.json", 'r') as f:
                embeddings_data = json.load(f)
            logger.info(f"📊 Carregados {len(embeddings_data)} embeddings")
        except Exception as e:
            logger.error(f"❌ Erro carregando embeddings: {str(e)}")
            return False
        
        # Conectar ao banco
        conn = self.connect_database()
        if not conn:
            return False
        
        try:
            # Preparar banco
            if not self.prepare_database(conn):
                return False
            
            # Inserir dados
            inserted_count = self.insert_embeddings(conn, embeddings_data)
            if inserted_count == 0:
                return False
            
            # Criar índices
            if not self.create_indexes(conn):
                return False
            
            # Testar busca
            if not self.test_similarity_search(conn):
                return False
            
            # Gerar relatório
            report = self.generate_database_report(conn)
            
            logger.info("🎉 POPULAÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info("🎯 Sistema pronto para receber uploads via webhook!")
            
            return True
            
        finally:
            conn.close()
            logger.info("🔌 Conexão com banco fechada")

def main():
    """Função principal"""
    populator = RaioxDatabasePopulator()
    success = populator.run_population_pipeline()
    
    if success:
        logger.info("✅ Pipeline de população executado com sucesso!")
    else:
        logger.error("❌ Pipeline de população falhou!")
    
    return success

if __name__ == "__main__":
    main()

