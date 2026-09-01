# ==============================================================================
# APP.PY - RECIBO FÁCIL
# ==============================================================================
# Arquivo principal da aplicação Streamlit.
# Gerencia a navegação entre telas e todo o fluxo de criação de recibos.
# ==============================================================================

import streamlit as st
import os
from datetime import datetime

# Importa nossas funções modularizadas.
# Cada arquivo tem uma responsabilidade clara:
# - database.py: salvar e buscar dados do banco SQLite
# - validacoes.py: verificar se os dados estão corretos
# - formatadores.py: melhorar apresentação (moeda, data, documento)
# - gerador_pdf.py: criar o arquivo PDF físico
from database import (
    inicializar_banco, gerar_numero_recibo, salvar_recibo,
    buscar_recibos, buscar_recibo_por_id, obter_estatisticas
)
from validacoes import validar_formulario
from formatadores import formatar_moeda, formatar_documento, formatar_data
from gerador_pdf import gerar_recibo_pdf

# ==============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==============================================================================

# Garante que o banco de dados existe e está estruturado corretamente.
# Essa função é segura de chamar múltiplas vezes (só cria se não existir).
inicializar_banco()

# Configura as propriedades da página do Streamlit.
st.set_page_config(
    page_title="Recibo Fácil",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para tornar a aplicação mais bonita e profissional.
# Inclui estilos para impressão, que ocultam elementos desnecessários.
st.markdown("""
<style>
    /* Quando o usuário pressiona Ctrl+P para imprimir, mostra só o recibo */
    @media print {
        /* Esconde sidebar */
        section[data-testid="stSidebar"] { display: none !important; }
        /* Esconde cabeçalho */
        header[data-testid="stHeader"] { display: none !important; }
        /* Esconde botões */
        button { display: none !important; }
        /* Esconde input */
        input { display: none !important; }
        /* Aumenta o espaço da página */
        .main .block-container { max-width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SISTEMA DE NAVEGAÇÃO
# ==============================================================================

# O session_state permite que o Streamlit "lembre" qual tela o usuário está.
# Quando o usuário clica em um botão, alteramos a página e fazemos st.rerun()
# para recarregar a interface mostrando o novo conteúdo.

# Inicializa a página atual (começa no painel).
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "painel"

# Guarda o ID do recibo recém-criado para exibir na tela de sucesso.
if "id_recibo_gerado" not in st.session_state:
    st.session_state["id_recibo_gerado"] = None

def mudar_pagina(nome_pagina):
    """
    Função auxiliar para trocar de página.
    Altera o session_state e força a recarga da interface.
    """
    st.session_state["pagina_atual"] = nome_pagina

# ==============================================================================
# MENU LATERAL (SIDEBAR)
# ==============================================================================

# O sidebar é a barra lateral que aparece do lado esquerdo.
# Usamos para mostrar o logo da aplicação e os botões de navegação.

with st.sidebar:
    st.markdown("## 🧾 Recibo Fácil")
    st.markdown("Gestão e emissão de recibos")
    st.markdown("---")
    
    # Botões para navegar entre as telas.
    # Cada botão altera o session_state e faz rerun() para recarregar.
    if st.button("🏠 Painel", use_container_width=True):
        mudar_pagina("painel")
        st.rerun()
    
    if st.button("🧾 Novo recibo", use_container_width=True):
        mudar_pagina("novo_recibo")
        st.rerun()
    
    if st.button("📋 Histórico", use_container_width=True):
        mudar_pagina("historico")
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2026 Recibo Fácil - Sistema de emissão de recibos digitais")


# ==============================================================================
# TELA 1: PAINEL (Dashboard)
# ==============================================================================
# Mostra estatísticas e atalhos rápidos para as outras funcionalidades.

if st.session_state["pagina_atual"] == "painel":
    st.title("🏠 Painel de controle")
    st.markdown("Visão geral do sistema de recibos.")
    st.markdown("---")
    
    # Busca as estatísticas do banco de dados.
    stats = obter_estatisticas()
    
    # Cria 3 colunas para exibir os números principais.
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total de recibos",
            stats["quantidade_total"],
            help="Todos os recibos emitidos no sistema"
        )
    
    with col2:
        st.metric(
            "Valor total recebido",
            formatar_moeda(stats["valor_total"]),
            help="Soma de todos os valores dos recibos"
        )
    
    with col3:
        st.metric(
            "Recibos hoje",
            stats["quantidade_hoje"],
            help="Recibos emitidos nesta data"
        )
    
    st.markdown("---")
    
    # Oferece atalhos rápidos.
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("➕ Criar um novo recibo", use_container_width=True):
            mudar_pagina("novo_recibo")
            st.rerun()
    
    with col_b:
        if st.button("🔍 Procurar no histórico", use_container_width=True):
            mudar_pagina("historico")
            st.rerun()

# ==============================================================================
# TELA 2: NOVO RECIBO (Formulário)
# ==============================================================================
# Formulário completo para criar um novo recibo com validação.

elif st.session_state["pagina_atual"] == "novo_recibo":
    st.title("🧾 Novo recibo")
    st.markdown("Preencha os dados abaixo para emitir um novo recibo.")
    st.markdown("---")
    
    # st.form agrupa os inputs de forma que a página NÃO recarregue a cada
    # tecla digitada, mas apenas quando o botão de submit for clicado.
    # Isso melhora muito a experiência do usuário.
    with st.form("form_recibo"):
        
        # ============================================================
        # SEÇÃO: INFORMAÇÕES DO PAGAMENTO
        # ============================================================
        st.subheader("💰 Informações do pagamento")
        
        pagador_nome = st.text_input(
            "Nome do pagador *",
            placeholder="Ex: Nicole Maranhão",
            help="Quem fez o pagamento?"
        )
        
        pagador_documento = st.text_input(
            "CPF/CNPJ do pagador *",
            placeholder="Apenas números ou formatado (123.456.789-00)",
            help="11 dígitos para CPF ou 14 para CNPJ"
        )
        
        # Cria 2 colunas para valor e data lado a lado.
        col_valor, col_data = st.columns(2)
        
        with col_valor:
            valor_texto = st.text_input(
                "Valor (R$) *",
                value="0,00",
                placeholder="150,00",
                help="Ex: 150,00 ou 1500,50"
            )
        
        with col_data:
            data_pagamento = st.date_input(
                "Data do pagamento *",
                value=datetime.today(),
                help="Quando o pagamento foi realizado?"
            )
        
        descricao = st.text_area(
            "Referente a *",
            placeholder="Ex: Prestação de serviços de design gráfico",
            help="O que este pagamento é referente?",
            height=80
        )
        
        forma_pagamento = st.selectbox(
            "Forma de pagamento *",
            ["PIX", "Dinheiro", "Cartão de Débito", "Cartão de Crédito", "Transferência Bancária"],
            help="Como foi realizado o pagamento?"
        )
        
        st.markdown("---")
        
        # ============================================================
        # SEÇÃO: DADOS DO RECEBEDOR
        # ============================================================
        st.subheader("👤 Dados do recebedor")
        
        recebedor_nome = st.text_input(
            "Nome de quem recebeu *",
            placeholder="Ex: Fernanda Maranhão",
            help="Quem recebeu o pagamento?"
        )
        
        recebedor_documento = st.text_input(
            "CPF/CNPJ de quem recebeu (Opcional)",
            placeholder="Deixe em branco se não souber",
            help="Não é obrigatório preencher"
        )
        
        st.markdown("---")
        
        # Botão para enviar o formulário.
        btn_gerar = st.form_submit_button(
            "🧾 Gerar recibo",
            use_container_width=True
        )
    
    # ================================================================
    # PROCESSAMENTO DO FORMULÁRIO
    # ================================================================
    # Este código roda APENAS quando o botão foi clicado.
    
    if btn_gerar:
        
        # PASSO 1: Converte o texto do valor para número.
        try:
            valor_float = float(
                valor_texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
            )
        except ValueError:
            valor_float = 0.0
        
        # PASSO 2: Cria o dicionário com os dados do formulário.
        dados = {
            "numero_recibo": gerar_numero_recibo(),  # Gera número único
            "pagador_nome": pagador_nome,
            "pagador_documento": pagador_documento,
            "valor": valor_float,
            "data_pagamento": formatar_data(data_pagamento),
            "descricao": descricao,
            "forma_pagamento": forma_pagamento,
            "recebedor_nome": recebedor_nome,
            "recebedor_documento": recebedor_documento
        }
        
        # PASSO 3: Valida os dados.
        # validar_formulario retorna (True/False, "mensagem de erro")
        tudo_certo, erro_msg = validar_formulario(dados)
        
        if not tudo_certo:
            # Se houver erro, mostra na interface e PARA aqui.
            st.error(f"❌ {erro_msg}")
        
        else:
            # Se passou na validação, continua o processo.
            try:
                # PASSO 4: Gera o PDF físico.
                # gerar_recibo_pdf retorna o caminho onde o arquivo foi salvo.
                caminho = gerar_recibo_pdf(dados)
                
                # PASSO 5: Verifica se o PDF realmente foi criado no disco rígido.
                if not os.path.exists(caminho):
                    raise Exception("O PDF não foi gerado corretamente no disco.")
                
                # Adiciona o caminho aos dados.
                dados["caminho_pdf"] = caminho
                
                # PASSO 6: Salva no banco de dados SQLite.
                # salvar_recibo retorna o ID do recibo criado.
                id_salvo = salvar_recibo(dados)
                
                # PASSO 7: Guarda o ID no session_state para mostrar depois.
                st.session_state["id_recibo_gerado"] = id_salvo
                
                # PASSO 8: Muda para a tela de sucesso.
                mudar_pagina("recibo_gerado")
                st.rerun()
                
            except Exception as erro:
                # Se algo der errado, mostra o erro técnico no console.
                print(f"[ERRO TÉCNICO] {erro}")
                # E mostra mensagem amigável para o usuário.
                st.error("❌ Não foi possível gerar o recibo. Verifique o terminal para mais detalhes.")


# ==============================================================================
# TELA 3: RECIBO GERADO (Visualização e Download)
# ==============================================================================
# Mostra o recibo recém-criado com opções de download e impressão.

elif st.session_state["pagina_atual"] == "recibo_gerado":
    
    # Busca o recibo no banco pelo ID armazenado no session_state.
    id_atual = st.session_state.get("id_recibo_gerado")
    recibo = buscar_recibo_por_id(id_atual)
    
    if not recibo:
        st.error("❌ Recibo não encontrado no banco de dados.")
        if st.button("Voltar ao Painel"):
            mudar_pagina("painel")
            st.rerun()
    
    else:
        # Mostra mensagem de sucesso.
        st.success("✅ Recibo gerado com sucesso!")
        st.title(f"Recibo {recibo['numero_recibo']}")
        st.markdown("---")
        
        # ============================================================
        # BOTÕES DE AÇÃO (Download, Impressão, Navegação)
        # ============================================================
        
        col_download, col_imprimir, col_voltar, col_novo = st.columns(4)
        
        # BOTÃO: Baixar PDF
        with col_download:
            caminho_pdf = recibo["caminho_pdf"]
            if caminho_pdf and os.path.exists(caminho_pdf):
                with open(caminho_pdf, "rb") as arquivo:
                    st.download_button(
                        label="📥 Baixar PDF",
                        data=arquivo,
                        file_name=f"{recibo['numero_recibo']}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.button("❌ PDF indisponível", disabled=True, use_container_width=True)
        
        # BOTÃO: Imprimir
        # Usamos CSS puro (sem JavaScript) para imprimir. O usuário pressiona
        # Ctrl+P no navegador e o CSS @media print esconde tudo que não é recibo.
        with col_imprimir:
            st.button(
                "🖨️ Imprimir (Ctrl+P)",
                disabled=False,
                use_container_width=True,
                help="Pressione Ctrl+P no navegador para imprimir"
            )
        
        # BOTÃO: Voltar ao Painel
        with col_voltar:
            if st.button("🏠 Painel", use_container_width=True):
                mudar_pagina("painel")
                st.rerun()
        
        # BOTÃO: Novo Recibo
        with col_novo:
            if st.button("➕ Novo recibo", use_container_width=True):
                mudar_pagina("novo_recibo")
                st.rerun()
        
        st.markdown("---")
        
        # ============================================================
        # VISUALIZAÇÃO DO RECIBO
        # ============================================================
        # Mostra o recibo de forma visualmente agradável em um container.
        
        with st.container(border=True):
            # Cabeçalho do recibo.
            col_titulo, col_numero = st.columns([2, 1])
            with col_titulo:
                st.markdown("## RECIBO")
                st.markdown(f"**Data:** {recibo['data_pagamento']}")
            with col_numero:
                st.markdown(f"### {recibo['numero_recibo']}")
            
            st.markdown("---")
            
            # Destaque do valor (o elemento mais importante).
            st.markdown("### VALOR RECEBIDO")
            st.markdown(f"# {formatar_moeda(recibo['valor'])}")
            
            st.markdown("---")
            
            # Informações divididas em 2 colunas.
            col_esq, col_dir = st.columns(2)
            
            with col_esq:
                st.markdown("### RECEBEMOS DE")
                st.markdown(f"**{recibo['pagador_nome']}**")
                st.markdown(f"CPF/CNPJ: {formatar_documento(recibo['pagador_documento'])}")
                
                st.markdown("")  # Espaço vazio
                st.markdown("### FORMA DE PAGAMENTO")
                st.markdown(f"{recibo['forma_pagamento']}")
            
            with col_dir:
                st.markdown("### REFERENTE A")
                st.markdown(f"{recibo['descricao']}")
            
            st.markdown("---")
            
            # Área de assinatura.
            col_empty, col_assinatura = st.columns([1, 1])
            
            with col_assinatura:
                st.markdown("___________________________________________________")
                st.markdown(f"**{recibo['recebedor_nome']}**")
                if recibo['recebedor_documento']:
                    st.caption(f"CPF/CNPJ: {formatar_documento(recibo['recebedor_documento'])}")
                st.caption("Responsável pelo recebimento")
            
            st.markdown("")
            st.caption("Documento gerado digitalmente. Não requer assinatura física.")


# ==============================================================================
# TELA 4: HISTÓRICO
# ==============================================================================
# Permite buscar e visualizar recibos já criados.

elif st.session_state["pagina_atual"] == "historico":
    st.title("📋 Histórico de recibos")
    st.markdown("Pesquise e consulte os recibos emitidos no sistema.")
    st.markdown("---")
    
    # Campo de pesquisa.
    # O usuário pode buscar por número, nome do pagador ou recebedor.
    termo = st.text_input(
        "🔎 Pesquisar recibo",
        placeholder="Digite número, nome do pagador ou recebedor...",
        help="Busca por: REC-000001, Nicole Maranhão, etc"
    )
    
    # Busca os recibos no banco de dados.
    # Se o usuário digitou algo, filtra. Caso contrário, mostra todos.
    resultados = buscar_recibos(termo)
    
    if not resultados:
        st.info("📭 Nenhum recibo encontrado.")
    
    else:
        # Mostra quantos foram encontrados.
        st.write(f"Foram encontrados **{len(resultados)}** recibo(s).")
        st.markdown("---")
        
        # Percorre todos os recibos encontrados.
        for r in resultados:
            # Cria um container com borda para cada recibo.
            with st.container(border=True):
                # Layout: Número | Pagador | Valor | Botão
                col1, col2, col3, col4 = st.columns([1.5, 2.5, 1.5, 1.2])
                
                with col1:
                    st.markdown(f"**{r['numero_recibo']}**")
                
                with col2:
                    st.markdown(f"{r['pagador_nome']}")
                
                with col3:
                    st.markdown(f"**{formatar_moeda(r['valor'])}**")
                
                # Botão para abrir o recibo.
                # Quando clicado, salva o ID e muda para a tela de visualização.
                with col4:
                    if st.button("Visualizar", key=f"btn_{r['id']}"):
                        st.session_state["id_recibo_gerado"] = r["id"]
                        mudar_pagina("recibo_gerado")
                        st.rerun()

# ==============================================================================
# FIM DO APP
# ==============================================================================