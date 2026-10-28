import pandas as pd

# =============================
# CAMINHOS
# =============================
BASE_DOCENTE = r"C:\Users\306253\Desktop\testes\calc_docente\Wesley 1.xlsx"
FALTAS = r"C:\Users\306253\Desktop\testes\calc_docente\faltas_teste.xlsx"
SAIDA = r"C:\Users\306253\Desktop\testes\calc_docente\faltas_com_desconto.xlsx"

# =============================
# LEITURA (PRIMEIRA ABA)
# =============================
base = pd.read_excel(BASE_DOCENTE, sheet_name=0)
faltas = pd.read_excel(FALTAS, sheet_name=0)

# =============================
# NORMALIZAR CHAPA
# =============================
def normalizar_chapa(col):
    return (
        col.astype(str)
        .str.replace(".0", "", regex=False)
        .str.lstrip("0")
    )

base["Chapa"] = normalizar_chapa(base["Chapa"])
faltas["Chapa"] = normalizar_chapa(faltas["Chapa"])

# =============================
# IDENTIFICAR GRAD / POS
# =============================
def identificar_tipo(txt):
    if pd.isna(txt):
        return None
    txt = str(txt).strip().lower()
    if txt.startswith("curso"):
        return "GRAD"
    if txt.startswith("programa"):
        return "POS"
    return None

faltas["Tipo"] = faltas["Curso/Programa"].apply(identificar_tipo)

# =============================
# COLUNAS DE SAÍDA (MODELO ACCESS)
# =============================
faltas["VH_eDSR_eATS"] = ""
faltas["1"] = ""
faltas["2"] = ""
faltas["3"] = ""
faltas["Valor Desconto"] = ""

# =============================
# PROCESSAMENTO POR CHAPA + TIPO
# =============================
for (chapa, tipo), grupo in faltas.groupby(["Chapa", "Tipo"], dropna=False):

    if tipo not in ["GRAD", "POS"]:
        continue

    docente = base[base["Chapa"] == chapa]
    if docente.empty:
        continue

    d = docente.iloc[0]

    horas = d["HGrad"] if tipo == "GRAD" else d["HPos"]
    num_semanas = d["NumSemanas"]
    valor_hora = d["ValorHora"]

    if pd.isna(horas) or horas == 0:
        continue

    # =============================
    # SALÁRIO BASE
    # =============================
    horas_mes = horas * num_semanas
    salario = horas_mes * valor_hora

    # =============================
    # DSR
    # =============================
    dsr = salario * 0.16667

    # =============================
    # FTD / ATS
    # =============================
    ftd_pct = d["FTD"] if not pd.isna(d["FTD"]) else 0
    ats_pct = d["ATS"] if not pd.isna(d["ATS"]) else 0
    regime = d["Regime"]

    ftd = 0
    if regime == "FTD":
        ftd = (salario + dsr) * (ftd_pct / 100)

    base_ats = salario + dsr + ftd
    ats = base_ats * (ats_pct / 100)

    salario_total = salario + dsr + ftd + ats

    # =============================
    # VH eDSR eATS (IGUAL AO ACCESS)
    # =============================
    vh_edsr_ats = salario_total / horas_mes

    # =============================
    # COLUNA 1 (A)
    # =============================
    creditos_faltas = grupo["Credito"].sum()
    creditos_semanais = horas  # Access usa horas semanais aqui
    col_1 = creditos_semanais * num_semanas

    # =============================
    # COLUNA 2 (B)
    # =============================
    col_2 = horas_mes / col_1 if col_1 != 0 else 0

    # =============================
    # COLUNA 3 (C)
    # =============================
    col_3 = creditos_faltas * col_2

    # =============================
    # VALOR DESCONTO
    # =============================
    valor_desconto = vh_edsr_ats * col_3

    # =============================
    # ESCREVER SOMENTE NA PRIMEIRA LINHA
    # =============================
    idx = grupo.index[0]
    faltas.at[idx, "VH_eDSR_eATS"] = round(vh_edsr_ats, 2)
    faltas.at[idx, "1"] = round(col_1, 2)
    faltas.at[idx, "2"] = round(col_2, 2)
    faltas.at[idx, "3"] = round(col_3, 2)
    faltas.at[idx, "Valor Desconto"] = round(valor_desconto, 2)

# =============================
# LIMPEZA FINAL
# =============================
faltas = faltas.loc[:, ~faltas.columns.str.contains("^Unnamed")]

# =============================
# SALVAR
# =============================
faltas.to_excel(SAIDA, index=False)

print("✅ Arquivo gerado no modelo do Access:")
print(SAIDA)
