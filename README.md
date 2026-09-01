# 🧾 Recibo Fácil

**Sistema profissional de emissão e gerenciamento de recibos**

Desenvolvido com Streamlit, SQLite, ReportLab e Python puro - perfeito para aprender desenvolvimento full-stack.

---

## 📋 Características

✅ **Dashboard** com estatísticas em tempo real  
✅ **Criação de recibos** com validação completa  
✅ **Geração de PDF** profissional  
✅ **Histórico** com pesquisa e filtros  
✅ **Edição** de recibos já criados  
✅ **Exclusão** com confirmação de segurança  
✅ **Configurações** personalizáveis  
✅ **Banco de dados** SQLite persistente  
✅ **Testes automatizados** (21 testes)  
✅ **Interface responsiva** e profissional

---

## 🚀 Instalação Rápida

### 1. Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes)

### 2. Clonar ou copiar os arquivos

```bash
cd gerador-recibos
```

### 3. Criar ambiente virtual (opcional mas recomendado)

```bash
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Executar a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
gerador-recibos/
├── app.py                  # Aplicação principal (Streamlit)
├── database.py             # Camada de banco de dados SQLite
├── validacoes.py           # Validações de entrada
├── formatadores.py         # Formatação de dados (moeda, data, documento)
├── gerador_pdf.py          # Geração de PDF com ReportLab
├── test_sistema.py         # Testes automatizados (21 testes)
├── requirements.txt        # Dependências do projeto
├── recibos.db              # Banco de dados SQLite (criado automaticamente)
├── recibos_pdf/            # Pasta com PDFs gerados (criada automaticamente)
└── config.json             # Configurações da empresa (criado ao salvar)
```

---

## 🎯 Como Usar

### Painel (Dashboard)

- Visualize estatísticas: total de recibos, valor total recebido, recibos de hoje
- Acesso rápido para criar novo recibo ou ver histórico
- Mostra últimos 5 recibos criados

### Novo Recibo

1. Preencha dados do pagador (nome, CPF/CNPJ)
2. Preencha informações do pagamento (valor, data, descrição)
3. Selecione forma de pagamento
4. Preencha dados de quem recebeu
5. Clique "Gerar recibo"
6. Recibo é validado, PDF é gerado, dados são salvos
7. Você é levado à página de visualização

### Histórico

- Pesquise por número, nome ou valor
- Veja lista de todos os recibos
- Clique em "Ver" para ir aos detalhes

### Detalhes / Edição / Exclusão

- **Aba Visualização**: Veja o recibo e baixe PDF
- **Aba Editar**: Altere dados e regenere PDF
- **Aba Excluir**: Delete com confirmação

### Configurações

- Salve dados da sua empresa/pessoa
- Esses dados podem ser usados em futuras melhorias

---

## 🧪 Testes Automatizados

O projeto inclui **21 testes automatizados** cobrindo:

- ✅ Validação de CPF/CNPJ
- ✅ Validação de formulário completo
- ✅ Formatação de moeda, data, documento
- ✅ Geração de números sequenciais
- ✅ CRUD completo (criar, ler, buscar, atualizar, excluir)
- ✅ Geração de PDF
- ✅ Fluxo completo de criação

### Rodar os testes

```bash
python -m unittest test_sistema -v
```

Todos os testes devem passar (21 OK).

---

## 🗂️ Explicação dos Arquivos

### app.py

Arquivo principal da aplicação Streamlit. Contém:

- Sistema de navegação entre 6 páginas
- Gerenciamento de sessão
- Interface do usuário
- Integração com todos os módulos

**Páginas:**

1. **Painel**: Dashboard
2. **Novo Recibo**: Formulário
3. **Recibo Gerado**: Visualização pós-criação
4. **Histórico**: Lista e pesquisa
5. **Detalhes**: Ver/editar/excluir
6. **Configurações**: Personalização

### database.py

Camada de acesso aos dados SQLite. Funções:

- `conectar()`: Cria conexão com o banco
- `inicializar_banco()`: Cria tabela com migração automática
- `gerar_numero_recibo()`: Gera REC-000001, REC-000002, etc
- `salvar_recibo()`: Insere novo recibo
- `buscar_recibos()`: Pesquisa com LIKE
- `buscar_recibo_por_id()`: Busca específica
- `atualizar_recibo()`: Edita recibo existente
- `excluir_recibo()`: Deleta recibo
- `obter_estatisticas()`: Retorna métricas

