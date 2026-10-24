import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# Configuracao visual padrao (qualidade de publicacao conforme skill chart-image)
plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "grid.color": "#cccccc",
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
})

# 1. Ler os dados originais de dados/fornecedores.csv (sem alterar o arquivo original)
caminho_entrada = os.path.join("dados", "fornecedores.csv")
fornecedores = []

with open(caminho_entrada, mode="r", encoding="utf-8") as f:
    leitor = csv.DictReader(f)
    for linha in leitor:
        fornecedores.append({
            "fornecedor": linha["fornecedor"],
            "preco_unitario": float(linha["preco_unitario"]),
            "prazo_dias": float(linha["prazo_dias"]),
            "defeitos_pct": float(linha["defeitos_pct"]),
            "suporte_nota": float(linha["suporte_nota"]),
        })

# 2. Converter criterios objetivos para escala de 1 a 10 conforme a skill decision-matrix:
melhor_preco = min(d["preco_unitario"] for d in fornecedores)
melhor_prazo = min(d["prazo_dias"] for d in fornecedores)
melhor_defeito = min(d["defeitos_pct"] for d in fornecedores)

for d in fornecedores:
    d["nota_preco"] = 10.0 * (melhor_preco / d["preco_unitario"])
    d["nota_prazo"] = 10.0 * (melhor_prazo / d["prazo_dias"])
    d["nota_qualidade"] = 10.0 * (melhor_defeito / d["defeitos_pct"])
    d["nota_suporte"] = d["suporte_nota"]

# 3. Definir pesos dos criterios (somando 100%)
pesos = {
    "preco": 0.30,      # 30% - Custo unitario
    "qualidade": 0.30,  # 30% - Baixo indice de defeitos
    "prazo": 0.25,      # 25% - Rapidez na entrega
    "suporte": 0.15,    # 15% - Qualidade do suporte
}

for d in fornecedores:
    d["pond_preco"] = d["nota_preco"] * pesos["preco"]
    d["pond_qualidade"] = d["nota_qualidade"] * pesos["qualidade"]
    d["pond_prazo"] = d["nota_prazo"] * pesos["prazo"]
    d["pond_suporte"] = d["nota_suporte"] * pesos["suporte"]
    d["nota_final"] = (
        d["pond_preco"]
        + d["pond_qualidade"]
        + d["pond_prazo"]
        + d["pond_suporte"]
    )

# Ordenar fornecedores do melhor para o pior
ranking = sorted(fornecedores, key=lambda x: x["nota_final"], reverse=True)
vencedor = ranking[0]
segundo = ranking[1]
margem_pct = ((vencedor["nota_final"] - segundo["nota_final"]) / segundo["nota_final"]) * 100

# 4. Analise de Sensibilidade (testando 4 cenarios de pesos)
cenarios = {
    "Base Equilibrado\n(30/30/25/15%)": (0.30, 0.30, 0.25, 0.15),
    "Pesos Iguais\n(25/25/25/25%)": (0.25, 0.25, 0.25, 0.25),
    "Foco em Custo\n(50/20/20/10%)": (0.50, 0.20, 0.20, 0.10),
    "Foco em Qualidade\n(15/40/30/15%)": (0.15, 0.40, 0.30, 0.15),
}

resultados_cenarios = {}
for nome_cenario, (p_preco, p_qual, p_prazo, p_sup) in cenarios.items():
    notas_cenario = []
    for d in fornecedores:
        total = (
            d["nota_preco"] * p_preco
            + d["nota_qualidade"] * p_qual
            + d["nota_prazo"] * p_prazo
            + d["nota_suporte"] * p_sup
        )
        notas_cenario.append((d["fornecedor"], total))
    notas_cenario.sort(key=lambda x: x[1], reverse=True)
    resultados_cenarios[nome_cenario] = notas_cenario

pasta_saida = os.path.join("resultados", "fornecedores")
os.makedirs(pasta_saida, exist_ok=True)
rodape_fonte = "Fonte: dados/fornecedores.csv | Escala iniciando em 0 (sem truncamento) | Metodologia: decision-matrix & chart-image"

# ==============================================================================
# GRAFICO 1: Painel Principal da Matriz de Decisao (resultados/grafico_fornecedores.png)
# ==============================================================================
nomes = [d["fornecedor"] for d in ranking]
notas_finais = [d["nota_final"] for d in ranking]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

