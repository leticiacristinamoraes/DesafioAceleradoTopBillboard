import streamlit as st
import pandas as pd
from billboard_spotify import get_billboard_data, search_spotify_links
import json
from datetime import datetime

def load_or_create_data():
    try:
        with open('music_cache.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open('music_cache.json', 'w') as f:
        json.dump(data, f)

def main():
    st.set_page_config(
        page_title="Billboard Hot 100 - Top 10",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title('🎵 Billboard Hot 100 - Top 10 com Links do Spotify')
    
    st.markdown("""
    Esta aplicação mostra as 10 músicas mais populares da Billboard Hot 100 para um mês e ano específicos,
    incluindo links diretos para o Spotify.
    """)
    
    # Layout em colunas para os seletores
    col1, col2 = st.columns(2)
    
    with col1:
        current_year = datetime.now().year
        year = st.selectbox('Ano', range(current_year, 1957, -1))
    
    with col2:
        month = st.selectbox('Mês', range(1, 13), format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
    
    if st.button('Buscar Top 10', type='primary'):
        try:
            with st.spinner('Buscando dados...'):
                billboard_data = get_billboard_data(year, month)
                
                if not billboard_data:
                    st.error(f'Não foram encontrados dados para {month}/{year}. Algumas possíveis razões:\n' +
                            '- O Billboard pode não ter dados para este período\n' +
                            '- O formato da página pode ser diferente para este ano\n' +
                            '- A data pode não estar disponível\n\n' +
                            'Tente uma data mais recente ou entre em contato com o suporte.')
                    return
                
                spotify_links = search_spotify_links(billboard_data)
                
                df = pd.DataFrame({
                    'Posição': list(range(1, len(billboard_data) + 1)),
                    'Música': [song['title'] for song in billboard_data],
                    'Artista': [song['artist'] for song in billboard_data],
                    'Link Spotify': spotify_links
                })
                
                # Exibir resultados
                st.subheader(f'Top 10 - {datetime(2000, month, 1).strftime("%B")}/{year}')
                
                # Botões de download
                col1, col2, col3 = st.columns([1,1,2])
                
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"billboard_top10_{year}_{month}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    json_str = df.to_json(orient='records')
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"billboard_top10_{year}_{month}.json",
                        mime="application/json"
                    )
                
                # Exibir cada música em um card
                for _, row in df.iterrows():
                    with st.container():
                        st.markdown("""---""")
                        cols = st.columns([1, 4])
                        
                        with cols[0]:
                            st.markdown(f"### #{row['Posição']}")
                        
                        with cols[1]:
                            st.markdown(f"### {row['Música']}")
                            st.markdown(f"**Artista:** {row['Artista']}")
                            if pd.notna(row['Link Spotify']) and row['Link Spotify']:
                                st.markdown(f"[🎵 Ouvir no Spotify]({row['Link Spotify']})")
                            else:
                                st.markdown("*Link do Spotify não disponível*")
                
        except Exception as e:
            st.error(f'Ocorreu um erro: {str(e)}')
            st.error('Por favor, tente novamente.')
    
    st.markdown("""---""")
    st.markdown("""
    <div style='text-align: center'>
        <p>Desenvolvido por Letícia Cristina França Moraes Dos Santos</p>
        <p>Dados obtidos do Billboard Hot 100</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()