
import csv
import random
import time

with open("matriz_distancias.csv", "r", encoding="utf-8-sig") as arquivo:
    matriz = [
        [float(valor) for valor in linha]
        for linha in csv.reader(arquivo)
    ]

with open("rota_2opt.csv", "r", encoding="utf-8-sig") as arquivo:
    rota_inicial = [
        int(linha["no"])
        for linha in csv.DictReader(arquivo)
    ]


def distancia(rota):
    return sum(
        matriz[rota[i]][rota[i + 1]]
        for i in range(len(rota) - 1)
    )


def dois_opt(rota):
    melhor = rota[:]
    custo = distancia(melhor)

    while True:
        encontrou = False

        for i in range(1, len(melhor) - 2):
            for j in range(i + 1, len(melhor) - 1):
                candidata = (
                    melhor[:i]
                    + melhor[i:j + 1][::-1]
                    + melhor[j + 1:]
                )

                novo_custo = distancia(candidata)

                if novo_custo < custo - 1e-9:
                    melhor = candidata
                    custo = novo_custo
                    encontrou = True
                    break

            if encontrou:
                break

        if not encontrou:
            break

    return melhor, custo


def perturbacao_double_bridge(rota):
    clientes = rota[1:-1]
    n = len(clientes)

    a, b, c = sorted(random.sample(range(1, n), 3))

    parte1 = clientes[:a]
    parte2 = clientes[a:b]
    parte3 = clientes[b:c]
    parte4 = clientes[c:]

    nova = parte1 + parte3 + parte2 + parte4

    return [0] + nova + [0]


def ils(rota, iteracoes=500, semente=42):
    random.seed(semente)

    atual, custo_atual = dois_opt(rota)
    melhor = atual[:]
    melhor_custo = custo_atual

    for _ in range(iteracoes):
        perturbada = perturbacao_double_bridge(atual)
        candidata, custo_candidata = dois_opt(perturbada)

        if custo_candidata < custo_atual - 1e-9:
            atual = candidata
            custo_atual = custo_candidata

        if custo_candidata < melhor_custo - 1e-9:
            melhor = candidata[:]
            melhor_custo = custo_candidata

    return melhor, melhor_custo


inicio = time.perf_counter()

rota_final, custo_final = ils(rota_inicial)

tempo = time.perf_counter() - inicio
custo_inicial = distancia(rota_inicial)

melhoria = 100 * (custo_inicial - custo_final) / custo_inicial

assert rota_final[0] == rota_final[-1] == 0
assert sorted(rota_final[1:-1]) == list(range(1, len(matriz)))

print("RESULTADO DO ILS")
print("-" * 50)
print("Rota:", rota_final)
print(f"Distância após 2-opt: {custo_inicial:.2f} km")
print(f"Distância após ILS: {custo_final:.2f} km")
print(f"Melhoria adicional: {melhoria:.2f}%")
print(f"Tempo de execução: {tempo:.2f} segundos")

with open("rota_ils.csv", "w", newline="", encoding="utf-8-sig") as arquivo:
    escritor = csv.writer(arquivo)
    escritor.writerow(["ordem", "no"])

    for ordem, no in enumerate(rota_final):
        escritor.writerow([ordem, no])

print("\nArquivo rota_ils.csv criado!")
