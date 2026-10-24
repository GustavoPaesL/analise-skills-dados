# Relatório de Qualidade e Tratamento dos Dados (`conferir-csv`)

## 1. Identificação do Arquivo e Finalidade
- **Arquivo original analisado:** `dados/fornecedores_erro.csv` (mantido intacto).
- **Arquivo tratado gerado:** `resultados/fornecedores/fornecedores_tratado.csv` (e `resultados/fornecedores_tratado.csv`).
- **Finalidade:** Avaliação e comparação de fornecedores (preço, prazo, taxa de defeitos e suporte) para tomada de decisão.
- **O que cada linha representa:** Um fornecedor avaliado (`Alfa`, `Beta`, `Gama`, `Delta`).

## 2. Estrutura do Arquivo
- **Separador utilizado:** Vírgula (`,`)
- **Total de linhas de dados:** 4 linhas (mais 1 linha de cabeçalho = 5 linhas no arquivo)
- **Total de colunas:** 5 colunas (`fornecedor, preco_unitario, prazo_dias, defeitos_pct, suporte_nota`)
- **Linhas duplicadas:** 0

## 3. Tipos e Ausências por Coluna (Antes do Tratamento)

| Coluna | Tipo Esperado | Tipo Encontrado nos Dados Preenchidos | Qtd. Ausentes | % Ausentes | Onde Ocorre (Linha do CSV / Fornecedor) |
|---|---|---|---:|---:|---|
| `fornecedor` | Texto (identificador) | texto (str) | 0 | 0.0% | Nenhuma ausência |
| `preco_unitario` | Numérico > 0 (moeda) | numero (int/float) | 1 | 25.0% | Linha 5 (Delta) |
| `prazo_dias` | Numérico inteiro > 0 (dias) | numero (int/float) | 0 | 0.0% | Nenhuma ausência |
| `defeitos_pct` | Numérico 0 a 100 (%) | numero (int/float), numero decimal (float) | 0 | 0.0% | Nenhuma ausência |
| `suporte_nota` | Numérico 0 a 10 (nota) | numero (int/float), numero decimal (float) | 1 | 25.0% | Linha 3 (Beta) |

## 4. Problemas Encontrados e Evidências (Números)
1. **Valores ausentes (campos vazios):** Foram encontrados **2 valores ausentes** em **2 das 4 linhas (50,0% dos fornecedores)**:
   - **Linha 3 (Fornecedor `Beta`):** Coluna `suporte_nota` vazia (`Beta,100,5,1,`).
   - **Linha 5 (Fornecedor `Delta`):** Coluna `preco_unitario` vazia (`Delta,,4,0.5,9.5`).
2. **Números guardados como texto inválido:** 0 ocorrências.
3. **Valores fora de sentido / fora de faixa:** 0 ocorrências.
4. **Linhas duplicadas:** 0 ocorrências.

## 5. Regra de Preenchimento Aplicada (Imputação pela Mediana)
Seguindo a regra 6 da skill `conferir-csv`, o arquivo original não foi alterado e os valores faltantes foram preenchidos em um novo arquivo usando a **mediana** dos valores válidos de cada coluna:

| Linha | Fornecedor | Coluna Preenchida | Valores Válidos na Coluna | Mediana Aplicada | Média (Referência) |
|:---:|---|---|---|---:|---:|
| 3 | **Beta** | `suporte_nota` | `[6.0, 8.0, 9.5]` | **8** | 7.83 |
| 5 | **Delta** | `preco_unitario` | `[85.0, 90.0, 100.0]` | **90** | 91.67 |

## 6. Base Final Tratada (`fornecedores_tratado.csv`)

| fornecedor | preco_unitario | prazo_dias | defeitos_pct | suporte_nota | Status |
|---|---:|---:|---:|---:|---|
| Alfa | 90 | 8 | 2 | 8 | Original completo |
| Beta | 100 | 5 | 1 | 8 | Preenchido pela mediana |
| Gama | 85 | 12 | 4 | 6 | Original completo |
| Delta | 90 | 4 | 0.5 | 9.5 | Preenchido pela mediana |