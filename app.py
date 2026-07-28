import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import plotly.graph_objects as go

# 1. Configuração da página
st.set_page_config(page_title="Monitoramento Plantas Piloto", layout="wide")

# Injeção de CSS para mudar a cor do botão selecionado (Primary) para Laranja
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #F57C00;
        color: white;
        border-color: #F57C00;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FF9800;
        border-color: #FF9800;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
# ---------------------------------------------------------
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'

if 'iniciar_anomalia' not in st.session_state:
    st.session_state.iniciar_anomalia = 0

# Variáveis para controle do gráfico
if 'janela_grafico' not in st.session_state:
    st.session_state.janela_grafico = 120 # Padrão: 2 horas em minutos

# Substituído offset numérico por timestamp real para fixar o histórico corretamente
if 'fim_historico' not in st.session_state:
    st.session_state.fim_historico = None # None significa modo Online (tempo real)

def inicializar_dados():
    agora = datetime.datetime.now()
    tempos = pd.date_range(end=agora, periods=960, freq='min')
    dados = {
        'TE-30401-1A': np.random.normal(85, 0.5, 960),
        'TE-30401-1B': np.random.normal(84.5, 0.5, 960),
        'TE-30401-1C': np.random.normal(86, 0.5, 960),
        'TE-30401-1D': np.random.normal(85.5, 0.5, 960),
        'TE-30401-1E': np.random.normal(83.5, 0.5, 960),
        'TE-30401-1F': np.random.normal(84.5, 0.5, 960),
        'TE-30401-G':  np.random.normal(85, 0.5, 960),
        'EI-30401-1A': np.random.normal(10, 0.2, 960)
    }
    return pd.DataFrame(dados, index=tempos)

if 'df_simulado' not in st.session_state:
    st.session_state.df_simulado = inicializar_dados()

# 2. Barra Lateral Fixa
try:
    st.sidebar.image("https://logospng.org/download/braskem/logo-braskem-256.png", width=150)
except:
    pass

st.sidebar.markdown("### 📍 Plantas Piloto")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Menu Inicial"):
    st.session_state.pagina = 'inicio'