cores_ranking = ["#0072B2" if i == 0 else "#9ECAE1" for i in range(len(nomes))]
barras = ax1.bar(nomes, notas_finais, color=cores_ranking, edgecolor="#222222", width=0.55)
ax1.set_title("A) Ranking Final Ponderado (Escala 0 a 10)", fontsize=12, fontweight="bold", pad=12)
ax1.set_xlabel("Fornecedor", fontsize=11, fontweight="bold")
ax1.set_ylabel("Nota Ponderada Total (pontos)", fontsize=11, fontweight="bold")
ax1.set_ylim(0, 11.0)
ax1.grid(axis="y")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

for i, (barra, nota) in enumerate(zip(barras, notas_finais)):
    sufixo = " (1º)" if i == 0 else ""
    ax1.text(
        barra.get_x() + barra.get_width() / 2,
        barra.get_height() + 0.25,
        f"{nota:.2f} pts{sufixo}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        color="#003366" if i == 0 else "#222222",
    )

# Painel B: Barras empilhadas
p_preco_vals = np.array([d["pond_preco"] for d in ranking])
p_qual_vals = np.array([d["pond_qualidade"] for d in ranking])
p_prazo_vals = np.array([d["pond_prazo"] for d in ranking])
p_sup_vals = np.array([d["pond_suporte"] for d in ranking])

b1 = p_preco_vals
b2 = b1 + p_qual_vals
b3 = b2 + p_prazo_vals

ax2.bar(nomes, p_preco_vals, label="Preço Unitário (peso 30%)", color="#009E73", edgecolor="#222222", width=0.55)
ax2.bar(nomes, p_qual_vals, bottom=b1, label="Qualidade / Sem Defeitos (peso 30%)", color="#0072B2", edgecolor="#222222", width=0.55)
ax2.bar(nomes, p_prazo_vals, bottom=b2, label="Prazo de Entrega (peso 25%)", color="#E69F00", edgecolor="#222222", width=0.55)
ax2.bar(nomes, p_sup_vals, bottom=b3, label="Nota de Suporte (peso 15%)", color="#CC79A7", edgecolor="#222222", width=0.55)

# Anotar valores dentro de cada segmento quando houver espaco suficiente
for i in range(len(nomes)):
    segmentos = [
        (p_preco_vals[i] / 2, p_preco_vals[i]),
        (b1[i] + p_qual_vals[i] / 2, p_qual_vals[i]),
        (b2[i] + p_prazo_vals[i] / 2, p_prazo_vals[i]),
        (b3[i] + p_sup_vals[i] / 2, p_sup_vals[i]),
    ]
    for y_pos, val in segmentos:
        if val >= 0.75:
            ax2.text(i, y_pos, f"{val:.2f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

ax2.set_title("B) Contribuição de Cada Critério na Nota Final", fontsize=12, fontweight="bold", pad=12)
ax2.set_xlabel("Fornecedor", fontsize=11, fontweight="bold")
ax2.set_ylabel("Pontos Ponderados Acumulados (0 a 10)", fontsize=11, fontweight="bold")
ax2.set_ylim(0, 11.5)
ax2.grid(axis="y")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.legend(loc="upper right", frameon=True, fontsize=9.5)

fig.suptitle("Matriz de Decisão: Avaliação Global dos 4 Fornecedores", fontsize=15, fontweight="bold", y=0.98)
fig.text(0.5, 0.01, rodape_fonte, ha="center", fontsize=9, style="italic", color="#444444")
plt.tight_layout(rect=[0, 0.03, 1, 0.94])

caminho_grafico_1 = os.path.join(pasta_saida, "grafico_fornecedores.png")
plt.savefig(caminho_grafico_1, dpi=180)
plt.close()

# ==============================================================================
# GRAFICO 2: Painel 2x2 das Metricas Originais (resultados/grafico_metricas_originais.png)
# ==============================================================================
nomes_orig = [d["fornecedor"] for d in ranking]
precos_orig = [d["preco_unitario"] for d in ranking]
prazos_orig = [d["prazo_dias"] for d in ranking]
defeitos_orig = [d["defeitos_pct"] for d in ranking]
suporte_orig = [d["suporte_nota"] for d in ranking]

fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))

