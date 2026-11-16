
import csv
import random
import statistics
import time
from pathlib import Path

PASTA = Path("instancias_experimento")
SEMENTES = range(10)
ITERACOES = 500

def carregar_matriz(caminho):
    with open(caminho, encoding="utf-8-sig") as f:
        return [
            [float(x) for x in linha]
            for linha in csv.reader(f)
        ]

def custo(rota, matriz):
    return sum(
        matriz[a][b]
        for a, b in zip(rota, rota[1:])
    )

def vizinho_mais_proximo(matriz):
    rota = [0]
    restantes = set(range(1, len(matriz)))

    while restantes:
        proximo = min(
            restantes,
            key=lambda j: (matriz[rota[-1]][j], j)
        )
        rota.append(proximo)
        restantes.remove(proximo)

    return rota + [0]

def dois_opt(rota, matriz):
    melhor = rota[:]
    melhor_custo = custo(melhor, matriz)

    while True:
        melhorou = False

        for i in range(1, len(melhor) - 2):
            for j in range(i + 1, len(melhor) - 1):
                candidata = (
                    melhor[:i]
                    + melhor[i:j + 1][::-1]
                    + melhor[j + 1:]
                )

                novo_custo = custo(candidata, matriz)

                if novo_custo < melhor_custo - 1e-9:
                    melhor = candidata
                    melhor_custo = novo_custo
                    melhorou = True
                    break

            if melhorou:
                break

        if not melhorou:
            break

    return melhor, melhor_custo

def perturbacao(rota, rng):
    clientes = rota[1:-1]

    if len(clientes) < 4:
        return rota[:]

    a, b, c = sorted(
        rng.sample(range(1, len(clientes)), 3)
    )

    novos = (
        clientes[:a]
        + clientes[b:c]
        + clientes[a:b]
        + clientes[c:]
    )

    return [0] + novos + [0]

def ils(matriz, semente):
    rng = random.Random(semente)

    inicial = vizinho_mais_proximo(matriz)
    atual, custo_atual = dois_opt(inicial, matriz)

    melhor = atual[:]
    melhor_custo = custo_atual

    for _ in range(ITERACOES):
        perturbada = perturbacao(atual, rng)

        candidata, custo_candidato = dois_opt(
            perturbada, matriz
        )

        if custo_candidato < custo_atual - 1e-9:
            atual = candidata
            custo_atual = custo_candidato

        if custo_candidato < melhor_custo - 1e-9:
            melhor = candidata[:]
            melhor_custo = custo_candidato

    return melhor, melhor_custo

def executar():
    resultados = []
    resumo = []

    arquivos = sorted(
        PASTA.glob("N*_matriz.csv"),
        key=lambda p: (
            int(p.stem.split("_")[0][1:]),
            int(p.stem.split("_")[1])
        )
    )

    print("EXPERIMENTO FINAL - ILS")
    print("=" * 65)
    print("Instâncias:", len(arquivos))
    print("Execuções por instância:", len(SEMENTES))
    print("Iterações por execução:", ITERACOES)

    for arquivo in arquivos:
        nome = arquivo.stem.replace("_matriz", "")
        matriz = carregar_matriz(arquivo)

        inicial = vizinho_mais_proximo(matriz)
        custo_inicial = custo(inicial, matriz)

        _, custo_2opt = dois_opt(inicial, matriz)

        distancias = []
        tempos = []

        print(f"\n{nome}", end=" | ", flush=True)

        for semente in SEMENTES:
            inicio = time.perf_counter()
            _, distancia = ils(matriz, semente)
            tempo = time.perf_counter() - inicio

            distancias.append(distancia)
            tempos.append(tempo)

            resultados.append({
                "instancia": nome,
                "semente": semente,
                "inicial_km": custo_inicial,
                "dois_opt_km": custo_2opt,
                "ils_km": distancia,
                "tempo_s": tempo
            })

            print(
                f"{distancia:.2f}",
                end=" ",
                flush=True
            )

        melhor = min(distancias)
        media = statistics.mean(distancias)
        desvio = statistics.stdev(distancias)

        melhoria = (
            (custo_inicial - melhor)
            / custo_inicial * 100
            if custo_inicial > 0 else 0
        )

        resumo.append({
            "instancia": nome,
            "clientes": len(matriz) - 1,
            "inicial_km": custo_inicial,
            "dois_opt_km": custo_2opt,
            "ils_melhor_km": melhor,
            "ils_media_km": media,
            "ils_desvio_km": desvio,
            "melhoria_pct": melhoria,
            "tempo_medio_s": statistics.mean(tempos),
            "tempo_minimo_s": min(tempos)
        })

        print(
            f"| Melhor: {melhor:.2f} km"
            f" | Melhoria: {melhoria:.2f}%"
        )

    with open(
        "resultados_ils_detalhados.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        escritor = csv.DictWriter(
            f, fieldnames=list(resultados[0])
        )
        escritor.writeheader()
        escritor.writerows(resultados)

    with open(
        "resultados_ils_resumo.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        escritor = csv.DictWriter(
            f, fieldnames=list(resumo[0])
        )
        escritor.writeheader()
        escritor.writerows(resumo)

    print("\n" + "=" * 65)
    print("EXPERIMENTO CONCLUÍDO")
    print("Execuções realizadas:", len(resultados))
    print("Arquivos gerados:")
    print(" - resultados_ils_detalhados.csv")
    print(" - resultados_ils_resumo.csv")

if __name__ == "__main__":
    executar()
