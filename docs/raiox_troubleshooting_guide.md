# RAIOX AI - DOCUMENTAÇÃO DE TROUBLESHOOTING

## PROBLEMAS RECORRENTES E SOLUÇÕES

### 1. ERRO: `operator does not exist: vector <-> numeric[]`
**CAUSA:** Bind parameters não são convertidos para tipo vector
**SOLUÇÃO:** Usar `::vector` no cast: `embedding <-> %(query_vector)s::vector`

### 2. ERRO: `%%(query_vector)s` - Duplicação de %
**CAUSA:** SQLAlchemy escapa automaticamente % para %% com text()
**SOLUÇÃO:** Usar psycopg2 direto ou sintaxe correta para SQLAlchemy

### 3. ERRO: `permission denied for table implants`
**CAUSA:** Usuário raiox_user sem permissões na tabela
**SOLUÇÃO:** `GRANT SELECT ON implants TO raiox_user;`

### 4. ERRO: `syntax error at or near ":"`
**CAUSA:** PostgreSQL não aceita sintaxe `:parameter` do SQLAlchemy
**SOLUÇÃO:** Usar `%s` com psycopg2 ou sintaxe correta

### 5. FUNÇÃO RETORNA LISTA VAZIA `[]`
**CAUSA:** Função find_similar_implants hardcoded para retornar []
**SOLUÇÃO:** Implementar busca real no PostgreSQL

## CHECKLIST DE VALIDAÇÃO COMPLETA

### ANTES DE DECLARAR SUCESSO:
- [ ] Teste end-to-end com imagem real
- [ ] Verificar logs sem erros
- [ ] Validar JSON estruturado retornado
- [ ] Confirmar dados no PostgreSQL
- [ ] Testar busca de similaridade

### PROTOCOLO DE MUDANÇAS:
1. **SEMPRE fazer backup** antes de alterar código
2. **Validar sintaxe** antes de restart
3. **Testar gradualmente** sem quebrar funcionamento
4. **Documentar problemas** encontrados
5. **Preparar rollback** antes de aplicar mudanças

### COMANDOS DE ROLLBACK:
```bash
# Restaurar main.py
cp /opt/raiox-app/app/main.py.backup_YYYYMMDD_HHMMSS /opt/raiox-app/app/main.py
systemctl restart raiox-api

# Verificar status
systemctl status raiox-api
```

## ARQUITETURA VALIDADA

### FLUXO COMPLETO FUNCIONANDO:
1. **Upload de imagem** → FastAPI recebe
2. **Processamento CLIP** → Gera embedding 512D
3. **Upload para Spaces** → Armazena imagem
4. **Busca PostgreSQL** → pgvector similarity search
5. **Retorno JSON** → Lista de implantes similares

### COMPONENTES VALIDADOS:
- ✅ **CLIP Staging (45.55.128.141)**: FastAPI + CLIP funcionando
- ✅ **PostgreSQL (159.65.183.73)**: 32 implantes + pgvector
- ✅ **DigitalOcean Spaces**: Upload de imagens
- ✅ **Busca de similaridade**: Retorna top 3 similares

### DADOS DE TESTE:
- **32 implantes reais** de 4 fabricantes
- **Nobel Biocare**: 8 implantes
- **Straumann**: 8 implantes  
- **Neodent**: 8 implantes
- **Zimmer**: 8 implantes

## LIÇÕES APRENDIDAS

1. **NÃO declarar "100% funcionando"** sem teste completo
2. **SEMPRE documentar** problemas recorrentes
3. **VALIDAR fluxo end-to-end** antes de confirmar sucesso
4. **MANTER backups** e planos de rollback
5. **LEMBRAR de edições manuais** anteriores

---
**Data:** 11/06/2025
**Status:** Sistema validado e funcionando completamente