# ---------------------------------------------------------
# PÁGINA 1: MENU INICIAL 
# ---------------------------------------------------------
if st.session_state.pagina == 'inicio':
    st.title("Sistema de Monitoramento Industrial")
    
    st.markdown("""
        <div style='background-color: #2b2b2b; padding: 20px; border-radius: 8px; border-left: 5px solid #00BFFF; margin-bottom: 25px;'>
            <h3 style='margin: 0; color: #E0E0E0;'>Plantas Piloto</h3>
            <p style='color: #B0B0B0; margin-top: 10px;'>
                Selecione abaixo o painel de análise desejado para acessar os dados em tempo real.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Painéis Disponíveis")
    
    if st.button("📊 Monitoramento dos TE's de parede dos reatores", use_container_width=True):
        st.session_state.pagina = 'reatores'
        st.rerun()

# ---------------------------------------------------------
# PÁGINA 2: MONITORAMENTO
# ---------------------------------------------------------
elif st.session_state.pagina == 'reatores':
    
    col_titulo, col_voltar = st.columns([6, 1])
    with col_titulo:
        st.title("Monitoramento dos TE's de parede dos reatores")
    with col_voltar:
        if st.button("⬅️ Voltar"):
            st.session_state.pagina = 'inicio'
            st.rerun()

    with st.expander("Ver Diagrama Planificado R-30401", expanded=False):
        try:
            st.image("image_ee1f12.png", caption="Diagrama Planificado para Análise de Variáveis de Processo R-30401", use_container_width=True)
        except:
            st.info("Imagem do diagrama (image_ee1f12.png) não encontrada. Coloque-a na mesma pasta do código local.")

    # ---------------------------------------------------------
    # MOTOR DE SIMULAÇÃO "ONLINE" E ANOMALIAS
    # ---------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.header("Controle do Simulador")
    modo_online = st.sidebar.toggle("🟢 Ativar Monitoramento Ao Vivo", value=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Teste de Anomalias:**")
    if st.sidebar.button("⚠️ Simular Padrão de Folha"):
        st.session_state.iniciar_anomalia = 6 
        st.session_state.fim_historico = None # Volta para o online para capturar a anomalia
    
    if modo_online:
        ultimo_tempo = st.session_state.df_simulado.index[-1]
        novo_tempo = ultimo_tempo + pd.Timedelta(minutes=1)
        
        ultimo_valor = st.session_state.df_simulado.iloc[-1]
        novo_dado = ultimo_valor + np.random.normal(0, 0.3, len(ultimo_valor))
        
        if st.session_state.iniciar_anomalia > 0:
            ciclo = st.session_state.iniciar_anomalia
            if ciclo == 6: novo_dado['TE-30401-1B'] += 2.0
            if ciclo == 5: novo_dado['TE-30401-1B'] += 5.0
            if ciclo == 4: novo_dado['TE-30401-1B'] += 8.0 
            if ciclo == 3: novo_dado['TE-30401-1B'] -= 4.0
            if ciclo == 2: novo_dado['TE-30401-1B'] -= 3.0
            if ciclo == 1: novo_dado['TE-30401-1B'] -= 1.0
            st.session_state.iniciar_anomalia -= 1

        df_novo = pd.DataFrame([novo_dado.values], columns=novo_dado.index, index=[novo_tempo])
        st.session_state.df_simulado = pd.concat([st.session_state.df_simulado, df_novo]).tail(960) 

    df_atual = st.session_state.df_simulado

    # ---------------------------------------------------------
    # DETECÇÃO DO ALERTA DE "PADRÃO DE FOLHA"
    # ---------------------------------------------------------
    ultimos_5_1B = df_atual['TE-30401-1B'].tail(5)
    taxa_subida_1B = ultimos_5_1B.max() - ultimos_5_1B.min()
    padrao_folha_detectado = taxa_subida_1B > 6.0 

    if padrao_folha_detectado:
        st.error("🚨 **Alerta de padrão de folha!** Desvio térmico acentuado detectado na zona do reator.")
        try:
            st.image("image_ee1e53.png", width=400)
        except:
            st.warning("Imagem de referência (image_ee1e53.png) ausente. Coloque-a na mesma pasta do código local.")

    # ---------------------------------------------------------
    # PAINEL DE CONTROLE LATERAL
    # ---------------------------------------------------------
    st.sidebar.markdown("---")
    mostrar_media_movel = st.sidebar.checkbox("Exibir Média Móvel no Gráfico", value=True)
    janela_minutos = st.sidebar.selectbox("Média Móvel e Desvio (minutos):", [10, 30, 60, 120, 240, 300]) 

    st.sidebar.markdown("**Selecione as TAG's:**")
    cores_tags_padrao = {
        'TE-30401-1A': '#00BFFF', 'TE-30401-1B': '#1f77b4', 'TE-30401-1C': '#2ca02c',       
        'TE-30401-1D': '#ff7f0e', 'TE-30401-1E': '#9467bd', 'TE-30401-1F': '#e377c2',
        'TE-30401-G':  '#bcbd22', 'EI-30401-1A': '#d62728'
    }

    tags_selecionadas = []
    cores_escolhidas = {}

    for tag, cor_padrao in cores_tags_padrao.items():
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.checkbox(tag, value=(tag in ['TE-30401-1A', 'TE-30401-1B'])):
                tags_selecionadas.append(tag)
        with col2:
            cores_escolhidas[tag] = st.color_picker(f"Cor {tag}", cor_padrao, label_visibility="collapsed")

    df_media_movel = df_atual.rolling(window=janela_minutos).mean()

    # ---------------------------------------------------------
    # INDICADORES PRINCIPAIS E TABELA DE DADOS
    # ---------------------------------------------------------
    st.subheader("⚙️ Indicadores Operacionais e Estatísticas")
    
    tes_atuais = df_atual[[col for col in df_atual.columns if "TE-" in col]].iloc[-1]
    amplitude = tes_atuais.max() - tes_atuais.min()
    
    if amplitude > 8 or padrao_folha_detectado:
        st.error("⚠️ **Status da Parede: Comportamento Anômalo Detectado**")
    else:
        st.success("✅ **Status da Parede: Operação Normal**")

    # Tabela Dinâmica
    if tags_selecionadas:
        st.markdown("#### Detalhamento por TAG (Valores Instantâneos)")
        dados_tabela = []
        for tag in tags_selecionadas:
            val_atual = df_atual[tag].iloc[-1]
            val_mm = df_media_movel[tag].iloc[-1]
            desvio_padrao = df_atual[tag].tail(janela_minutos).std()
            
            val_5_atras = df_atual[tag].iloc[-6] if len(df_atual) >= 6 else df_atual[tag].iloc[0]
            taxa_var = (val_atual - val_5_atras) / 5.0
            
            desvio_max = abs(val_atual - val_mm)
            
            dados_tabela.append({
                "TAG": tag,
                "Valor Atual (°C)": f"{val_atual:.2f}",
                "Média Móvel (°C)": f"{val_mm:.2f}" if pd.notna(val_mm) else "-",
                "Desvio Padrão": f"{desvio_padrao:.2f}",
                "Taxa Var. (dT/dt)": f"{taxa_var:.2f}",
                "Desvio vs Média": f"{desvio_max:.2f}" if pd.notna(val_mm) else "-"
            })
            
        df_tabela = pd.DataFrame(dados_tabela)
        st.dataframe(df_tabela, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # GRÁFICO PRINCIPAL COM CONTROLE BASEADO EM TIMESTAMPS
    # ---------------------------------------------------------
    if len(tags_selecionadas) > 0:
        
        janela_minutos_grafico = st.session_state.janela_grafico
        
        # Filtragem baseada em tempo absoluto (timestamps)
        if st.session_state.fim_historico is None:
            # Modo Online: pega os últimos X minutos do dataframe
            df_plot = df_atual.tail(janela_minutos_grafico)
            df_plot_media = df_media_movel.tail(janela_minutos_grafico)
            st.markdown(f"#### 📈 Tendência de Temperatura (Online - Últimas {janela_minutos_grafico//60}h)")
        else:
            # Modo Histórico: corta entre (fim - janela) e fim
            t_fim = st.session_state.fim_historico
            t_inicio = t_fim - pd.Timedelta(minutes=janela_minutos_grafico)
            
            # Assegura que está dentro dos limites do df simulado
            if t_inicio < df_atual.index[0]:
                t_inicio = df_atual.index[0]
                t_fim = t_inicio + pd.Timedelta(minutes=janela_minutos_grafico)
                st.session_state.fim_historico = t_fim
                
            df_plot = df_atual.loc[t_inicio:t_fim]
            df_plot_media = df_media_movel.loc[t_inicio:t_fim]
            
            hora_inicio = df_plot.index[0].strftime('%d/%m %H:%M')
            hora_fim = df_plot.index[-1].strftime('%d/%m %H:%M')
            st.markdown(f"#### 🕰️ Tendência Histórica ({hora_inicio} até {hora_fim})")

        fig = go.Figure()

        for tag in tags_selecionadas:
            cor = cores_escolhidas[tag]
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot[tag], mode='lines', line=dict(color=cor, width=1.5), name=f"{tag} (Atual)"))
            
            if mostrar_media_movel:
                fig.add_trace(go.Scatter(x=df_plot_media.index, y=df_plot_media[tag], mode='lines', line=dict(color=cor, width=2.5, dash='dot'), name=f"{tag} (Média)"))

        fig.update_layout(
            height=450,
            hovermode="x unified",
            plot_bgcolor='#1E1E1E',         
            paper_bgcolor='rgba(0,0,0,0)',  
            font=dict(color='#E0E0E0'),     
            xaxis=dict(showgrid=True, gridcolor='#333333', title="Tempo"),
            yaxis=dict(showgrid=True, gridcolor='#333333', title="Temperatura (°C)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20),
            uirevision='constant' 
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # ---------------------------------------------------------
        # BOTÕES DE CONTROLE DE TEMPO E NAVEGAÇÃO (LINHAS SEPARADAS)
        # ---------------------------------------------------------
        
        # LINHA 1: Navegação Histórica (Voltar, Avançar, Online)
        st.markdown("**Navegação Histórica:**")
        n1, n2, n3 = st.columns(3)
        
        if n1.button("⬅️ Voltar", help=f"Retroceder exatamente {janela_minutos_grafico//60}h no tempo", use_container_width=True):
            if st.session_state.fim_historico is None:
                # Partindo do online, o novo fim histórico é o último ponto atual menos a janela
                st.session_state.fim_historico = df_atual.index[-1] - pd.Timedelta(minutes=janela_minutos_grafico)
            else:
                # Recua mais uma janela inteira com base no tempo atual de visualização
                st.session_state.fim_historico -= pd.Timedelta(minutes=janela_minutos_grafico)
            
            # Limite de segurança para não ultrapassar o início da base de dados
            if st.session_state.fim_historico < df_atual.index[0] + pd.Timedelta(minutes=janela_minutos_grafico):
                st.session_state.fim_historico = df_atual.index[0] + pd.Timedelta(minutes=janela_minutos_grafico)
            st.rerun()
            
        if n2.button("Avançar ➡️", help=f"Avançar exatamente {janela_minutos_grafico//60}h no tempo", use_container_width=True):
            if st.session_state.fim_historico is not None:
                st.session_state.fim_historico += pd.Timedelta(minutes=janela_minutos_grafico)
                # Se avançar e ultrapassar o momento atual, retorna automaticamente para o modo Online
                if st.session_state.fim_historico >= df_atual.index[-1]:
                    st.session_state.fim_historico = None
            st.rerun()
            
        if n3.button("⏭️ Online", help="Retornar para o tempo real", use_container_width=True):
            st.session_state.fim_historico = None
            st.rerun()

        st.markdown("---") 

        # LINHA 2: Escala de Tempo (2h, 4h, 8h, 16h com cor laranja se ativo)
        st.markdown("**Escala do Gráfico:**")
        e1, e2, e3, e4 = st.columns(4)
        
        if e1.button("2 Horas", use_container_width=True, type="primary" if janela_minutos_grafico == 120 else "secondary"): 
            st.session_state.janela_grafico = 120
            st.rerun()
        if e2.button("4 Horas", use_container_width=True, type="primary" if janela_minutos_grafico == 240 else "secondary"): 
            st.session_state.janela_grafico = 240
            st.rerun()
        if e3.button("8 Horas", use_container_width=True, type="primary" if janela_minutos_grafico == 480 else "secondary"): 
            st.session_state.janela_grafico = 480
            st.rerun()
        if e4.button("16 Horas", use_container_width=True, type="primary" if janela_minutos_grafico == 960 else "secondary"): 
            st.session_state.janela_grafico = 960
            st.rerun()

    else:
        st.warning("Selecione pelo menos uma TAG na barra lateral para visualizar os dados.")

    # Atualização da página a cada 30 segundos (somente se estiver no modo Online)
    if modo_online and st.session_state.fim_historico is None:
        time.sleep(30)
        st.rerun()
