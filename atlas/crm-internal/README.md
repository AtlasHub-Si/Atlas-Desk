# AtlasHub Internal Group CRM (`crm.atlas-si.com`)

Configuração do **Atlas-Crm-OS** (baseado em [DeskcommCRM](https://github.com/melgarafael/DeskcommCRM), licença **MIT** preservada integralmente) para operar como o **CRM Interno Multi-Atividades do Grupo AtlasHub.SI** — **não** como SaaS comercial aberto.

## Regras de Governança Aplicadas

1. **Cadastro Fechado por Padrão (`SIGNUP_MODE=so_convite`):**
   - Novos usuários só entram por convite administrativo gerado pela equipe **AtlasHub.SI**.
2. **Multi-Atividades / Multi-Unidades Internas (`units_and_pipelines.json`):**
   - `AtlasHub-Institutional` (Empresa Mãe · Parcerias & B2B)
   - `AtlasClub-Commercial` (Funil Free → Premium, Cursos Pagos, Mentorias VIP, Projetos)
   - `AtlasRadar-Media` (AtlasNews / Parcerias / Patrocínios)
   - `AtlasHarness-Projects` (Implementações Agênticas, AtlasDesk & Consultoria)
3. **Banco de Dados (Sem Destruição):**
   - Suporta **Supabase Master AtlasHub** (conforme `docs/atlashub/FOUNDATION-01.md`) *ou* **Supabase/Postgres dedicado na VPS**.
   - **Nunca** execute resets ou drops em schemas compartilhados. Faça backup antes de aplicar migrations novas.
4. **Ponte Bidirecional com `pay.atlas-si.com` (`AtlasPayBridge`):**
   - **Entrada (`pay.atlas-si.com → crm.atlas-si.com`):** Toda venda via Hotmart, Whop ou Checkout Direto cria/atualiza o cliente no CRM.
   - **Saída (`crm.atlas-si.com → pay.atlas-si.com`):** Ao fechar um negócio manual/B2B (`WON`), o script `crm_to_bridge_trigger.py` (ou automação do CRM) aciona `POST /api/grants` e libera automaticamente o aluno em **`club.atlashub.si`**.

## Como subir na VPS (junto do stack mestre ou isolado)

```bash
cd atlas/crm-internal
cp .env.crm.atlas-si.com.example .env
# Preencha Supabase (Master ou isolado), WAHA_HMAC_SECRET, INTERNAL_SECRET e PAY_BRIDGE_ADMIN_KEY
docker compose -f ../../docker-compose.prod.yml -f docker-compose.crm.yml --env-file .env up -d
```

Para testar o gatilho CRM → AtlasPayBridge localmente:
```bash
python crm_to_bridge_trigger.py --bridge-url http://127.0.0.1:8790 --admin-key atlas-dev-admin-key --email cliente@empresa.com --name "Cliente Teste" --offer club_premium --unit AtlasClub-Commercial
```
