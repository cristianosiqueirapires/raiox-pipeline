# Raiox AI - Pipeline de Processamento

## 🎯 Pipeline Completo Funcionando (11/06/2025)

Este repositório contém o **pipeline completo e funcional** para processamento de imagens e geração de embeddings do sistema Raiox AI.

### ✅ Status Validado
- **32 implantes reais** processados e inseridos
- **Pipeline end-to-end** funcionando
- **Integração CLIP + PostgreSQL** operacional
- **Scripts de produção** testados e validados

### 🏗️ Estrutura do Repositório

```
raiox-pipeline/
├── scripts/
│   ├── current/                    # Scripts atuais funcionais
│   │   ├── process_implant_images.py    # Processamento principal
│   │   └── populate_implants_table.py   # População do PostgreSQL
│   └── legacy/                     # Scripts históricos
├── data/
│   ├── embeddings/                 # Dados de embeddings
│   │   └── implants_embeddings.json     # 32 implantes processados
│   ├── images/                     # Imagens processadas
│   └── *.json                      # Metadados e relatórios
├── docs/
│   └── raiox_troubleshooting_guide.md   # Guia de troubleshooting
└── README.md
```

### 🔄 Pipeline Atual Funcionando

#### 1. Coleta de Imagens Reais
```bash
# Busca automática de imagens por fabricante
- Nobel Biocare: 8 implantes
- Straumann: 8 implantes  
- Neodent: 8 implantes
- Zimmer: 8 implantes
```

#### 2. Processamento CLIP
```python
# Gera embeddings 512D via API CLIP Staging
python3 scripts/current/process_implant_images.py
```

#### 3. População PostgreSQL
```python
# Insere dados no banco com pgvector
python3 scripts/current/populate_implants_table.py
```

### 📊 Dados Processados

**32 implantes reais** com metadados completos:

```json
{
  "id": 1,
  "name": "Nobel Biocare Implant 1",
  "manufacturer": "Nobel Biocare",
  "model": "Replace Select",
  "diameter": "4.3mm",
  "length": "10mm",
  "image_url": "https://raiox-images.nyc3.digitaloceanspaces.com/referencia/M7ZMEtGI2liC.jpg",
  "embedding": [0.1234, 0.5678, ...] // 512 dimensões
}
```

### 🧪 Fluxo de Validação

#### Teste End-to-End
```bash
# 1. Processar imagens
cd scripts/current/
python3 process_implant_images.py

# 2. Popular banco
python3 populate_implants_table.py

# 3. Testar API
curl -H "X-Client-ID: test123" \
     -F "file=@imagem.jpg" \
     http://45.55.128.141:8000/upload
```

#### Resultado Esperado
```json
[
  {
    "name": "Nobel Biocare Implant 2",
    "manufacturer": "Nobel Biocare",
    "type": null,
    "image_url": "https://raiox-images.nyc3.digitaloceanspaces.com/referencia/SEpl3TF2HXyV.webp",
    "id": 2
  }
]
```

### 🔧 Scripts Principais

#### process_implant_images.py
- Busca imagens reais via API de busca
- Processa com CLIP para gerar embeddings
- Organiza metadados por fabricante
- Salva dados estruturados em JSON

#### populate_implants_table.py
- Conecta ao PostgreSQL via psycopg2
- Insere embeddings com cast correto (::vector)
- Configura permissões necessárias
- Valida inserção dos dados

### 📈 Métricas de Sucesso

- ✅ **100% das imagens** processadas com sucesso
- ✅ **32 embeddings** gerados corretamente
- ✅ **Busca de similaridade** retornando resultados
- ✅ **Zero erros** no pipeline de produção

### 🚨 Troubleshooting

Ver `docs/raiox_troubleshooting_guide.md` para:
- Problemas SQL recorrentes
- Erros de permissão PostgreSQL
- Falhas de conexão
- Soluções definitivas documentadas

### 🔗 Integração com Servidores

- **CLIP Staging (45.55.128.141)**: Processamento de imagens
- **PostgreSQL (159.65.183.73)**: Armazenamento de embeddings
- **DigitalOcean Spaces**: Armazenamento de imagens

### 📋 Comandos Úteis

```bash
# Verificar dados processados
python3 -c "
import json
with open('data/embeddings/implants_embeddings.json') as f:
    data = json.load(f)
    print(f'Total implantes: {len(data)}')
    for item in data[:3]:
        print(f'- {item[\"name\"]} ({item[\"manufacturer\"]})')
"

# Testar conexão PostgreSQL
python3 -c "
import psycopg2
conn = psycopg2.connect(
    host='159.65.183.73',
    database='raiox', 
    user='raiox_user',
    password='Xc7!rA2v9Z@1pQ3y'
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM implants')
print(f'Implantes no banco: {cur.fetchone()[0]}')
conn.close()
"
```

### 🎯 Próximos Passos

1. **Webhook Jotform**: Integração com formulários
2. **Sistema Admin**: Interface de gerenciamento
3. **Produção**: Deploy em ambiente final
4. **Terraform**: Infraestrutura como código

---

**Última atualização:** 11/06/2025  
**Status:** ✅ Pipeline 100% funcional e validado

