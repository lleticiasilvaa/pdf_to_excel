import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path

from extractor import extrair_produtos, FormatoPDFError

st.set_page_config(
    page_title="Extrator de Produtos",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF -> Excel")

st.write(
    "Faça o upload do PDF para gerar uma planilha Excel contendo "
    "Código Interno, EAN e Quantidade."
)

arquivo = st.file_uploader(
    "Selecione o PDF",
    type="pdf"
)

if arquivo is not None:

    if st.button("Processar PDF"):

        # with st.spinner("Extraindo produtos..."):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(arquivo.read())
            caminho_pdf = tmp.name

        barra = st.progress(0)
        status = st.empty()

        def atualizar_progresso(valor):
            barra.progress(valor)
            status.text(
                f"🔎 Extraindo produtos... {int(valor * 100)}%"
            )

        try:

            df = extrair_produtos(
                caminho_pdf,
                callback=atualizar_progresso
            )

        except FormatoPDFError as e:

            st.error(
                f"⚠️ Não foi possível extrair os produtos.\n\n"
                f"{e}"
            )

            st.info(
                "Certifique-se de enviar um PDF de pedido "
                "com a tabela de produtos no formato esperado."
            )

            st.stop()

        # st.success(f"✅ {len(df)} produtos encontrados.")
        
        excel = tempfile.NamedTemporaryFile(suffix=".xlsx")

        with pd.ExcelWriter(excel.name, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
            
        nome_excel = Path(arquivo.name).with_suffix(".xlsx").name

        with open(excel.name, "rb") as f:
            st.download_button(
                label= "📥 Baixar Excel",
                data=f,
                file_name=nome_excel,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        tab1, tab2 = st.tabs(["⬇️ Últimos produtos", "⬆️ Primeiros produtos"])

        with tab1:
            st.dataframe(
                df.tail(5),
                use_container_width=True,
                hide_index=True
            )

        with tab2:
            st.dataframe(
                df.head(5),
                use_container_width=True,
                hide_index=True
            )
        
        