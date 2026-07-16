# PAINEL-VENDAS · Morais Engenharia

Painel dos **gestores de venda**. Site estático (GitHub Pages), sem login.

## Páginas

| Arquivo | O que é |
|---|---|
| `index.html` | Portal — resumo do ano + acesso aos 3 módulos |
| `vendas.html` | **Gestão de Vendas** — cópia da página do controle interno (tabela completa, filtros, export Excel) |
| `casas-vendidas.html` | **Casas Vendidas** — aba `METAS → CASAS VENDIDAS` do `analise.html`, extraída como página independente |
| *(link externo)* | **Central de Vendas** → https://devmoraiseng.github.io/SITE-DE-VENDAS/ |

## Dados

`data_vendas.json` (~374 KB) é gerado por `gerar_dados_vendas.py`, que baixa o
`data.json` completo do CONTROLES-INTERNOS (~4,7 MB) e mantém só:

- `vendas` — 381 registros, todos os campos
- `metas` — usado para meta de casas do ano (regra original: meta cadastrada no ano **anterior**)
- `documentos` — só `endereco` e `data_certidoes`, usados no KPI *Prazo Médio Certidões→Venda*

Tudo mais (`pagamentos_full` com 13.525 linhas, `faturamentos_erp`, `obras_erp`,
`pagamentos_detalhe`) é descartado — é o que pesa no arquivo original.

O script tem trava de segurança: se a origem vier vazia, ele aborta em vez de
publicar um JSON vazio.

## Como subir no GitHub (passo a passo)

1. Crie um repositório **público** chamado `PAINEL-VENDAS` na organização `devmoraiseng`.
2. Suba todos os arquivos desta pasta (inclusive `.github/workflows/`).
3. Em **Settings → Pages → Build and deployment → Source**, selecione **GitHub Actions**.
4. Em **Settings → Actions → General → Workflow permissions**, marque **Read and write permissions**.
5. Vá em **Actions → "Atualizar dados e publicar painel de vendas" → Run workflow**.
6. Pronto: https://devmoraiseng.github.io/PAINEL-VENDAS/

> ⚠️ **Confirme a URL de origem.** O workflow usa
> `SOURCE_DATA_URL: https://devmoraiseng.github.io/CONTROLES-INTERNOS/data.json`.
> Se o Pages do controle interno estiver em outro endereço, altere essa linha em
> `.github/workflows/atualizar_dados.yml`.

## Atualização automática

O workflow roda:

- a cada 4 h (`cron '30 */4 * * *'`, 30 min depois do ciclo do CONTROLES-INTERNOS);
- em todo `push` na `main`;
- manualmente (**Run workflow**) ou via cron-job.org;
- por `repository_dispatch` do tipo `dados-atualizados`.

### (Opcional) Atualizar na hora, junto com o controle interno

Para o painel atualizar no mesmo instante em que o `data.json` é regerado, crie um
PAT com escopo `repo` e salve como secret `PAT_DISPATCH` **no CONTROLES-INTERNOS**;
depois acrescente este passo ao final do `fetch_notion.yml` dele:

```yaml
      - name: Avisar o PAINEL-VENDAS
        run: |
          curl -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${{ secrets.PAT_DISPATCH }}" \
            https://api.github.com/repos/devmoraiseng/PAINEL-VENDAS/dispatches \
            -d '{"event_type":"dados-atualizados"}'
```

## Rodar localmente

```bash
python gerar_dados_vendas.py                 # baixa da URL de produção
python gerar_dados_vendas.py ../data.json    # usa um data.json local
python -m http.server 8000                   # abrir http://localhost:8000
```

`fetch()` não funciona abrindo o HTML com duplo clique (`file://`) — use o servidor local.

## Manutenção

`casas-vendidas.html` é um **recorte fiel** do `analise.html` (mesmo CSS, mesmas
funções `buildVendas`, `drawBars`, `drawLines`). Se a aba mudar lá, o recorte aqui
precisa ser refeito — não há herança automática entre os dois repositórios.
