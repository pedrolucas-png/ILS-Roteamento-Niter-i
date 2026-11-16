
import csv
import random
from collections import defaultdict, Counter
from pathlib import Path

ARQUIVO_PONTOS = Path("instancia_niteroi.csv")
ARQUIVO_MATRIZ = Path("matriz_viaria.csv")
PASTA_SAIDA = Path("instancias_experimento")

SEMENTE = 42
CONFIGURACOES = {
    10: 10,
    15: 10,
    20: 10,
    27: 1
}

PASTA_SAIDA.mkdir(exist_ok=True)

# Carregar dados originais
with open(ARQUIVO_PONTOS, encoding="utf-8-sig") as f:
    pontos = list(csv.DictReader(f))

with open(ARQUIVO_MATRIZ, encoding="utf-8-sig") as f:
    matriz = [
        [float(valor) for valor in linha]
        for linha in csv.reader(f)
    ]

ids = [int(p["id"]) for p in pontos]
n = len(pontos)

assert ids == list(range(n)), (
    "Os IDs não correspondem às linhas da matriz."
)

assert len(matriz) == n
assert all(len(linha) == n for linha in matriz)

# Agrupar clientes por modalidade
grupos = defaultdict(list)

for ponto in pontos:
    id_ponto = int(ponto["id"])

    if id_ponto != 0:
        grupos[ponto["modalidade"]].append(id_ponto)

modalidades = sorted(grupos)

total_clientes = sum(
    len(grupo) for grupo in grupos.values()
)

rng = random.Random(SEMENTE)

def calcular_cotas(tamanho):
    cotas = {
        m: tamanho * len(grupos[m]) / total_clientes
        for m in modalidades
    }

    quantidades = {
        m: int(cotas[m])
        for m in modalidades
    }

    faltantes = tamanho - sum(quantidades.values())

    ordem = sorted(
        modalidades,
        key=lambda m: (
            -(cotas[m] - quantidades[m]),
            m
        )
    )

    for m in ordem[:faltantes]:
        quantidades[m] += 1

    return quantidades


def selecionar_clientes(tamanho):
    quantidades = calcular_cotas(tamanho)
    selecionados = []

    for modalidade in modalidades:
        candidatos = grupos[modalidade]

        escolhidos = rng.sample(
            candidatos,
            quantidades[modalidade]
        )

        selecionados.extend(escolhidos)

    return sorted(selecionados)


def salvar_instancia(nome, selecionados):
    ids_originais = [0] + selecionados

    matriz_reduzida = [
        [matriz[i][j] for j in ids_originais]
        for i in ids_originais
    ]

    caminho_matriz = PASTA_SAIDA / f"{nome}_matriz.csv"
    caminho_pontos = PASTA_SAIDA / f"{nome}_pontos.csv"

    with open(
        caminho_matriz,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        csv.writer(f).writerows(matriz_reduzida)

    with open(
        caminho_pontos,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        campos = ["id_local"] + list(pontos[0].keys())

        escritor = csv.DictWriter(
            f,
            fieldnames=campos
        )

        escritor.writeheader()

        for id_local, id_original in enumerate(
            ids_originais
        ):
            registro = pontos[id_original].copy()
            registro["id_local"] = id_local
            escritor.writerow(registro)

    return ids_originais


print("GERAÇÃO DAS INSTÂNCIAS EXPERIMENTAIS")
print("=" * 65)

registro_instancias = []
conjuntos_gerados = set()

for tamanho, quantidade in CONFIGURACOES.items():

    print(f"\nGRUPO N{tamanho}")
    print("-" * 65)

    for numero in range(1, quantidade + 1):

        # Evitar instâncias duplicadas
        for tentativa in range(10000):
            selecionados = selecionar_clientes(tamanho)
            chave = tuple(selecionados)

            if chave not in conjuntos_gerados:
                conjuntos_gerados.add(chave)
                break
        else:
            raise RuntimeError(
                f"Não foi possível gerar instância única N{tamanho}"
            )

        nome = f"N{tamanho}_{numero:02d}"

        ids_originais = salvar_instancia(
            nome,
            selecionados
        )

        composicao = Counter(
            pontos[i]["modalidade"]
            for i in selecionados
        )

        registro_instancias.append({
            "instancia": nome,
            "clientes": tamanho,
            "total_nos": tamanho + 1,
            "semente_geracao": SEMENTE,
            "ids_originais": ";".join(
                map(str, ids_originais)
            ),
            **{
                m: composicao.get(m, 0)
                for m in modalidades
            }
        })

        print(
            f"{nome} | "
            f"{tamanho} clientes | "
            f"{dict(composicao)}"
        )

# Salvar registro para reprodutibilidade
arquivo_registro = (
    PASTA_SAIDA / "registro_instancias.csv"
)

with open(
    arquivo_registro,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    campos = list(registro_instancias[0].keys())

    escritor = csv.DictWriter(
        f,
        fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(registro_instancias)

print("\n" + "=" * 65)
print("TOTAL DE INSTÂNCIAS:", len(registro_instancias))
print("PASTA:", PASTA_SAIDA)
print("REGISTRO:", arquivo_registro)
print("GERAÇÃO CONCLUÍDA!")
