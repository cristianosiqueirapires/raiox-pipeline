# RAIOX AI - PIPELINE DE COLETA E PROCESSAMENTO
# Documentação completa para transferência entre chats Manus

## OBJETIVO
Executar pipeline completo de coleta de imagens reais de implantes, processamento com CLIP e população da tabela implants no staging.

## AMBIENTE
- **Staging CLIP**: 45.55.128.141 (SSH configurado)
- **PostgreSQL**: 159.65.183.73 (SSH configurado)
- **DigitalOcean Spaces**: raiox-images
- **Sessão tmux**: raiox_pipeline

## PROGRESSO ATUAL
- [x] Sistema CLIP 100% funcionando no staging
- [x] PostgreSQL com pgvector configurado
- [x] Tabela implants criada e vazia
- [x] DigitalOcean Spaces configurado
- [x] SSH configurado nos servidores
- [x] Sessão tmux criada
- [ ] **FASE 1**: Coletar imagens reais de implantes
- [ ] **FASE 2**: Processar e padronizar nomenclatura
- [ ] **FASE 3**: Upload para DigitalOcean Spaces
- [ ] **FASE 4**: Extrair embeddings com CLIP
- [ ] **FASE 5**: Popular tabela implants
- [ ] **FASE 6**: Documentar e testar

## COMANDOS IMPORTANTES
```bash
# Conectar ao staging
ssh -i ~/.ssh/raiox_key root@45.55.128.141

# Conectar ao PostgreSQL
ssh -i ~/.ssh/raiox_key root@159.65.183.73

# Verificar sessão tmux
tmux list-sessions
tmux attach-session -t raiox_pipeline
```

## CREDENCIAIS (.env no staging)
```
DATABASE_URL=postgresql+psycopg2://raiox_user:Xc7!rA2v9Z@1pQ3y@159.65.183.73/raiox
DO_SPACES_KEY=DO00CVCTFVXPANB4DD9M
DO_SPACES_SECRET=+nWSRpFnQ+MncvZKDdw/herwYQRo0YEvVHujg1YMmaA
DO_SPACES_BUCKET=raiox-images
DO_SPACES_REGION=nyc3
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

## ESTRUTURA DE NOMENCLATURA (do manual)
- Formato: `FABRICANTE_MODELO_DIAMETRO.jpg`
- Exemplos: `NOBEL_REPLACE_4.3mm.jpg`, `STRAUMANN_BL_4.1mm.jpg`

## FABRICANTES E MODELOS ALVO
- **Nobel Biocare**: Replace, Active, Conical Connection
- **Straumann**: Bone Level (BL), Bone Level Tapered (BLT), Tissue Level (TL)
- **Neodent**: Drive, Helix, Titamax
- **Zimmer**: Tapered Screw-Vent, SwissPlus

## PRÓXIMOS PASSOS
1. Buscar imagens no Google Images
2. Aplicar nomenclatura padronizada
3. Processar com CLIP no staging
4. Popular tabela implants

## LOGS DE ERRO
[Será atualizado conforme necessário]

---
**INICIADO EM**: 2025-06-11 05:00 UTC
**STATUS**: Executando Fase 1 - Coleta de Imagens

