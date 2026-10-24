import csv
import os
import statistics

caminho_csv = os.path.join("dados", "fornecedores_erro.csv")

with open(caminho_csv, mode="r", encoding="utf-8") as f:
    leitor = csv.reader(f, delimiter=",")
    cabecalho = next(leitor)
    linhas = list(leitor)

num_linhas = len(linhas)
num_colunas = len(cabecalho)

# Contagem de linhas duplicadas
linhas_tuplas = [tuple(l) for l in linhas]
num_duplicadas = num_linhas - len(set(linhas_tuplas))

# Verificar valores ausentes (vazios ou apenas espacos), tipos e validade
ausentes_por_coluna = {col: [] for col in cabecalho}
tipos_detectados = {col: set() for col in cabecalho}
valores_validos_por_coluna = {col: [] for col in cabecalho if col != "fornecedor"}
valores_invalidos = []
numeros_como_texto = []

for idx_linha, linha in enumerate(linhas, start=2):  # linha 1 e o cabecalho
    fornecedor_id = linha[0].strip() if len(linha) > 0 and linha[0].strip() else f"Linha {idx_linha}"
    for idx_col, col in enumerate(cabecalho):
        valor_bruto = linha[idx_col] if idx_col < len(linha) else ""
        valor = valor_bruto.strip()

        # Passo 4 da skill: textos vazios ou so com espacos contam como ausencia
        if valor == "":
            ausentes_por_coluna[col].append((idx_linha, fornecedor_id))
            continue

        if col == "fornecedor":
            tipos_detectados[col].add("texto (str)")
        else:
            try:
                num = float(valor)
                valores_validos_por_coluna[col].append(num)
                if num.is_integer():
                    tipos_detectados[col].add("numero (int/float)")
                else:
                    tipos_detectados[col].add("numero decimal (float)")

                # Passo 5 da skill: checar valores que nao fazem sentido para a coluna
                if col == "preco_unitario" and num <= 0:
                    valores_invalidos.append((idx_linha, fornecedor_id, col, valor, "Preco menor ou igual a zero"))
                elif col == "prazo_dias" and num <= 0:
                    valores_invalidos.append((idx_linha, fornecedor_id, col, valor, "Prazo menor ou igual a zero"))
                elif col == "defeitos_pct" and (num < 0 or num > 100):
                    valores_invalidos.append((idx_linha, fornecedor_id, col, valor, "Porcentagem fora de 0 a 100%"))
                elif col == "suporte_nota" and (num < 0 or num > 10):
                    valores_invalidos.append((idx_linha, fornecedor_id, col, valor, "Nota fora da escala 0 a 10"))
            except ValueError:
                tipos_detectados[col].add("texto invalido em coluna numerica")
                numeros_como_texto.append((idx_linha, fornecedor_id, col, valor))

total_ausentes = sum(len(v) for v in ausentes_por_coluna.values())
linhas_com_ausencia = set()
for col, ocorrencias in ausentes_por_coluna.items():
    for idx_l, _ in ocorrencias:
        linhas_com_ausencia.add(idx_l)

# Calcular a mediana de cada coluna numerica para preencher valores faltantes
medianas_colunas = {}
medias_colunas = {}
for col, vals in valores_validos_por_coluna.items():
    if vals:
        medianas_colunas[col] = statistics.median(vals)
        medias_colunas[col] = statistics.mean(vals)

# Criar uma copia das linhas e preencher os valores ausentes com a mediana da coluna
linhas_tratadas = []
preenchimentos_realizados = []

for idx_linha, linha in enumerate(linhas, start=2):
    nova_linha = []
    fornecedor_id = linha[0].strip()
    for idx_col, col in enumerate(cabecalho):
        valor_bruto = linha[idx_col] if idx_col < len(linha) else ""
        valor = valor_bruto.strip()
        if valor == "" and col in medianas_colunas:
            val_mediana = medianas_colunas[col]
            # Formatar como inteiro se for exato, ou decimal caso contrario
            valor_preenchido = f"{int(val_mediana)}" if val_mediana.is_integer() else f"{val_mediana:.1f}"
            nova_linha.append(valor_preenchido)
            preenchimentos_realizados.append({
                "linha": idx_linha,
                "fornecedor": fornecedor_id,
                "coluna": col,
                "valores_base": sorted(valores_validos_por_coluna[col]),
                "mediana_aplicada": valor_preenchido,
                "media_referencia": f"{medias_colunas[col]:.2f}",
            })
        else:
            nova_linha.append(valor)
    linhas_tratadas.append(nova_linha)

# Salvar o CSV tratado em resultados/ (sem tocar em dados/fornecedores_erro.csv)
os.makedirs(os.path.join("resultados", "fornecedores"), exist_ok=True)
caminho_csv_tratado_raiz = os.path.join("resultados", "fornecedores_tratado.csv")
caminho_csv_tratado_forn = os.path.join("resultados", "fornecedores", "fornecedores_tratado.csv")

