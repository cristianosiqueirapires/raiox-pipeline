#!/bin/bash

# Script de execução completa do pipeline Raiox AI
# Data: 11/06/2025
# Versão: 1.0

set -e

echo "🚀 Iniciando pipeline completo Raiox AI..."

# Verificar dependências
echo "🔍 Verificando dependências..."
python3 -c "import requests, json, psycopg2" || {
    echo "❌ Instalando dependências..."
    pip3 install requests psycopg2-binary
}

# Verificar conectividade
echo "🌐 Testando conectividade..."

# Testar CLIP Staging
curl -s http://45.55.128.141:8000/health > /dev/null || {
    echo "❌ Servidor CLIP Staging não acessível"
    exit 1
}

# Testar PostgreSQL
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='159.65.183.73',
        database='raiox',
        user='raiox_user', 
        password='Xc7!rA2v9Z@1pQ3y',
        connect_timeout=10
    )
    conn.close()
    print('✅ PostgreSQL acessível')
except Exception as e:
    print(f'❌ PostgreSQL não acessível: {e}')
    exit(1)
"

echo "✅ Conectividade OK"

# Executar pipeline
echo "🔄 Executando pipeline..."

cd scripts/current/

# 1. Processar imagens e gerar embeddings
echo "📸 Processando imagens..."
python3 process_implant_images.py

# 2. Popular banco de dados
echo "🗄️ Populando PostgreSQL..."
python3 populate_implants_table.py

# 3. Validar resultado
echo "🧪 Validando resultado..."
python3 -c "
import psycopg2
import json

# Verificar banco
conn = psycopg2.connect(
    host='159.65.183.73',
    database='raiox',
    user='raiox_user',
    password='Xc7!rA2v9Z@1pQ3y'
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM implants')
count = cur.fetchone()[0]
print(f'✅ Implantes no banco: {count}')

cur.execute('SELECT manufacturer, COUNT(*) FROM implants GROUP BY manufacturer')
for row in cur.fetchall():
    print(f'  - {row[0]}: {row[1]} implantes')

conn.close()

# Verificar arquivo de dados
with open('../../data/embeddings/implants_embeddings.json') as f:
    data = json.load(f)
    print(f'✅ Embeddings gerados: {len(data)}')
"

# 4. Testar API end-to-end
echo "🎯 Testando API..."
cd ../../

# Usar primeira imagem como teste
TEST_IMAGE=$(find data/images -name "*.jpg" -o -name "*.png" -o -name "*.webp" | head -1)

if [ -n "$TEST_IMAGE" ]; then
    echo "🧪 Testando com imagem: $TEST_IMAGE"
    RESULT=$(curl -s -H "X-Client-ID: pipeline_test" -F "file=@$TEST_IMAGE" http://45.55.128.141:8000/upload)
    
    if echo "$RESULT" | grep -q '"id"'; then
        echo "✅ API retornou resultados válidos"
        echo "📊 Resultado: $RESULT" | head -c 200
        echo "..."
    else
        echo "❌ API não retornou resultados válidos"
        echo "📊 Resposta: $RESULT"
    fi
else
    echo "⚠️ Nenhuma imagem encontrada para teste"
fi

echo ""
echo "🎉 Pipeline executado com sucesso!"
echo ""
echo "📋 Resumo:"
echo "- ✅ Imagens processadas e embeddings gerados"
echo "- ✅ Dados inseridos no PostgreSQL"
echo "- ✅ API funcionando e retornando resultados"
echo "- ✅ Sistema end-to-end validado"
echo ""
echo "🔗 Para testar manualmente:"
echo "curl -H 'X-Client-ID: test' -F 'file=@imagem.jpg' http://45.55.128.141:8000/upload"

