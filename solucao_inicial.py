
import csv

# Carregar matriz de distâncias
with open(
    "matriz_distancias.csv",
    "r",
    encoding="utf-8-sig"
) as arquivo:
    matriz = [
        [float(valor) for valor in linha]
        for linha in csv.reader(arquivo)
    ]

n = len(matriz)

# Depósito é o nó 0
atual = 0
nao_visitados = set(range(1, n))
rota = [0]

while nao_visitados:
    proximo = min(
        nao_visitados,
        key=lambda j: matriz[atual][j]
    )

    rota.append(proximo)
    nao_visitados.remove(proximo)
    atual = proximo

# Retornar ao depósito
rota.append(0)

# Calcular distância total
distancia_total = sum(
    matriz[rota[i]][rota[i + 1]]
    for i in range(len(rota) - 1)
)

print("SOLUÇÃO INICIAL — VIZINHO MAIS PRÓXIMO")
print("-" * 50)
print("Rota:", rota)
print("Pontos atendidos:", len(rota) - 2)
print(f"Distância total: {distancia_total:.2f} km")

# Salvar resultado
with open(
    "rota_inicial.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as arquivo:
    escritor = csv.writer(arquivo)
    escritor.writerow(["ordem", "no"])

    for ordem, no in enumerate(rota):
        escritor.writerow([ordem, no])

print("\nArquivo rota_inicial.csv criado!")
