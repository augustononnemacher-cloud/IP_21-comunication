import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

# 1. Configuração da página
st.set_page_config(page_title="Monitoramento Plantas Piloto", layout="wide")

# Inicializa o controle de páginas no estado da sessão
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'

# 2. Barra Lateral Fixa - Logo e Identificação da Área
try:
    st.sidebar.image("https://logospng.org/download/braskem/logo-braskem-256.png", width=150)
except:
    pass

st.sidebar.markdown("### 📍 Plantas Piloto")
st.sidebar.markdown("---")

# Botão global na barra lateral para voltar ao início rapidamente
if st.sidebar.button("🏠 Menu Inicial"):
    st.session_state.pagina = 'inicio'

# ---------------------------------------------------------
# PÁGINA 1: MENU INICIAL (HUB DE NAVEGAÇÃO)
# ---------------------------------------------------------
if st.session_state.pagina == 'inicio':
    st.title("Sistema de Monitoramento Industrial")
    
    st.markdown("""
        <div style='background-color: #2b2b2b; padding: 20px; border-radius: 8px; border-left: 5px solid #00BFFF; margin-bottom: 25px;'>
            <h3 style='margin: 0; color: #E0E0E0;'>Área: Plantas Piloto</h3>
            <p style='color: #B0B0B0; margin-top: 10px;'>
                Selecione abaixo o painel de análise desejado para acessar os dados em tempo real, manômetros e médias móveis.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Painéis Disponíveis")
    
    if st.button("📊 Monitoramento dos TE's de parede dos reatores", use_container_width=True):
        st.session_state.pagina = 'reatores'

# ---------------------------------------------------------
# PÁGINA 2: MONITORAMENTO DOS TE'S DE PAREDE DOS REATORES
# ---------------------------------------------------------
elif st.session_state.pagina == 'reatores':
    
    # Cabeçalho da página com botão de retorno
    col_titulo, col_voltar = st.columns([6, 1])
    with col_titulo:
        st.title("Monitoramento dos TE's de parede dos reatores")
    with col_voltar:
        if st.button("⬅️ Voltar"):
            st.session_state.pagina = 'inicio'

    # Gerando Dados Simulados com as Tags Reais (480 minutos = 8 horas)
    @st.cache_data
    def gerar_dados_simulados():
        agora = datetime.datetime.now()
        tempos = pd.date_range(end=agora, periods=480, freq='min') 
        
        dados = {
            'TE-30401-1A': np.random.normal(85, 1.5, 480),
            'TE-30401-1B': np.random.normal(84, 1.2, 480),
            'TE-30401-1C': np.random.normal(86, 1.8, 480),
            'TE-30401-1D': np.random.normal(85.5, 1.3, 480),
            'TE-30401-1E': np.random.normal(83, 1.4, 480),
            'TE-30401-1F': np.random.normal(84.5, 1.1, 480),
            'TE-30401-G':  np.random.normal(85, 1.6, 480),
            'EI-30401-1A': np.random.normal(10, 0.8, 480),
            'PIC-30401':   np.random.normal(12, 0.5, 480),
            'LI-30401':    np.random.normal(50, 2, 480),
            'TIC-30401':   np.random.normal(85, 1, 480)
        }
        df = pd.DataFrame(dados, index=tempos)
        return df

    df_simulado = gerar_dados_simulados()

    st.sidebar.markdown("---")
    st.sidebar.header("Painel de Controle")

    # Botão Liga/Desliga para a Média Móvel
    mostrar_media_movel = st.sidebar.checkbox("Exibir linhas de Média Móvel", value=True)

    # Opções de tempo de média móvel
    if mostrar_media_movel:
        opcoes_janela = [5, 10, 30, 60, 120, 240]
        janela_minutos = st.sidebar.selectbox("Média Móvel (minutos):", opcoes_janela)
    else:
        janela_minutos = 15 

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Selecione as TAG's:**")

    # Cores sugeridas para as novas tags de temperatura e instrumentação
    cores_tags_padrao = {
        'TE-30401-1A': '#00BFFF',       
        'TE-30401-1B': '#1f77b4',  
        'TE-30401-1C': '#2ca02c',       
        'TE-30401-1D': '#ff7f0e',       
        'TE-30401-1E': '#9467bd',
        'TE-30401-1F': '#e377c2',
        'TE-30401-G':  '#bcbd22',
        'EI-30401-1A': '#d62728'
    }

    tags_selecionadas = []
    cores_escolhidas = {}

    for tag, cor_padrao in cores_tags_padrao.items():
        col1, col2 = st.sidebar.columns([4, 1])
        
        with col1:
            # Deixa as duas primeiras tês marcadas por padrão
            marcado_por_padrao = True if tag in ['TE-30401-1A', 'TE-30401-1B'] else False
            if st.checkbox(tag, value=marcado_por_padrao):
                tags_selecionadas.append(tag)
                
        with col2:
            nova_cor = st.color_picker(f"Cor {tag}", cor_padrao, label_visibility="collapsed")
            cores_escolhidas[tag] = nova_cor

    # Cálculo Matemático das Médias Móveis
    df_media_movel = df_simulado.rolling(window=janela_minutos).mean()

    # ---------------------------------------------------------
    # SEÇÃO DE GAUGES (MANÔMETROS E INDICADORES COM AS NOVAS TAGS)
    # ---------------------------------------------------------
    st.subheader("⚙️ Indicadores Atuais do Reator")
    
    g_cols = st.columns(3)
    
    # 1. Gauge de Pressão (PIC-30401)
    with g_cols[0]:
        val_pressao = df_simulado['PIC-30401'].iloc[-1]
        fig_p = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_pressao,
            title={'text': "<b>Pressão Reator</b><br><span style='font-size:0.8em;color:gray'>PIC-30401</span>", 'font': {'color': '#E0E0E0'}},
            number={'font': {'color': '#ff7f0e'}},
            gauge={
                'axis': {'range': [0, 25], 'tickcolor': "white"},
                'bar': {'color': "#ff7f0e"},
                'bgcolor': "#1E1E1E",
                'borderwidth': 2,
                'bordercolor': "#333333",
                'steps': [
                    {'range': [0, 15], 'color': '#2a2a2a'},
                    {'range': [15, 20], 'color': '#3a3a2a'},
                    {'range': [20, 25], 'color': '#4a2a2a'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 21}
            }
        ))
        fig_p.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
        st.plotly_chart(fig_p, use_container_width=True)

    # 2. Gauge de Temperatura (TIC-30401)
    with g_cols[1]:
        val_temp = df_simulado['TIC-30401'].iloc[-1]
        fig_t = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_temp,
            title={'text': "<b>Temp. Reator</b><br><span style='font-size:0.8em;color:gray'>TIC-30401</span>", 'font': {'color': '#E0E0E0'}},
            number={'font': {'color': '#9467bd'}},
            gauge={
                'axis': {'range': [50, 120], 'tickcolor': "white"},
                'bar': {'color': "#9467bd"},
                'bgcolor': "#1E1E1E",
                'borderwidth': 2,
                'bordercolor': "#333333",
                'steps': [
                    {'range': [50, 80], 'color': '#2a2a2a'},
                    {'range': [80, 105], 'color': '#2a3a2a'},
                    {'range': [105, 120], 'color': '#4a2a2a'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 110}
            }
        ))
        fig_t.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
        st.plotly_chart(fig_t, use_container_width=True)

    # 3. Gauge de Nível (LI-30401)
    with g_cols[2]:
        val_nivel = df_simulado['LI-30401'].iloc[-1]
        fig_n = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_nivel,
            title={'text': "<b>Nível Reator</b><br><span style='font-size:0.8em;color:gray'>LI-30401</span>", 'font': {'color': '#E0E0E0'}},
            number={'font': {'color': '#00BFFF'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#00BFFF"},
                'bgcolor': "#1E1E1E",
                'borderwidth': 2,
                'bordercolor': "#333333",
                'steps': [
                    {'range': [0, 20], 'color': '#4a2a2a'},
                    {'range': [20, 80], 'color': '#2a2a2a'},
                    {'range': [80, 100], 'color': '#4a2a2a'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 85}
            }
        ))
        fig_n.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
        st.plotly_chart(fig_n, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # CAIXAS DE DESVIO PADRÃO
    # ---------------------------------------------------------
    st.subheader("📈 Análise Estatística (Desvio Padrão vs Média Móvel)")
    
    stat_cols = st.columns(len(tags_selecionadas) if len(tags_selecionadas) > 0 else 1)
    
    if len(tags_selecionadas) > 0:
        for idx, tag in enumerate(tags_selecionadas):
            serie_diff = (df_simulado[tag] - df_media_movel[tag]).dropna()
            desvio_padrao_val = serie_diff.std()
            
            with stat_cols[idx % len(stat_cols)]:
                st.metric(
                    label=f"Desvio ({tag})", 
                    value=f"{desvio_padrao_val:.4f}",
                    delta="Flutuação vs Média"
                )

    st.markdown("---")

    # ---------------------------------------------------------
    # GRÁFICO PRINCIPAL DE TENDÊNCIA
    # ---------------------------------------------------------
    st.subheader("Tendência Histórica: Instantâneo vs Média Móvel")

    if len(tags_selecionadas) > 0:
        fig = go.Figure()

        for tag in tags_selecionadas:
            cor = cores_escolhidas[tag]
            
            # A) Linha do Valor Instantâneo 
            fig.add_trace(go.Scatter(
                x=df_simulado.index,
                y=df_simulado[tag],
                mode='lines',
                line=dict(color=cor, width=1),
                opacity=0.35, 
                name=f"{tag} (Inst)"
            ))
            
            # B) Linha da Média Móvel com Estrelas
            if mostrar_media_movel:
                fig.add_trace(go.Scatter(
                    x=df_media_movel.index,
                    y=df_media_movel[tag],
                    mode='lines+markers',
                    marker=dict(symbol='star', size=6), 
                    line=dict(color=cor, width=2.5),
                    name=f"Média {tag}"
                ))

        # Ajustes do Layout do Gráfico
        fig.update_layout(
            height=600,
            hovermode="x unified",
            plot_bgcolor='#1E1E1E',         
            paper_bgcolor='rgba(0,0,0,0)',  
            font=dict(color='#E0E0E0'),     
            xaxis=dict(showgrid=True, gridcolor='#333333', title="Tempo"),
            yaxis=dict(showgrid=True, gridcolor='#333333', title="Valores"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    else:
        st.warning("Selecione pelo menos uma TAG na barra lateral para visualizar o gráfico.")