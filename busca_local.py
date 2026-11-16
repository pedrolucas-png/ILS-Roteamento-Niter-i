
import csv

# Carregar matriz de distâncias
with open("matriz_distancias.csv", "r", encoding="utf-8-sig") as arquivo:
    matriz = [
        [float(valor) for valor in linha]
        for linha in csv.reader(arquivo)
    ]

# Carregar a rota inicial
with open("rota_inicial.csv", "r", encoding="utf-8-sig") as arquivo:
    leitor = csv.DictReader(arquivo)
    rota_inicial = [int(linha["no"]) for linha in leitor]


def calcular_distancia(rota):
    return sum(
        matriz[rota[i]][rota[i + 1]]
        for i in range(len(rota) - 1)
    )


def dois_opt(rota):
    melhor_rota = rota[:]
    melhor_distancia = calcular_distancia(melhor_rota)

    melhorou = True

    while melhorou:
        melhorou = False

        for i in range(1, len(melhor_rota) - 2):
            for j in range(i + 1, len(melhor_rota) - 1):

                nova_rota = (
                    melhor_rota[:i]
                    + melhor_rota[i:j + 1][::-1]
                    + melhor_rota[j + 1:]
                )

                nova_distancia = calcular_distancia(nova_rota)

                if nova_distancia < melhor_distancia - 1e-9:
                    melhor_rota = nova_rota
                    melhor_distancia = nova_distancia
                    melhorou = True

        # Continua até não encontrar melhorias

    return melhor_rota, melhor_distancia


distancia_inicial = calcular_distancia(rota_inicial)

rota_otimizada, distancia_otimizada = dois_opt(rota_inicial)

melhoria = (
    (distancia_inicial - distancia_otimizada)
    / distancia_inicial
) * 100

print("RESULTADO DA BUSCA LOCAL 2-OPT")
print("-" * 50)
print("Rota inicial:", rota_inicial)
print("Rota otimizada:", rota_otimizada)
print(f"Distância inicial: {distancia_inicial:.2f} km")
print(f"Distância otimizada: {distancia_otimizada:.2f} km")
print(f"Redução: {melhoria:.2f}%")

with open(
    "rota_2opt.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as arquivo:
    escritor = csv.writer(arquivo)
    escritor.writerow(["ordem", "no"])

    for ordem, no in enumerate(rota_otimizada):
        escritor.writerow([ordem, no])

print("\nArquivo rota_2opt.csv criado!")
