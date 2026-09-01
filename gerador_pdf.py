# ==============================================================================
# GERADOR_PDF.PY
# ==============================================================================
# Usa a biblioteca ReportLab para "desenhar" o arquivo PDF.
# Cria fisicamente o arquivo em uma pasta chamada 'recibos_pdf'.
# ==============================================================================

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from formatadores import formatar_moeda, formatar_documento, valor_por_extenso

def gerar_recibo_pdf(dados):
    """
    Gera o PDF real no tamanho A4.
    Retorna o caminho exato onde o arquivo foi salvo.
    """
    # Cria a pasta caso não exista
    pasta = "recibos_pdf"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        
    # Monta o nome do arquivo, ex: recibos_pdf/REC-000001.pdf
    caminho_arquivo = os.path.join(pasta, f"{dados['numero_recibo']}.pdf")
    
    # Inicia a folha de desenho (canvas)
    c = canvas.Canvas(caminho_arquivo, pagesize=A4)
    largura_folha, altura_folha = A4
    margem_esq = 40
    margem_dir = largura_folha - 40
    
    # --- BORDA EXTERNA ---
    c.setLineWidth(1)
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.rect(margem_esq, altura_folha - 420, largura_folha - 80, 380)
    
    # --- CABEÇALHO ---
    y_atual = altura_folha - 70
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem_esq + 20, y_atual, "RECIBO FÁCIL")
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(margem_esq + 20, y_atual - 15, "Documento Oficial de Comprovação de Pagamento")
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_dir - 160, y_atual, f"NÚMERO: {dados['numero_recibo']}")
    c.setFont("Helvetica", 10)
    c.drawString(margem_dir - 160, y_atual - 15, f"Data: {dados['data_pagamento']}")
    
    c.setLineWidth(0.5)
    c.line(margem_esq, y_atual - 30, margem_dir, y_atual - 30)
    
    # --- INFORMAÇÕES DO VALOR ---
    y_atual -= 65
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margem_esq + 20, y_atual, "VALOR RECEBIDO")
    
    valor_texto = formatar_moeda(dados["valor"])
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margem_esq + 20, y_atual - 22, valor_texto)
    
    extenso = f"({valor_por_extenso(dados['valor']).capitalize()})"
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(margem_esq + 20, y_atual - 35, extenso)
    
    # --- DADOS DAS PARTES ---
    y_atual -= 80
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq + 20, y_atual, "RECEBEMOS DE:")
    c.setFont("Helvetica", 10)
    c.drawString(margem_esq + 130, y_atual, dados["pagador_nome"])
    
    doc_pagador = formatar_documento(dados["pagador_documento"])
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(margem_esq + 130, y_atual - 12, f"CPF/CNPJ: {doc_pagador}")
    
    y_atual -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq + 20, y_atual, "REFERENTE A:")
    c.setFont("Helvetica", 10)
    c.drawString(margem_esq + 130, y_atual, dados["descricao"])
    
    y_atual -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_esq + 20, y_atual, "FORMA DE PAGAMENTO:")
    c.setFont("Helvetica", 10)
    c.drawString(margem_esq + 160, y_atual, dados["forma_pagamento"])
    
    # --- ASSINATURA ---
    y_assinatura = altura_folha - 380
    c.setLineWidth(0.5)
    c.line(margem_dir - 250, y_assinatura + 15, margem_dir - 20, y_assinatura + 15)
    
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(margem_dir - 135, y_assinatura, dados["recebedor_nome"])
    
    doc_receb = formatar_documento(dados.get("recebedor_documento", ""))
    subtitulo = f"Responsável (CPF/CNPJ: {doc_receb})" if doc_receb else "Responsável pelo Recebimento"
    
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(margem_dir - 135, y_assinatura - 12, subtitulo)
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margem_esq, y_assinatura - 50, "Documento gerado digitalmente.")
    
    # Salva e finaliza o arquivo
    c.save()
    
    return caminho_arquivo