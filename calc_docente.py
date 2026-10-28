
import streamlit as st
from decimal import Decimal, ROUND_HALF_UP

st.set_page_config(
    page_title="Desconto de Faltas Docentes",
    page_icon="🧮",
    layout="centered"
)


# -------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------

def D(valor):
    return Decimal(str(valor))


def arredondar(valor):
    return D(valor).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def moeda(valor):
    texto = f"{arredondar(valor):,.2f}"
    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    return f"R$ {texto}"


# -------------------------------
# TÍTULO
# -------------------------------

st.title("Calculadora de Desconto de Faltas Docentes")
st.write("Informe os dados do professor para calcular o desconto.")


# -------------------------------
# 1. DADOS SALARIAIS
# -------------------------------

st.header("1. Dados salariais")

salario_input = st.number_input(
    "Salário bruto (R$)",
    min_value=0.0,
    value=0.0,
    step=100.0,
    format="%.2f"
)

quantidade_ats = st.number_input(
    "Quantidade de ATS",
    min_value=0,
    value=0,
    step=1
)

salario = D(salario_input)

# DSR = salário x 0,16667
dsr = arredondar(salario * D("0.16667"))

# Cada ATS equivale a 5% sobre salário + DSR
percentual_ats = D(quantidade_ats) * D("0.05")

ats = arredondar(
    (salario + dsr) * percentual_ats
)

st.caption(f"DSR calculado: {moeda(dsr)}")
st.caption(
    f"Percentual de ATS: {percentual_ats * 100}%"
)
st.caption(f"Valor do ATS: {moeda(ats)}")


# -------------------------------
# 2. DADOS CONTRATUAIS
# -------------------------------

st.header("2. Dados contratuais")

creditos_semanais_input = st.number_input(
    "Quantidade de créditos semanais",
    min_value=0,
    value=0,
    step=1
)

horas_contratuais_input = st.number_input(
    "Horas contratuais semanais",
    min_value=0.0,
    value=0.0,
    step=1.0,
    format="%.2f"
)

semanas_input = st.selectbox(
    "Nº de semanas contratuais",
    options=[5.0, 4.5],
    format_func=lambda x: str(x).replace(".", ",")
)

creditos_semanais = D(creditos_semanais_input)
horas_contratuais = D(horas_contratuais_input)
semanas = D(semanas_input)


# -------------------------------
# 3. DADOS DA FALTA
# -------------------------------

st.header("3. Dados da falta")

creditos_falta_input = st.number_input(
    "Quantidade de créditos da falta",
    min_value=0.0,
    value=0.0,
    step=1.0,
    format="%.2f"
)

creditos_falta = D(creditos_falta_input)


# -------------------------------
# 4. CALCULAR DESCONTO
# -------------------------------

if st.button("Calcular desconto", type="primary"):

    # Passo A:
    # Créditos semanais x semanas contratuais
    A = creditos_semanais * semanas

    if salario <= 0:
        st.error("Informe um salário bruto maior que zero.")

    elif creditos_semanais <= 0 or semanas <= 0:
        st.error(
            "Créditos semanais e semanas contratuais "
            "devem ser maiores que zero."
        )

    elif horas_contratuais <= 0:
        st.error(
            "Informe as horas contratuais semanais."
        )

    else:
        # Passo B:
        # Horas contratuais x semanas / A
        B = (horas_contratuais * semanas) / A

        # Passo C:
        # Créditos de falta x B
        C = creditos_falta * B

        # Base salarial incluindo DSR e ATS
        base_salarial = salario + dsr + ats

        # Total de horas contratuais do período
        total_horas = horas_contratuais * semanas

        # Valor hora bruto
        valor_hora = base_salarial / total_horas

        # Desconto final: valor hora x C
        desconto = arredondar(valor_hora * C)

        # -------------------------------
        # 5. RESULTADO
        # -------------------------------

        st.divider()
        st.header("Resultado do cálculo")

        st.metric(
            "Desconto total da falta",
            moeda(desconto)
        )

        st.subheader("Composição salarial")

        st.write(f"**Salário bruto:** {moeda(salario)}")
        st.write(f"**DSR:** {moeda(dsr)}")
        st.write(f"**Quantidade de ATS:** {quantidade_ats}")
        st.write(f"**Valor do ATS:** {moeda(ats)}")
        st.write(f"**Base salarial total:** {moeda(base_salarial)}")

        st.subheader("Memória de cálculo")

        st.write(
            f"**Passo A:** {creditos_semanais} × "
            f"{semanas} = {A}"
        )

        st.write(
            f"**Passo B:** ({horas_contratuais} × "
            f"{semanas}) ÷ {A} = {B:.4f}"
        )

        st.write(
            f"**Passo C:** {creditos_falta} × "
            f"{B:.4f} = {C:.4f}"
        )

        st.write(
            f"**Total de horas contratuais:** "
            f"{horas_contratuais} × {semanas} "
            f"= {total_horas}"
        )

        st.write(
            f"**Valor hora bruto:** "
            f"{moeda(base_salarial)} ÷ {total_horas} "
            f"= {moeda(valor_hora)}"
        )

        st.success(
            f"Desconto final: {moeda(desconto)}"
        )

        st.caption(
            "Os valores de DSR e ATS são arredondados "
            "para centavos. O desconto final também é "
            "arredondado para duas casas decimais."
        )
