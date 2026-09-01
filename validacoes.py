# ==============================================================================
# VALIDACOES.PY
# ==============================================================================
# Concentra as regras para garantir que o usuário não digite dados inválidos.
# ==============================================================================

def validar_documento(doc, opcional=False):
    """
    Verifica se o CPF ou CNPJ digitado tem a quantidade certa de números.
    """
    if opcional and (not doc or not str(doc).strip()):
        return True
        
    # Extrai apenas os números da string
    digitos = "".join(filter(str.isdigit, str(doc)))
    
    # Valida o tamanho numérico (11 para CPF, 14 para CNPJ)
    if len(digitos) in [11, 14]:
        return True
    return False

def validar_formulario(dados):
    """
    Verifica todos os campos do recibo antes de salvar.
    Retorna (True, "") se tudo estiver certo, ou (False, "Mensagem") se der erro.
    """
    # Verifica o nome do pagador
    if not dados.get("pagador_nome") or str(dados["pagador_nome"]).strip() == "":
        return False, "O nome do pagador é obrigatório."
        
    # Verifica o documento do pagador
    if not dados.get("pagador_documento") or str(dados["pagador_documento"]).strip() == "":
        return False, "O CPF/CNPJ do pagador é obrigatório."
    if not validar_documento(dados["pagador_documento"]):
        return False, "O CPF/CNPJ do pagador é inválido. Digite 11 (CPF) ou 14 (CNPJ) números."
        
    # Verifica se o valor é maior que zero
    try:
        valor = float(dados.get("valor", 0))
        if valor <= 0:
            return False, "O valor do recibo deve ser maior que zero."
    except ValueError:
        return False, "O valor digitado não é um número válido."
        
    # Verifica a descrição
    if not dados.get("descricao") or str(dados["descricao"]).strip() == "":
        return False, "A descrição (Referente a) é obrigatória."
        
    # Verifica o nome do recebedor
    if not dados.get("recebedor_nome") or str(dados["recebedor_nome"]).strip() == "":
        return False, "O nome de quem recebeu é obrigatório."
        
    # Verifica o documento do recebedor (opcional)
    doc_recebedor = dados.get("recebedor_documento")
    if not validar_documento(doc_recebedor, opcional=True):
        return False, "O CPF/CNPJ de quem recebeu é inválido."
            
    return True, ""