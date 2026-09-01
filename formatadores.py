# ==============================================================================
# FORMATADORES.PY
# ==============================================================================
# Este arquivo contém funções para melhorar a apresentação visual dos dados.
# Ele formata dinheiro, datas e documentos, e converte números para extenso.
# ==============================================================================

def formatar_moeda(valor):
    """
    Recebe um número e transforma no formato de dinheiro do Brasil.
    Exemplo: 50.0 -> "R$ 50,00"
    """
    try:
        # Formata com 2 casas decimais e ajusta vírgulas e pontos
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

def formatar_documento(doc):
    """
    Coloca a pontuação correta em CPF (11 dígitos) ou CNPJ (14 dígitos).
    Exemplo: 12345678900 -> "123.456.789-00"
    """
    if not doc:
        return ""
    
    # Extrai apenas os números, ignorando letras ou símbolos
    digitos = "".join(filter(str.isdigit, str(doc)))
    
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    elif len(digitos) == 14:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"
        
    return doc

def formatar_data(data_objeto):
    """
    Garante que a data fique no formato padrão brasileiro (Dia/Mês/Ano).
    """
    if not data_objeto:
        return ""
    # Se for um objeto de data do Python, formata para texto
    if hasattr(data_objeto, "strftime"):
        return data_objeto.strftime("%d/%m/%Y")
    return str(data_objeto)

def valor_por_extenso(valor):
    """
    Transforma um valor numérico na sua leitura por extenso.
    Exemplo: 15.0 -> "quinze reais"
    """
    try:
        v = float(valor)
    except (ValueError, TypeError):
        return "zero reais"

    if v == 0:
        return "zero reais"
        
    unidades = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
                "dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
    dezenas = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
    centenas = ["", "cem", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]

    inteiro = int(v)
    centavos = int(round((v - inteiro) * 100))
    
    partes = []
    
    if inteiro > 0:
        if inteiro == 1000:
            partes.append("um mil reais")
        else:
            milhares = inteiro // 1000
            resto_mil = inteiro % 1000
            
            if milhares > 0:
                if milhares == 1:
                    partes.append("mil")
                else:
                    partes.append(unidades[milhares] + " mil")
                    
            c = resto_mil // 100
            d = (resto_mil % 100) // 10
            u = resto_mil % 10
            
            sub_partes = []
            if c > 0:
                if c == 1 and (d > 0 or u > 0):
                    sub_partes.append("cento")
                else:
                    sub_partes.append(centenas[c])
            if d > 0:
                if d == 1:
                    sub_partes.append(unidades[10 + u])
                    u = 0
                else:
                    sub_partes.append(dezenas[d])
            if u > 0:
                sub_partes.append(unidades[u])
                
            if sub_partes:
                partes.append(" e ".join(sub_partes))
                
            if inteiro == 1:
                partes.append("real")
            else:
                partes.append("reais")

    if centavos > 0:
        c_str = f"{centavos} centavo{'s' if centavos > 1 else ''}"
        if inteiro > 0:
            partes.append(f"e {c_str}")
        else:
            partes.append(c_str)
            
    return " ".join(partes)