config_paineis = [
    (axes[0, 0], precos_orig, "1) Preço Unitário — Menor é melhor", "Preço (R$)", "R$ {:.0f}", min(precos_orig), 130),
    (axes[0, 1], prazos_orig, "2) Prazo de Entrega — Menor é melhor", "Prazo (dias corridos)", "{:.0f} dias", min(prazos_orig), 14.5),
    (axes[1, 0], defeitos_orig, "3) Taxa de Defeitos — Menor é melhor", "Defeitos (%)", "{:.1f}%", min(defeitos_orig), 4.8),
    (axes[1, 1], suporte_orig, "4) Avaliação de Suporte — Maior é melhor", "Nota de Suporte (escala 0–10)", "{:.1f} / 10", max(suporte_orig), 11.2),
]

for ax, valores, titulo, ylabel, formato, melhor_val, y_max in config_paineis:
    cores = ["#009E73" if v == melhor_val else "#B3CDE3" for v in valores]
    bars = ax.bar(nomes_orig, valores, color=cores, edgecolor="#222222", width=0.52)
    ax.set_title(titulo, fontsize=11.5, fontweight="bold", pad=10)
    ax.set_xlabel("Fornecedor", fontsize=10, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=10, fontweight="bold")
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(0, y_max)
    ax.grid(axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for b, v in zip(bars, valores):
        destaque = " ★ Melhor" if v == melhor_val else ""
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + (y_max * 0.025),
            formato.format(v) + destaque,
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold" if v == melhor_val else "normal",
            color="#005A32" if v == melhor_val else "#222222",
        )

fig.suptitle("Indicadores Originais por Fornecedor (Dados Brutos com Unidades Explícitas)", fontsize=14, fontweight="bold", y=0.98)
fig.text(0.5, 0.01, "Fonte: dados/fornecedores.csv | Barras verdes (★) indicam o melhor desempenho em cada métrica individual", ha="center", fontsize=9, style="italic", color="#444444")
plt.tight_layout(rect=[0, 0.03, 1, 0.94])

caminho_grafico_2 = os.path.join(pasta_saida, "grafico_metricas_originais.png")
plt.savefig(caminho_grafico_2, dpi=180)
plt.close()

# ==============================================================================
# GRAFICO 3: Analise de Sensibilidade por Cenario (resultados/grafico_sensibilidade.png)
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 6))

nomes_cenarios = list(cenarios.keys())
x = np.arange(len(nomes_cenarios))
largura = 0.19

cores_forn = {
    "Delta": "#0072B2",
    "Beta": "#009E73",
    "Alfa": "#E69F00",
    "Gama": "#D55E00",
}

for idx, forn_nome in enumerate(["Delta", "Beta", "Alfa", "Gama"]):
    valores_cenario = []
    for nc in nomes_cenarios:
        mapa = dict(resultados_cenarios[nc])
        valores_cenario.append(mapa[forn_nome])

    deslocamento = (idx - 1.5) * largura
    rects = ax.bar(
        x + deslocamento,
        valores_cenario,
        largura,
        label=f"Fornecedor {forn_nome}",
        color=cores_forn[forn_nome],
        edgecolor="#222222",
    )
    for r, val in zip(rects, valores_cenario):
        ax.text(
            r.get_x() + r.get_width() / 2,
            r.get_height() + 0.18,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold" if forn_nome == "Delta" else "normal",
        )

