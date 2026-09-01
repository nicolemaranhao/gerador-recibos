#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTES AUTOMATIZADOS DO GERADOR DE RECIBOS

Este arquivo contém testes para garantir que todas as funcionalidades
funcionam corretamente. Usamos unittest, que é padrão do Python.

Para rodar os testes:
    python -m pytest tests/test_sistema.py -v
    
Ou com unittest:
    python -m unittest tests.test_sistema -v
"""

import unittest
import os
import sqlite3
import tempfile
import shutil
from datetime import datetime

# Importa os módulos da aplicação
from database import (
    conectar, inicializar_banco, gerar_numero_recibo, 
    salvar_recibo, buscar_recibos, buscar_recibo_por_id, obter_estatisticas
)
from validacoes import validar_formulario, validar_documento
from formatadores import formatar_moeda, formatar_documento, formatar_data
from gerador_pdf import gerar_recibo_pdf


class TestValidacoes(unittest.TestCase):
    """Testes para o módulo de validações"""
    
    def test_validar_documento_cpf_valido(self):
        """CPF válido deve passar na validação"""
        resultado = validar_documento("12345678900")
        self.assertTrue(resultado)
    
    def test_validar_documento_cnpj_valido(self):
        """CNPJ válido deve passar na validação"""
        resultado = validar_documento("12345678000100")
        self.assertTrue(resultado)
    
    def test_validar_documento_invalido(self):
        """Documento com número de dígitos errado deve falhar"""
        resultado = validar_documento("123456789")
        self.assertFalse(resultado)
    
    def test_validar_documento_opcional_vazio(self):
        """Campo opcional vazio deve passar"""
        resultado = validar_documento("", opcional=True)
        self.assertTrue(resultado)
    
    def test_validar_formulario_completo_valido(self):
        """Formulário com todos os dados válidos deve passar"""
        dados = {
            "pagador_nome": "João Silva",
            "pagador_documento": "12345678900",
            "valor": 100.50,
            "descricao": "Prestação de serviços",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Maria Santos",
            "recebedor_documento": "98765432100"
        }
        tudo_certo, msg = validar_formulario(dados)
        self.assertTrue(tudo_certo, msg)
    
    def test_validar_formulario_sem_pagador_nome(self):
        """Formulário sem nome do pagador deve falhar"""
        dados = {
            "pagador_nome": "",
            "pagador_documento": "12345678900",
            "valor": 100.50,
            "descricao": "Teste",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Teste"
        }
        tudo_certo, msg = validar_formulario(dados)
        self.assertFalse(tudo_certo)
    
    def test_validar_formulario_valor_zero(self):
        """Formulário com valor zero deve falhar"""
        dados = {
            "pagador_nome": "João",
            "pagador_documento": "12345678900",
            "valor": 0,
            "descricao": "Teste",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Maria"
        }
        tudo_certo, msg = validar_formulario(dados)
        self.assertFalse(tudo_certo)


class TestFormatadores(unittest.TestCase):
    """Testes para o módulo de formatadores"""
    
    def test_formatar_moeda(self):
        """Moeda deve ser formatada corretamente"""
        resultado = formatar_moeda(150.50)
        self.assertEqual(resultado, "R$ 150,50")
    
    def test_formatar_moeda_zero(self):
        """Moeda zero deve retornar R$ 0,00"""
        resultado = formatar_moeda(0)
        self.assertEqual(resultado, "R$ 0,00")
    
    def test_formatar_documento_cpf(self):
        """CPF deve ser formatado corretamente"""
        resultado = formatar_documento("12345678900")
        self.assertEqual(resultado, "123.456.789-00")
    
    def test_formatar_documento_cnpj(self):
        """CNPJ deve ser formatado corretamente"""
        resultado = formatar_documento("12345678000100")
        self.assertEqual(resultado, "12.345.678/0001-00")
    
    def test_formatar_documento_vazio(self):
        """Documento vazio deve retornar string vazia"""
        resultado = formatar_documento("")
        self.assertEqual(resultado, "")
    
    def test_formatar_data(self):
        """Data deve ser formatada no padrão brasileiro"""
        data = datetime(2026, 8, 31)
        resultado = formatar_data(data)
        self.assertEqual(resultado, "31/08/2026")


class TestDatabase(unittest.TestCase):
    """Testes para o módulo de banco de dados"""
    
    def setUp(self):
        """Cria um banco de dados temporário para CADA teste"""
        # Salva o nome original do banco
        self.nome_banco_original = "recibos.db"
        
        # Cria um banco temporário único
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, f"test_{id(self)}.db")
        
        # Altera o nome do banco no módulo database
        import database
        database.NOME_BANCO = self.temp_db
        
        # Inicializa o banco
        inicializar_banco()
    
    def tearDown(self):
        """Remove o banco de dados temporário após cada teste"""
        import database
        database.NOME_BANCO = self.nome_banco_original
        
        # Remove pasta temporária
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_gerar_numero_recibo_primeiro(self):
        """Primeiro recibo deve ser REC-000001"""
        numero = gerar_numero_recibo()
        self.assertEqual(numero, "REC-000001")
    
    def test_gerar_numero_recibo_sequencial(self):
        """Números devem ser sequenciais"""
        # Cria primeiro recibo
        dados1 = {
            "numero_recibo": gerar_numero_recibo(),
            "pagador_nome": "Teste 1",
            "pagador_documento": "12345678900",
            "valor": 100.0,
            "data_pagamento": "31/08/2026",
            "descricao": "Teste",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Recebedor"
        }
        salvar_recibo(dados1)
        
        # Cria segundo recibo
        numero2 = gerar_numero_recibo()
        self.assertEqual(numero2, "REC-000002")
    
    def test_salvar_recibo(self):
        """Recibo deve ser salvo no banco"""
        dados = {
            "numero_recibo": "REC-000001",
            "pagador_nome": "João Silva",
            "pagador_documento": "12345678900",
            "valor": 150.50,
            "data_pagamento": "31/08/2026",
            "descricao": "Serviço de design",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Maria Santos",
            "recebedor_documento": "98765432100"
        }
        id_criado = salvar_recibo(dados)
        self.assertIsNotNone(id_criado)
        self.assertGreater(id_criado, 0)
    
    def test_buscar_recibo_por_id(self):
        """Deve encontrar recibo pelo ID"""
        # Salva recibo
        dados = {
            "numero_recibo": "REC-000001",
            "pagador_nome": "João",
            "pagador_documento": "12345678900",
            "valor": 100.0,
            "data_pagamento": "31/08/2026",
            "descricao": "Teste",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Maria"
        }
        id_criado = salvar_recibo(dados)
        
        # Busca pelo ID
        recibo = buscar_recibo_por_id(id_criado)
        self.assertIsNotNone(recibo)
        self.assertEqual(recibo["numero_recibo"], "REC-000001")
    
    def test_buscar_recibos_por_numero(self):
        """Deve pesquisar recibos por número"""
        # Salva dois recibos
        for i in range(2):
            dados = {
                "numero_recibo": f"REC-{i+1:06d}",
                "pagador_nome": f"Pagador {i+1}",
                "pagador_documento": "12345678900",
                "valor": 100.0 * (i+1),
                "data_pagamento": "31/08/2026",
                "descricao": f"Teste {i+1}",
                "forma_pagamento": "PIX",
                "recebedor_nome": "Maria"
            }
            salvar_recibo(dados)
        
        # Busca
        resultados = buscar_recibos("REC-000001")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["numero_recibo"], "REC-000001")
    
    def test_obter_estatisticas(self):
        """Deve calcular estatísticas do banco"""
        # Salva alguns recibos
        for i in range(3):
            dados = {
                "numero_recibo": f"REC-{i+1:06d}",
                "pagador_nome": f"Pagador {i+1}",
                "pagador_documento": "12345678900",
                "valor": 100.0 * (i+1),
                "data_pagamento": datetime.today().strftime("%d/%m/%Y"),
                "descricao": f"Teste {i+1}",
                "forma_pagamento": "PIX",
                "recebedor_nome": "Maria"
            }
            salvar_recibo(dados)
        
        # Obtém estatísticas
        stats = obter_estatisticas()
        self.assertEqual(stats["quantidade_total"], 3)
        self.assertGreater(stats["valor_total"], 0)
        self.assertGreater(stats["quantidade_hoje"], 0)


class TestGeracaoPDF(unittest.TestCase):
    """Testes para geração de PDF"""
    
    def setUp(self):
        """Limpa pasta de PDFs antes de cada teste"""
        self.pasta_pdf = "recibos_pdf"
        if os.path.exists(self.pasta_pdf):
            shutil.rmtree(self.pasta_pdf)
    
    def tearDown(self):
        """Limpa PDFs gerados nos testes"""
        if os.path.exists(self.pasta_pdf):
            shutil.rmtree(self.pasta_pdf)
    
    def test_gerar_pdf(self):
        """Deve gerar arquivo PDF real"""
        dados = {
            "numero_recibo": "REC-000001",
            "pagador_nome": "João Silva",
            "pagador_documento": "12345678900",
            "valor": 150.50,
            "data_pagamento": "31/08/2026",
            "descricao": "Serviço de design",
            "forma_pagamento": "PIX",
            "recebedor_nome": "Maria Santos",
            "recebedor_documento": ""
        }
        
        # Gera PDF
        caminho = gerar_recibo_pdf(dados)
        
        # Verifica se arquivo existe
        self.assertTrue(os.path.exists(caminho))
        
        # Verifica se tem tamanho > 0
        tamanho = os.path.getsize(caminho)
        self.assertGreater(tamanho, 0)
        
        # Verifica extensão
        self.assertTrue(caminho.endswith(".pdf"))


class TestFluxoCompleto(unittest.TestCase):
    """Testes de integração do fluxo completo"""
    
    def setUp(self):
        """Configura banco de dados temporário para CADA teste"""
        self.nome_banco_original = "recibos.db"
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, f"test_fluxo_{id(self)}.db")
        
        import database
        database.NOME_BANCO = self.temp_db
        
        # Inicializa o banco
        inicializar_banco()
    
    def tearDown(self):
        """Limpa banco temporário"""
        import database
        database.NOME_BANCO = self.nome_banco_original
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_fluxo_criar_recibo_completo(self):
        """
        Testa fluxo completo:
        1. Validar dados
        2. Gerar número
        3. Salvar no banco
        4. Gerar PDF
        5. Buscar recibo
        """
        # PASSO 1: Dados de entrada
        dados_entrada = {
            "pagador_nome": "João Silva",
            "pagador_documento": "12345678900",
            "valor": 250.75,
            "descricao": "Consultoria de sistemas",
            "forma_pagamento": "Transferência Bancária",
            "recebedor_nome": "Maria Santos",
            "recebedor_documento": "98765432100"
        }
        
        # PASSO 2: Validar
        tudo_certo, erro_msg = validar_formulario(dados_entrada)
        self.assertTrue(tudo_certo, f"Validação falhou: {erro_msg}")
        
        # PASSO 3: Gerar número
        numero = gerar_numero_recibo()
        self.assertIsNotNone(numero)
        
        # PASSO 4: Montar dados completos
        dados_completos = dados_entrada.copy()
        dados_completos["numero_recibo"] = numero
        dados_completos["data_pagamento"] = "31/08/2026"
        
        # PASSO 5: Salvar no banco
        id_salvo = salvar_recibo(dados_completos)
        self.assertIsNotNone(id_salvo)
        
        # PASSO 6: Gerar PDF
        caminho_pdf = gerar_recibo_pdf(dados_completos)
        self.assertTrue(os.path.exists(caminho_pdf))
        
        # PASSO 7: Buscar recibo
        recibo = buscar_recibo_por_id(id_salvo)
        self.assertIsNotNone(recibo)
        self.assertEqual(recibo["pagador_nome"], "João Silva")
        self.assertEqual(recibo["valor"], 250.75)


if __name__ == "__main__":
    # Executa os testes com output verboso
    unittest.main(verbosity=2)
