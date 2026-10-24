import os
import matplotlib.pyplot as plt

# Pontos conhecidos: (x1, y1) = (0, 4) e (x2, y2) = (100, 20)
x1, y1 = 0, 4
x2, y2 = 100, 20

# Calculando o coeficiente angular (a) e o coeficiente linear (b) da reta y = a*x + b
a = (y2 - y1) / (x2 - x1)
b = y1 - a * x1

# Calculando o valor de y (corrente) para x = 50 graus (temperatura)
x_alvo = 50
y_resultado = a * x_alvo + b

# Classificacao da temperatura: baixa (ate 30°C), media (ate 60°C) e alta (acima de 60°C)
if x_alvo <= 30:
    classificacao = "Baixa"
elif x_alvo <= 60:
    classificacao = "Media"
else:
    classificacao = "Alta"

print(f"Coeficiente A (inclinacao): {a}")
print(f"Coeficiente B (intercepto): {b}")
print(f"Equacao da reta: y = {a} * x + {b}")
print(f"Resultado para X = {x_alvo} °C: Corrente Y = {y_resultado} mA")
print(f"Classificacao da temperatura ({x_alvo} °C): {classificacao}")

# Avisos de limites de temperatura (0 a 100 °C) e corrente (4 a 20 mA)
if x_alvo < 0 or x_alvo > 100:
    print(f"AVISO: Temperatura ({x_alvo} °C) esta fora da faixa de 0 a 100 °C!")

if y_resultado < 4 or y_resultado > 20:
    print(f"AVISO: Corrente eletrica ({y_resultado} mA) esta fora da faixa de 4 a 20 mA!")

# Criando o grafico com Matplotlib
temperaturas = [x1, x_alvo, x2]
correntes = [y1, y_resultado, y2]

plt.figure(figsize=(8, 5))

# Faixas de cor no fundo do grafico para cada classificacao de temperatura
plt.axvspan(0, 30, color="skyblue", alpha=0.3, label="Baixa (0 a 30°C)")
plt.axvspan(30, 60, color="gold", alpha=0.3, label="Media (30 a 60°C)")
plt.axvspan(60, 100, color="salmon", alpha=0.3, label="Alta (60 a 100°C)")

plt.plot([x1, x2], [y1, y2], label="Reta do Sensor (y = ax + b)", color="blue", linewidth=2)
plt.scatter(temperaturas, correntes, color="red", zorder=5, label="Pontos (0°C, 50°C, 100°C)")

# Destacando o ponto calculado (X = 50) com a classificacao
plt.annotate(
    f"({x_alvo}°C, {y_resultado}mA) - Temp. {classificacao}",
    (x_alvo, y_resultado),
    textcoords="offset points",
    xytext=(0, 10),
    ha="center",
    fontweight="bold",
)

plt.title("Termometro: Corrente Eletrica vs Temperatura")
plt.xlabel("Temperatura (°C)")
plt.ylabel("Corrente Eletrica (mA)")
plt.xlim(0, 100)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper left")

# Salvando o grafico na pasta resultados/termometro/ conforme organizacao do projeto
pasta_saida = os.path.join("resultados", "termometro")
os.makedirs(pasta_saida, exist_ok=True)
caminho_grafico = os.path.join(pasta_saida, "grafico_termometro.png")
plt.savefig(caminho_grafico, dpi=150, bbox_inches="tight")
print(f"Grafico salvo em: {caminho_grafico}")