ax.set_title("Análise de Sensibilidade: Nota Final sob Diferentes Cenários de Pesos (Preço/Qualidade/Prazo/Suporte)", fontsize=12.5, fontweight="bold", pad=14)
ax.set_xlabel("Cenário de Pesos Testado", fontsize=11, fontweight="bold")
ax.set_ylabel("Nota Ponderada Final (escala 0 a 10)", fontsize=11, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(nomes_cenarios, fontsize=10)
ax.set_ylim(0, 11.2)
ax.grid(axis="y")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper right", frameon=True, fontsize=10)

fig.text(0.5, 0.01, "Fonte: dados/fornecedores.csv | O fornecedor Delta mantém o 1º lugar em todos os cenários simulados", ha="center", fontsize=9, style="italic", color="#444444")
plt.tight_layout(rect=[0, 0.03, 1, 0.96])

caminho_grafico_3 = os.path.join(pasta_saida, "grafico_sensibilidade.png")
plt.savefig(caminho_grafico_3, dpi=180)
plt.close()

# ==============================================================================
# GRAFICO 4: Grafico de Radar Normalizado 0-10 (resultados/grafico_radar_fornecedores.png)
# ==============================================================================
categorias = [
    "Preço Competitivo\n(peso 30%)",
    "Qualidade / Sem Defeitos\n(peso 30%)",
    "Rapidez no Prazo\n(peso 25%)",
    "Suporte Técnico\n(peso 15%)",
]
N = len(categorias)
angulos = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angulos += angulos[:1]

fig, ax = plt.subplots(figsize=(9.5, 8.0), subplot_kw=dict(polar=True))

estilos_radar = {
    "Delta": ("#0072B2", "-", 2.6, 0.20),
    "Beta": ("#009E73", "--", 2.0, 0.10),
    "Alfa": ("#E69F00", "-.", 1.8, 0.05),
    "Gama": ("#D55E00", ":", 1.8, 0.05),
}

for d in ranking:
    nome_f = d["fornecedor"]
    valores = [
        d["nota_preco"],
        d["nota_qualidade"],
        d["nota_prazo"],
        d["nota_suporte"],
    ]
    valores += valores[:1]
    cor, estilo_linha, espessura, alpha_fill = estilos_radar[nome_f]
    ax.plot(angulos, valores, color=cor, linestyle=estilo_linha, linewidth=espessura, marker="o", label=f"{nome_f} (Final: {d['nota_final']:.2f})")
    ax.fill(angulos, valores, color=cor, alpha=alpha_fill)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_xticks(angulos[:-1])
ax.set_xticklabels(["", "", "", ""])

# Posicionar rotulos manualmente fora do circulo para evitar qualquer sobreposicao
rotulos_pos = [
    (0, 11.7, "Preço Competitivo\n(peso 30%)", "center", "bottom"),
    (np.pi / 2, 11.4, "Qualidade /\nSem Defeitos\n(peso 30%)", "left", "center"),
    (np.pi, 11.7, "Rapidez no Prazo\n(peso 25%)", "center", "top"),
    (3 * np.pi / 2, 11.4, "Suporte Técnico\n(peso 15%)", "right", "center"),
]
for ang, raio, texto, ha_align, va_align in rotulos_pos:
    ax.text(ang, raio, texto, ha=ha_align, va=va_align, fontsize=10.5, fontweight="bold", color="#222222")

ax.set_ylim(0, 10.5)
ax.set_rlabel_position(35)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(["2", "4", "6", "8", "10 pts"], fontsize=8.5, color="#444444")

fig.suptitle("Perfil Multidimensional dos Fornecedores (Notas Normalizadas 0 a 10)", fontsize=13.5, fontweight="bold", y=0.98)
ax.legend(loc="upper right", bbox_to_anchor=(1.32, 1.08), frameon=True, fontsize=10)
fig.text(0.5, 0.01, "Fonte: dados/fornecedores.csv | Quanto mais externa a linha, melhor o desempenho no critério (10 = melhor do grupo)", ha="center", fontsize=9, style="italic", color="#444444")
plt.tight_layout(rect=[0.04, 0.04, 0.94, 0.90])

caminho_grafico_4 = os.path.join(pasta_saida, "grafico_radar_fornecedores.png")
plt.savefig(caminho_grafico_4, dpi=180)
plt.close()

# ==============================================================================
# 6. Atualizar o relatorio em Markdown em resultados/fornecedores/relatorio_fornecedores.md
# ==============================================================================
caminho_relatorio = os.path.join(pasta_saida, "relatorio_fornecedores.md")

linhas_md = [
    "# Matriz de Decisão: Escolha do Melhor Fornecedor\n",
    "## 1. Contexto da Decisão e Alternativas",
    "- **Objetivo:** Selecionar o melhor fornecedor com base nos dados de `dados/fornecedores.csv` usando as skills `decision-matrix` e `chart-image`.",
    "- **Alternativas avaliadas:** Alfa, Beta, Gama e Delta.\n",
    "## 2. Dados Originais dos Fornecedores\n",
    "| Fornecedor | Preço Unitário (R$) | Prazo (dias) | Defeitos (%) | Nota de Suporte (0-10) |",
    "|---|---:|---:|---:|---:|",
]

for d in fornecedores:
    linhas_md.append(
        f"| {d['fornecedor']} | {d['preco_unitario']:.2f} | {d['prazo_dias']:.0f} | {d['defeitos_pct']:.1f}% | {d['suporte_nota']:.1f} |"
    )

linhas_md.extend([
    "\n### Comparação Visual dos Dados Originais",
    "![Métricas Originais dos Fornecedores](grafico_metricas_originais.png)\n",
    "## 3. Critérios, Pesos e Normalização (Escala 1 a 10)",
    "Seguindo a fórmula da skill `decision-matrix` para critérios objetivos:",
    "- **Menor é melhor** (`Preço`, `Prazo`, `Defeitos`): `Nota = 10 × (Melhor Valor / Valor do Fornecedor)`",
    "- **Maior é melhor** (`Suporte`): Valor já está na escala de 0 a 10.\n",
    "**Pesos definidos (Total = 100%):**",
    "- **Preço Unitário:** 30%",
    "- **Qualidade (Baixo % de Defeitos):** 30%",
    "- **Prazo de Entrega:** 25%",
    "- **Suporte:** 15%\n",
    "## 4. Resultado da Matriz de Decisão\n",
    "| Posição | Fornecedor | Preço (30%) | Qualidade (30%) | Prazo (25%) | Suporte (15%) | **Nota Final Ponderada** |",
    "|:---:|---|---:|---:|---:|---:|---:|",
])

for pos, d in enumerate(ranking, start=1):
    destaque = " **(Vencedor)**" if pos == 1 else ""
    linhas_md.append(
        f"| {pos}º | **{d['fornecedor']}**{destaque} | "
        f"{d['nota_preco']:.2f} ({d['pond_preco']:.2f}) | "
        f"{d['nota_qualidade']:.2f} ({d['pond_qualidade']:.2f}) | "
        f"{d['nota_prazo']:.2f} ({d['pond_prazo']:.2f}) | "
        f"{d['nota_suporte']:.2f} ({d['pond_suporte']:.2f}) | "
        f"**{d['nota_final']:.2f}** |"
    )

linhas_md.extend([
    "\n### Gráfico Principal: Ranking e Composição da Nota",
    "![Gráfico de Análise dos Fornecedores](grafico_fornecedores.png)\n",
    "### Perfil Multidimensional (Radar 0 a 10)",
    "![Gráfico de Radar dos Fornecedores](grafico_radar_fornecedores.png)\n",
    "## 5. Análise de Sensibilidade (Outros Cenários de Pesos)\n",
    "| Cenário | 1º Lugar | 2º Lugar | 3º Lugar | 4º Lugar |",
    "|---|---|---|---|---|",
])

for nome_cenario, lista_notas in resultados_cenarios.items():
    nome_limpo = nome_cenario.replace("\n", " ")
    colunas = [f"**{f}** ({n:.2f})" if i == 0 else f"{f} ({n:.2f})" for i, (f, n) in enumerate(lista_notas)]
    linhas_md.append(f"| {nome_limpo} | {colunas[0]} | {colunas[1]} | {colunas[2]} | {colunas[3]} |")

linhas_md.extend([
    "\n### Gráfico da Análise de Sensibilidade",
    "![Gráfico de Sensibilidade](grafico_sensibilidade.png)\n",
    "## 6. Recomendação Final e Trade-offs",
    f"- **Fornecedor Recomendado:** **{vencedor['fornecedor']}** (Nota Final: **{vencedor['nota_final']:.2f}** de 10).",
    f"- **Vantagem sobre o 2º colocado ({segundo['fornecedor']}):** +{vencedor['nota_final'] - segundo['nota_final']:.2f} pontos (+{margem_pct:.1f}%).",
    "- **Principais Pontos Fortes e Trade-offs:**",
    "  - **Delta:** Possui o menor prazo (4 dias), a menor taxa de defeitos (0.5%) e o melhor suporte (9.5), compensando com folga o preço unitário mais alto (R$ 110).",
    "  - **Beta:** Segundo colocado equilibrado, com bom prazo (5 dias), poucos defeitos (1%) e ótimo suporte (9.0).",
    "  - **Alfa e Gama:** Têm preços menores (R$ 90 e R$ 85), mas perdem muitos pontos pelo prazo de entrega maior (8 e 12 dias) e pela taxa de defeitos até 8 vezes maior que a do Delta.\n",
])

with open(caminho_relatorio, mode="w", encoding="utf-8") as f:
    f.write("\n".join(linhas_md))

print("Graficos gerados com sucesso:")
print(f"1. {caminho_grafico_1}")
print(f"2. {caminho_grafico_2}")
print(f"3. {caminho_grafico_3}")
print(f"4. {caminho_grafico_4}")
print(f"Relatorio atualizado em: {caminho_relatorio}")
