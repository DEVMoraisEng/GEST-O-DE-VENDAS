# -*- coding: utf-8 -*-
"""
Gera o data_vendas.json enxuto do PAINEL-VENDAS.

Lê o data.json completo publicado pelo repositório CONTROLES-INTERNOS e mantém
apenas o que as duas páginas deste painel usam:

  vendas.html          -> data.vendas
  casas-vendidas.html  -> data.vendas, data.metas e data.documentos
                          (dos documentos só interessam ENDERECO e DATA_CERTIDOES,
                           usados no KPI "Prazo Médio Certidões -> Venda")

Tudo mais (pagamentos_full, faturamentos_erp, obras_erp, pagamentos_detalhe...)
é descartado — é o que faz o data.json original passar de 4 MB.

Uso:
    python gerar_dados_vendas.py
    SOURCE_DATA_URL=https://.../data.json python gerar_dados_vendas.py
    python gerar_dados_vendas.py caminho/local/data.json     (modo offline)
"""
import io
import json
import os
import sys
import urllib.request

# URL do data.json completo publicado pelo painel de controle interno.
# Confira se o endereço do GitHub Pages do repositório CONTROLES-INTERNOS é este.
SOURCE_DATA_URL = os.environ.get(
    "SOURCE_DATA_URL",
    "https://devmoraiseng.github.io/CONTROLES-INTERNOS/data.json",
)
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_vendas.json")

# Campos de DOCUMENTOS realmente usados pelo painel
CAMPOS_DOC = ("endereco", "data_certidoes")


def baixar(url):
    print("Baixando: %s" % url)
    req = urllib.request.Request(url, headers={"User-Agent": "painel-vendas-bot"})
    with urllib.request.urlopen(req, timeout=120) as r:
        bruto = r.read()
    print("  %.2f MB recebidos" % (len(bruto) / 1048576.0))
    return json.loads(bruto.decode("utf-8"))


def carregar_local(caminho):
    print("Lendo arquivo local: %s" % caminho)
    with io.open(caminho, encoding="utf-8") as f:
        return json.load(f)


def enxugar(data):
    vendas = data.get("vendas") or []
    metas = data.get("metas") or []
    docs = []
    for d in data.get("documentos") or []:
        # só entra no arquivo se tiver algo aproveitável
        if not d.get("endereco"):
            continue
        docs.append({k: d.get(k) for k in CAMPOS_DOC})

    return {
        "updated_at": data.get("updated_at"),
        "gerado_por": "gerar_dados_vendas.py",
        "vendas": vendas,
        "metas": metas,
        "documentos": docs,
    }


def main():
    if len(sys.argv) > 1:
        data = carregar_local(sys.argv[1])
    else:
        data = baixar(SOURCE_DATA_URL)

    saida = enxugar(data)

    if not saida["vendas"]:
        # trava de segurança: nunca sobrescrever com um arquivo vazio
        raise SystemExit("ERRO: nenhuma venda encontrada na origem — abortando "
                         "para não publicar um data_vendas.json vazio.")

    with io.open(SAIDA, "w", encoding="utf-8") as f:
        f.write(json.dumps(saida, ensure_ascii=False, separators=(",", ":")))

    tam = os.path.getsize(SAIDA) / 1024.0
    print("OK -> data_vendas.json  (%.0f KB)" % tam)
    print("   vendas ....... %d" % len(saida["vendas"]))
    print("   metas ........ %d" % len(saida["metas"]))
    print("   documentos ... %d (somente %s)" % (len(saida["documentos"]), ", ".join(CAMPOS_DOC)))
    print("   updated_at ... %s" % saida["updated_at"])


if __name__ == "__main__":
    main()
