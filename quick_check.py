#!/usr/bin/env python3
"""
TESTE RÁPIDO - Verificação do banco PostgreSQL
"""

import psycopg2
import json

def quick_check():
    """Verificação rápida do banco"""
    
    db_config = {
        "host": "159.65.183.73",
        "database": "raiox",
        "user": "raiox_user", 
        "password": "Xc7!rA2v9Z@1pQ3y",
        "port": 5432
    }
    
    try:
        print("🔌 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print("✅ Conectado com sucesso!")
        
        # Verificar tabela implants
        cur.execute("SELECT COUNT(*) FROM implants;")
        total = cur.fetchone()[0]
        
        print(f"📊 Total de implantes: {total}")
        
        if total > 0:
            # Verificar alguns registros
            cur.execute("SELECT id, name, manufacturer FROM implants LIMIT 3;")
            samples = cur.fetchall()
            
            print("🔍 Amostras:")
            for id, name, manufacturer in samples:
                print(f"   - ID {id}: {manufacturer} {name}")
            
            print("✅ BANCO POPULADO COM SUCESSO!")
            return True
        else:
            print("❌ Tabela vazia!")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = quick_check()
    print(f"Resultado: {'SUCESSO' if success else 'FALHA'}")

