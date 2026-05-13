import os
import re
import time
import requests
import pandas as pd
from urllib.parse import urlparse

ARQUIVO_ENTRADA = "startups.csv"
ARQUIVO_SAIDA = "resultado_final.csv"

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
CNPJ_REGEX = r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}"


def ler_csv_flexivel(caminho):
    encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252"]
    for enc in encodings:
        try:
            return pd.read_csv(caminho, encoding=enc)
        except Exception:
            continue
    raise ValueError("Erro ao ler CSV. Salve como CSV UTF-8 ou ANSI.")


def normalizar_colunas(df):
    df.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]
    return df


def descobrir_coluna_nome(df):
    candidatas = [
        "nome_fantasia",
        "nome_startup",
        "startup",
        "nome",
        "empresa",
    ]
    for c in candidatas:
        if c in df.columns:
            return c
    raise ValueError(
        f"Não encontrei a coluna de nome. Colunas encontradas: {list(df.columns)}"
    )


def limpar_cnpj(cnpj):
    if not cnpj:
        return None
    numeros = re.sub(r"\D", "", str(cnpj))
    return numeros if len(numeros) == 14 else None


def formatar_cnpj(cnpj):
    cnpj = limpar_cnpj(cnpj)
    if not cnpj:
        return None
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def extrair_cnpj(texto):
    if not texto:
        return None
    match = re.search(CNPJ_REGEX, texto)
    if match:
        return limpar_cnpj(match.group())
    return None


def buscar_site_e_cnpj(nome):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'"{nome}" cnpj empresa',
        "hl": "pt-br",
        "gl": "br",
        "api_key": SERPAPI_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        resultados = data.get("organic_results", [])

        site = None
        cnpj = None

        for res in resultados[:10]:
            link = res.get("link")
            if link and not site:
                dominio = urlparse(link).netloc.replace("www.", "")
                site = dominio

            texto = (res.get("title", "") + " " + res.get("snippet", ""))
            encontrado = extrair_cnpj(texto)
            if encontrado:
                cnpj = encontrado

            if site and cnpj:
                break

        return site, cnpj

    except Exception as e:
        print(f"Erro na busca de '{nome}': {e}")
        return None, None


def consultar_cnpj_ws(cnpj):
    cnpj_limpo = limpar_cnpj(cnpj)
    if not cnpj_limpo:
        return None

    url = f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}"

    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"Erro CNPJ.ws: {r.status_code} para {cnpj_limpo}")
            return None

        data = r.json()
        est = data.get("estabelecimento", {}) or {}

        rua = " ".join(filter(None, [
            est.get("tipo_logradouro"),
            est.get("logradouro"),
            est.get("numero")
        ])).strip()

        cidade = est.get("cidade", {}) or {}
        estado = est.get("estado", {}) or {}

        return {
            "cnpj": formatar_cnpj(cnpj_limpo),
            "rua": rua or None,
            "cidade": cidade.get("nome"),
            "estado": estado.get("sigla"),
            "cep": est.get("cep"),
            "pais": "Brasil"
        }

    except Exception as e:
        print(f"Erro API CNPJ.ws para {cnpj_limpo}: {e}")
        return None


def main():
    if not SERPAPI_KEY:
        raise ValueError("A variável de ambiente SERPAPI_KEY não está definida.")

    df = ler_csv_flexivel(ARQUIVO_ENTRADA)
    df = normalizar_colunas(df)
    coluna_nome = descobrir_coluna_nome(df)

    print("Colunas detectadas:", list(df.columns))
    print("Usando coluna de entrada:", coluna_nome)

    resultados = []

    for i, row in df.iterrows():
        nome = str(row[coluna_nome]).strip()

        if not nome or nome.lower() == "nan":
            resultados.append({
                "nome_fantasia": None,
                "site": None,
                "cnpj": None,
                "rua": None,
                "cidade": None,
                "estado": None,
                "cep": None,
                "pais": None,
                "status": "nome vazio"
            })
            continue

        print(f"[{i+1}/{len(df)}] {nome}")

        site, cnpj = buscar_site_e_cnpj(nome)

        if not cnpj:
            resultados.append({
                "nome_fantasia": nome,
                "site": site,
                "cnpj": None,
                "rua": None,
                "cidade": None,
                "estado": None,
                "cep": None,
                "pais": None,
                "status": "cnpj não encontrado"
            })
            continue

        print(f"CNPJ encontrado: {formatar_cnpj(cnpj)}")

        dados = consultar_cnpj_ws(cnpj)
        time.sleep(21)

        if not dados:
            resultados.append({
                "nome_fantasia": nome,
                "site": site,
                "cnpj": formatar_cnpj(cnpj),
                "rua": None,
                "cidade": None,
                "estado": None,
                "cep": None,
                "pais": None,
                "status": "erro api"
            })
            continue

        resultados.append({
            "nome_fantasia": nome,
            "site": site,
            "cnpj": dados["cnpj"],
            "rua": dados["rua"],
            "cidade": dados["cidade"],
            "estado": dados["estado"],
            "cep": dados["cep"],
            "pais": dados["pais"],
            "status": "ok"
        })

    df_final = pd.DataFrame(resultados)
    df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print("\n✅ Arquivo resultado_final.csv gerado com sucesso!")


if __name__ == "__main__":
    main()