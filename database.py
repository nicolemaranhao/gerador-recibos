# ==============================================================================
# DATABASE.PY
# ==============================================================================
# Arquivo responsável pela comunicação com o banco de dados SQLite (recibos.db).
# Aqui definimos a estrutura correta (colunas) e isolamos o código SQL.
# ==============================================================================

import sqlite3
from datetime import datetime

# Nome do arquivo do banco
NOME_BANCO = "recibos.db"

def conectar():
    """
    Cria a conexão com o SQLite.
    row_factory permite buscar dados pelo nome da coluna em vez de posição.
    """
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao

def inicializar_banco():
    """
    Cria a tabela se não existir.
    Se o banco antigo tiver estrutura quebrada, ele recria a tabela
    para garantir que os nomes das colunas estejam 100% corretos.
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Define os campos que DEVEM existir na tabela
    campos_obrigatorios = {
        "pagador_nome", "pagador_documento", "data_pagamento",
        "forma_pagamento", "recebedor_nome", "recebedor_documento"
    }
    
    # Verifica as colunas do banco atual
    cursor.execute("PRAGMA table_info(recibos)")
    colunas_atuais = {coluna["name"] for coluna in cursor.fetchall()}
    
    # Se a tabela existir mas estiver com estrutura diferente (faltam campos),
    # apagamos para recriar de forma limpa.
    # Isso evita problemas com versões antigas do banco.
    precisa_migrar = colunas_atuais and not campos_obrigatorios.issubset(colunas_atuais)
    
    if precisa_migrar:
        # Se o banco antigo tem dados, poderia fazer uma migração complexa,
        # mas como no início é vazio, é mais seguro recriar.
        print("[DATABASE] Estrutura de banco incompatível. Recriando tabela...")
        cursor.execute("DROP TABLE IF EXISTS recibos")
        conexao.commit()
    
    # Estrutura definitiva do nosso projeto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recibos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_recibo TEXT,
            pagador_nome TEXT,
            pagador_documento TEXT,
            valor REAL,
            data_pagamento TEXT,
            descricao TEXT,
            forma_pagamento TEXT,
            recebedor_nome TEXT,
            recebedor_documento TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            caminho_pdf TEXT
        )
    """)
    conexao.commit()
    conexao.close()

def gerar_numero_recibo():
    """
    Conta os recibos existentes e gera o próximo número (ex: REC-000005).
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT COUNT(id) as total FROM recibos")
    resultado = cursor.fetchone()
    total = resultado["total"] if resultado["total"] else 0
    
    conexao.close()
    return f"REC-{(total + 1):06d}"

def salvar_recibo(dados):
    """
    Salva o novo recibo no banco. 
    Usa (?) que é o "SQL Parametrizado", mais seguro contra ataques.
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        INSERT INTO recibos (
            numero_recibo, pagador_nome, pagador_documento, valor,
            data_pagamento, descricao, forma_pagamento,
            recebedor_nome, recebedor_documento, caminho_pdf
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["numero_recibo"],
        dados["pagador_nome"],
        dados["pagador_documento"],
        dados["valor"],
        dados["data_pagamento"],
        dados["descricao"],
        dados["forma_pagamento"],
        dados["recebedor_nome"],
        dados.get("recebedor_documento", ""),
        dados.get("caminho_pdf", "")
    ))
    
    id_criado = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return id_criado

def buscar_recibos(termo_pesquisa=""):
    """
    Busca os recibos no histórico.
    Ordena do mais novo para o mais velho (ORDER BY id DESC).
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    if termo_pesquisa:
        termo = f"%{termo_pesquisa}%"
        cursor.execute("""
            SELECT * FROM recibos 
            WHERE numero_recibo LIKE ? 
               OR pagador_nome LIKE ? 
               OR recebedor_nome LIKE ?
            ORDER BY id DESC
        """, (termo, termo, termo))
    else:
        cursor.execute("SELECT * FROM recibos ORDER BY id DESC")
        
    lista = cursor.fetchall()
    conexao.close()
    return lista

def buscar_recibo_por_id(id_recibo):
    """
    Carrega apenas 1 recibo usando seu ID único.
    """
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM recibos WHERE id = ?", (id_recibo,))
    recibo = cursor.fetchone()
    conexao.close()
    return recibo

def obter_estatisticas():
    """
    Faz as contas para o Dashboard (soma de valores e contagem total).
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT COUNT(id) as total_qtd, SUM(valor) as total_valor FROM recibos")
    resultado = cursor.fetchone()
    qtd = resultado["total_qtd"] if resultado["total_qtd"] else 0
    soma = resultado["total_valor"] if resultado["total_valor"] else 0.0
    
    hoje = datetime.today().strftime("%d/%m/%Y")
    cursor.execute("SELECT COUNT(id) as hoje_qtd FROM recibos WHERE data_pagamento = ?", (hoje,))
    res_hoje = cursor.fetchone()
    qtd_hoje = res_hoje["hoje_qtd"] if res_hoje["hoje_qtd"] else 0
    
    conexao.close()
    
    return {
        "quantidade_total": qtd,
        "valor_total": soma,
        "quantidade_hoje": qtd_hoje
    }

def atualizar_recibo(id_recibo, dados):
    """
    Atualiza os dados de um recibo existente.
    Usa parameterização para evitar SQL injection.
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
        UPDATE recibos 
        SET pagador_nome = ?, pagador_documento = ?, valor = ?,
            data_pagamento = ?, descricao = ?, forma_pagamento = ?,
            recebedor_nome = ?, recebedor_documento = ?
        WHERE id = ?
    """, (
        dados["pagador_nome"],
        dados["pagador_documento"],
        dados["valor"],
        dados["data_pagamento"],
        dados["descricao"],
        dados["forma_pagamento"],
        dados["recebedor_nome"],
        dados.get("recebedor_documento", ""),
        id_recibo
    ))
    
    conexao.commit()
    conexao.close()

def excluir_recibo(id_recibo):
    """
    Deleta um recibo do banco de dados.
    """
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM recibos WHERE id = ?", (id_recibo,))
    
    conexao.commit()
    conexao.close()