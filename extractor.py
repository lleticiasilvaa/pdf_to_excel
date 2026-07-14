import pdfplumber
import pandas as pd

class FormatoPDFError(Exception):
    pass

def extrair_produtos(pdf_path, callback=None):
    dados = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            
            total_paginas = len(pdf.pages)
            
            if total_paginas == 0:
                raise FormatoPDFError(
                    "O PDF está vazio."
                )

            primeira_tabela = pdf.pages[0].extract_tables()[0]
            
            if not primeira_tabela:
                raise FormatoPDFError(
                    "Não foi encontrada nenhuma tabela no PDF."
                )
                    
            cabecalho = primeira_tabela[0]
            
            colunas_esperadas = [
                "Código interno",
                "Ean",
                "Quantidade",
                "Total"
            ]
            
            for coluna in colunas_esperadas:
                if coluna not in cabecalho:
                    raise FormatoPDFError(
                        f"O PDF não possui a coluna esperada: '{coluna}'."
                    )

            for i, page in enumerate(pdf.pages):

                tabela = page.extract_tables()[0]

                if i == 0:
                    linhas = tabela[1:]
                else:
                    linhas = tabela

                df = pd.DataFrame(linhas, columns=cabecalho)

                dados.append(
                    df[["Código interno", "Ean", "Quantidade", "Total"]]
                )
                
                # Atualiza progresso a cada página
                if callback:
                    callback((i + 1) / total_paginas)
        
        if not dados:
            raise FormatoPDFError(
                "Nenhum produto foi encontrado no PDF."
            )

        return pd.concat(dados, ignore_index=True)

    except FormatoPDFError:
            raise

    except Exception as e:
        raise FormatoPDFError(
            "Não foi possível processar o PDF. "
            "Verifique se ele está no formato correto."
        ) from e