### validacoes.py

Validações de entrada:

- `validar_documento()`: Verifica CPF (11 dig) ou CNPJ (14 dig)
- `validar_formulario()`: Valida todos os campos do recibo

### formatadores.py

Formata dados para apresentação:

- `formatar_moeda()`: 150.50 → "R$ 150,50"
- `formatar_documento()`: 12345678900 → "123.456.789-00"
- `formatar_data()`: Converte para "DD/MM/YYYY"
- `valor_por_extenso()`: 15.0 → "quinze reais"

### gerador_pdf.py

Cria PDFs profissionais com ReportLab:

- Desenha layout do recibo em A4
- Inclui número, data, valor, partes
- Salva em `recibos_pdf/REC-000001.pdf`

### test_sistema.py

Testes automatizados:

- **TestValidacoes**: 7 testes
- **TestFormatadores**: 6 testes
- **TestDatabase**: 6 testes
- **TestGeracaoPDF**: 1 teste
- **TestFluxoCompleto**: 1 teste completo

---

## 🔧 Estrutura do Banco de Dados

**Tabela: recibos**

| Campo               | Tipo       | Descrição           |
| ------------------- | ---------- | ------------------- |
| id                  | INTEGER PK | ID único            |
| numero_recibo       | TEXT       | REC-000001          |
| pagador_nome        | TEXT       | Nome de quem pagou  |
| pagador_documento   | TEXT       | CPF/CNPJ            |
| valor               | REAL       | Valor em reais      |
| data_pagamento      | TEXT       | DD/MM/YYYY          |
| descricao           | TEXT       | O que é o pagamento |
| forma_pagamento     | TEXT       | PIX, Dinheiro, etc  |
| recebedor_nome      | TEXT       | Quem recebeu        |
| recebedor_documento | TEXT       | CPF/CNPJ (opcional) |
| data_criacao        | TIMESTAMP  | Quando foi criado   |
| caminho_pdf         | TEXT       | Caminho do PDF      |

---

## 📚 Aprendizados

Este projeto é perfeito para aprender:

1. **Python Fundamentals**
   - Funções modulares
   - Tratamento de exceções
   - Estruturas de dados (dicts, lists)
   - String manipulation

2. **Banco de Dados**
   - SQLite
   - SQL básico (CREATE, INSERT, SELECT, UPDATE, DELETE)
   - Parameterização (SQL injection prevention)
   - row_factory para acesso por nome

3. **Streamlit**
   - Componentes (input, button, form)
   - Session state e navegação
   - Layout (columns, containers)
   - Download e upload

4. **PDF Generation**
   - ReportLab canvas
   - Posicionamento de elementos
   - Fontes e cores

5. **Testing**
   - unittest framework
   - Isolamento de dados em testes
   - Monkey patching
   - Test fixtures

6. **Design Patterns**
   - Separação de responsabilidades
   - MVC (Model-View-Controller)
   - Factory pattern (gerar números)

---

## 🐛 Troubleshooting

### "Módulo não encontrado"

```bash
pip install -r requirements.txt
```

### "Porta 8501 em uso"

```bash
streamlit run app.py --server.port 8502
```

### "Banco de dados corrompido"

Simplesmente delete `recibos.db` - será recriado automaticamente.

### "PDF não é gerado"

Verifique se existe pasta `recibos_pdf/` e se possui permissões de escrita.

---

## 📈 Próximas Funcionalidades (Ideias)

- [ ] Gráficos com Plotly/Matplotlib
- [ ] Filtros avançados por data/forma de pagamento
- [ ] Exportar em CSV
- [ ] Backup automático do banco
- [ ] Criptografia de dados sensíveis
- [ ] Multi-usuário com login
- [ ] Temas claro/escuro
- [ ] Impressão de lista de recibos

---

## 📄 Licença

Este projeto é de código aberto e pode ser usado livremente para aprendizado e portfólio.

---

## 👨‍💻 Desenvolvedor

Projeto criado para demonstrar habilidades em Python, Streamlit, SQLite e desenvolvimento full-stack.

**Últimas atualizações:**

- v1.0 (2026-08-31): Versão completa com 6 páginas, testes automatizados e funcionalidades CRUD