for caminho_destino in [caminho_csv_tratado_raiz, caminho_csv_tratado_forn]:
    with open(caminho_destino, mode="w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, delimiter=",")
        escritor.writerow(cabecalho)
        escritor.writerows(linhas_tratadas)

# Gerar resultados/qualidade.md conforme passo 8 da skill conferir-csv
caminho_saida = os.path.join("resultados", "qualidade.md")
caminho_saida_forn = os.path.join("resultados", "fornecedores", "qualidade.md")

relatorio = [
    "# Relatório de Qualidade e Tratamento dos Dados (`conferir-csv`)\n",
    "## 1. Identificação do Arquivo e Finalidade",
    "- **Arquivo original analisado:** `dados/fornecedores_erro.csv` (mantido intacto).",
    "- **Arquivo tratado gerado:** `resultados/fornecedores/fornecedores_tratado.csv` (e `resultados/fornecedores_tratado.csv`).",
    "- **Finalidade:** Avaliação e comparação de fornecedores (preço, prazo, taxa de defeitos e suporte) para tomada de decisão.",
    "- **O que cada linha representa:** Um fornecedor avaliado (`Alfa`, `Beta`, `Gama`, `Delta`).\n",
    "## 2. Estrutura do Arquivo",
    "- **Separador utilizado:** Vírgula (`,`)",
    f"- **Total de linhas de dados:** {num_linhas} linhas (mais 1 linha de cabeçalho = {num_linhas + 1} linhas no arquivo)",
    f"- **Total de colunas:** {num_colunas} colunas (`{', '.join(cabecalho)}`)",
    f"- **Linhas duplicadas:** {num_duplicadas}\n",
    "## 3. Tipos e Ausências por Coluna (Antes do Tratamento)\n",
    "| Coluna | Tipo Esperado | Tipo Encontrado nos Dados Preenchidos | Qtd. Ausentes | % Ausentes | Onde Ocorre (Linha do CSV / Fornecedor) |",
    "|---|---|---|---:|---:|---|",
]

tipos_esperados = {
    "fornecedor": "Texto (identificador)",
    "preco_unitario": "Numérico > 0 (moeda)",
    "prazo_dias": "Numérico inteiro > 0 (dias)",
    "defeitos_pct": "Numérico 0 a 100 (%)",
    "suporte_nota": "Numérico 0 a 10 (nota)",
}

for col in cabecalho:
    qtd_aus = len(ausentes_por_coluna[col])
    pct_aus = (qtd_aus / num_linhas) * 100 if num_linhas > 0 else 0.0
    onde = ", ".join([f"Linha {l} ({f})" for l, f in ausentes_por_coluna[col]]) if qtd_aus > 0 else "Nenhuma ausência"
    tipos_str = ", ".join(sorted(tipos_detectados[col])) if tipos_detectados[col] else "Sem valores"
    relatorio.append(
        f"| `{col}` | {tipos_esperados[col]} | {tipos_str} | {qtd_aus} | {pct_aus:.1f}% | {onde} |"
    )

relatorio.extend([
    "\n## 4. Problemas Encontrados e Evidências (Números)",
    f"1. **Valores ausentes (campos vazios):** Foram encontrados **{total_ausentes} valores ausentes** em **{len(linhas_com_ausencia)} das {num_linhas} linhas (50,0% dos fornecedores)**:",
    "   - **Linha 3 (Fornecedor `Beta`):** Coluna `suporte_nota` vazia (`Beta,100,5,1,`).",
    "   - **Linha 5 (Fornecedor `Delta`):** Coluna `preco_unitario` vazia (`Delta,,4,0.5,9.5`).",
    f"2. **Números guardados como texto inválido:** {len(numeros_como_texto)} ocorrências.",
    f"3. **Valores fora de sentido / fora de faixa:** {len(valores_invalidos)} ocorrências.",
    f"4. **Linhas duplicadas:** {num_duplicadas} ocorrências.\n",
    "## 5. Regra de Preenchimento Aplicada (Imputação pela Mediana)",
    "Seguindo a regra 6 da skill `conferir-csv`, o arquivo original não foi alterado e os valores faltantes foram preenchidos em um novo arquivo usando a **mediana** dos valores válidos de cada coluna:\n",
    "| Linha | Fornecedor | Coluna Preenchida | Valores Válidos na Coluna | Mediana Aplicada | Média (Referência) |",
    "|:---:|---|---|---|---:|---:|",
])

for p in preenchimentos_realizados:
    relatorio.append(
        f"| {p['linha']} | **{p['fornecedor']}** | `{p['coluna']}` | `{p['valores_base']}` | **{p['mediana_aplicada']}** | {p['media_referencia']} |"
    )

relatorio.extend([
    "\n## 6. Base Final Tratada (`fornecedores_tratado.csv`)\n",
    "| fornecedor | preco_unitario | prazo_dias | defeitos_pct | suporte_nota | Status |",
    "|---|---:|---:|---:|---:|---|",
])

for idx_l, (linha_orig, linha_trat) in enumerate(zip(linhas, linhas_tratadas), start=2):
    teve_ajuste = linha_orig != linha_trat
    status = "Preenchido pela mediana" if teve_ajuste else "Original completo"
    relatorio.append(
        f"| {linha_trat[0]} | {linha_trat[1]} | {linha_trat[2]} | {linha_trat[3]} | {linha_trat[4]} | {status} |"
    )

with open(caminho_saida, mode="w", encoding="utf-8") as f:
    f.write("\n".join(relatorio))

with open(caminho_saida_forn, mode="w", encoding="utf-8") as f:
    f.write("\n".join(relatorio))

print("Preenchimentos realizados com sucesso:")
for p in preenchimentos_realizados:
    print(f" - Linha {p['linha']} ({p['fornecedor']}) | Coluna '{p['coluna']}': preenchido com mediana = {p['mediana_aplicada']} (valores base: {p['valores_base']})")
print(f"Arquivo CSV tratado salvo em: {caminho_csv_tratado_forn}")
print(f"Relatorio atualizado em: {caminho_saida}")
