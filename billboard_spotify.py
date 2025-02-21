import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import re

# Carregar variáveis de ambiente
load_dotenv()

def get_spotify_client():
    """Inicializa e retorna o cliente do Spotify"""
    try:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise Exception(
                "Credenciais do Spotify não encontradas! "
                "Certifique-se de criar um arquivo .env com SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET"
            )
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    except Exception as e:
        print(f"Erro ao inicializar cliente do Spotify: {str(e)}")
        return None

def find_valid_date(year, month):
    """Encontra uma data válida no mês para consulta"""
    try:
        # Criar data para o primeiro dia do mês
        target_date = datetime(year, month, 1)
        
        # Encontrar o primeiro sábado do mês
        while target_date.weekday() != 5:  # 5 = Sábado
            target_date += timedelta(days=1)
        
        formatted_date = target_date.strftime('%Y-%m-%d')
        print(f"Data de busca: {formatted_date}")
        return formatted_date
    
    except Exception as e:
        print(f"Erro ao gerar data: {str(e)}")
        return f"{year}-{month:02d}-01"

def get_billboard_data(year, month):
    """Busca dados do Billboard Hot 100 para um determinado mês/ano"""
    try:
        # Formatar a data para o primeiro dia do mês
        date = f"{year}-{month:02d}-01"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # URL direta para a data específica
        url = f"https://www.billboard.com/charts/hot-100/{date}/"
        print(f"Buscando URL: {url}")
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erro na resposta: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        songs = []
        
        # Seletores específicos para diferentes períodos
        selectors = [
            # Formato mais recente (2012-presente)
            {
                'container': 'div.o-chart-results-list-row-container',
                'title': 'h3#title-of-a-story, span.c-title',
                'artist': 'span.c-label.a-no-trucate'
            },
            # Formato intermediário (2010-2012)
            {
                'container': 'div.chart-list-item',
                'title': 'span.chart-element__information__song',
                'artist': 'span.chart-element__information__artist'
            },
            # Formato antigo (pré-2010)
            {
                'container': 'tr.chart-list__element',
                'title': 'td.chart-list__song',
                'artist': 'td.chart-list__artist'
            }
        ]
        
        for selector in selectors:
            items = soup.select(selector['container'])
            if not items:
                continue
                
            print(f"Usando seletor: {selector['container']}")
            
            for item in items[:10]:
                try:
                    # Buscar título
                    title_element = item.select_one(selector['title'])
                    if not title_element:
                        continue
                    
                    # Buscar artista
                    artist_element = item.select_one(selector['artist'])
                    if not artist_element:
                        continue
                    
                    title = title_element.get_text().strip()
                    artist = artist_element.get_text().strip()
                    
                    # Limpar os dados
                    title = ' '.join(title.split())
                    artist = ' '.join(artist.split())
                    
                    # Verificar se os dados são válidos
                    if title and artist and len(title) > 1 and len(artist) > 1:
                        print(f"Encontrado: {title} - {artist}")
                        songs.append({
                            'title': title,
                            'artist': artist
                        })
                        
                except Exception as e:
                    print(f"Erro ao processar item: {str(e)}")
                    continue
            
            if len(songs) >= 10:
                break
        
        if not songs:
            # Tentar um método alternativo para anos mais antigos
            try:
                old_items = soup.select('table.chart-table tr')
                for item in old_items[1:11]:  # Pular o cabeçalho
                    song_info = item.select('td')
                    if len(song_info) >= 3:
                        title = song_info[1].get_text().strip()
                        artist = song_info[2].get_text().strip()
                        if title and artist:
                            songs.append({
                                'title': title,
                                'artist': artist
                            })
            except Exception as e:
                print(f"Erro no método alternativo: {str(e)}")
        
        if not songs:
            print("Nenhuma música encontrada")
            return None
        
        print(f"Total de músicas encontradas: {len(songs)}")
        return songs[:10]
        
    except Exception as e:
        print(f"Erro ao buscar dados do Billboard: {str(e)}")
        return None

def search_spotify_links(songs):
    """Busca links do Spotify para uma lista de músicas"""
    spotify_links = []
    
    if not songs:
        return []
    
    # Inicializar cliente do Spotify
    sp = get_spotify_client()
    if not sp:
        print("Não foi possível inicializar o cliente do Spotify")
        return [''] * len(songs)
    
    for song in songs:
        try:
            time.sleep(0.5)  
            
            query = f"{song['title']} {song['artist']}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track_url = results['tracks']['items'][0]['external_urls']['spotify']
                spotify_links.append(track_url)
                print(f"Link encontrado para: {song['title']}")
            else:
                spotify_links.append('')
                print(f"Nenhum link encontrado para: {song['title']}")
                
        except Exception as e:
            print(f"Erro ao buscar música no Spotify: {str(e)}")
            spotify_links.append('')
    
    return spotify_links


__all__ = ['get_billboard_data', 'search_spotify_links']