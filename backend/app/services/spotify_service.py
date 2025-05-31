import os
import requests
import base64
from datetime import datetime, timedelta


class SpotifyService:
    """Serviço para integração com a API do Spotify"""
    
    def __init__(self):
        self.client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        self.client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        self.base_url = 'https://api.spotify.com/v1'
        self.auth_url = 'https://accounts.spotify.com/api/token'
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self):
        """Obtém token de acesso do Spotify usando Client Credentials Flow"""
        if not self.client_id or not self.client_secret:
            print("⚠️  Spotify API credentials não configuradas")
            return None
        
        # Verificar se token ainda é válido
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        try:
            # Preparar credenciais
            credentials = f"{self.client_id}:{self.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {credentials_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(self.auth_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                return self.access_token
            else:
                print(f"❌ Erro ao obter token do Spotify: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na autenticação do Spotify: {str(e)}")
            return None
    
    def _make_request(self, endpoint, params=None):
        """Faz uma requisição autenticada para a API do Spotify"""
        token = self._get_access_token()
        if not token:
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na requisição Spotify: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição Spotify: {str(e)}")
            return None
    
    def search_tracks(self, query, limit=20, offset=0):
        """Busca músicas no Spotify"""
        if not query:
            return []
        
        params = {
            'q': query,
            'type': 'track',
            'limit': min(limit, 50),
            'offset': offset,
            'market': 'BR'  # Mercado brasileiro
        }
        
        data = self._make_request('search', params)
        if not data or 'tracks' not in data:
            return []
        
        tracks = []
        for track in data['tracks']['items']:
            track_data = self._format_track_data(track)
            if track_data:
                tracks.append(track_data)
        
        return tracks
    
    def get_track(self, track_id):
        """Obtém informações de uma música específica"""
        data = self._make_request(f'tracks/{track_id}')
        if not data:
            return None
        
        return self._format_track_data(data)
    
    def get_track_features(self, track_id):
        """Obtém características de áudio de uma música"""
        data = self._make_request(f'audio-features/{track_id}')
        return data
    
    def search_artists(self, query, limit=20):
        """Busca artistas no Spotify"""
        params = {
            'q': query,
            'type': 'artist',
            'limit': min(limit, 50),
            'market': 'BR'
        }
        
        data = self._make_request('search', params)
        if not data or 'artists' not in data:
            return []
        
        artists = []
        for artist in data['artists']['items']:
            artists.append({
                'id': artist['id'],
                'name': artist['name'],
                'genres': artist.get('genres', []),
                'popularity': artist.get('popularity', 0),
                'followers': artist.get('followers', {}).get('total', 0),
                'images': artist.get('images', []),
                'external_url': artist.get('external_urls', {}).get('spotify')
            })
        
        return artists
    
    def get_artist_top_tracks(self, artist_id, limit=10):
        """Obtém top tracks de um artista"""
        params = {'market': 'BR'}
        data = self._make_request(f'artists/{artist_id}/top-tracks', params)
        
        if not data or 'tracks' not in data:
            return []
        
        tracks = []
        for track in data['tracks'][:limit]:
            track_data = self._format_track_data(track)
            if track_data:
                tracks.append(track_data)
        
        return tracks
    
    def _format_track_data(self, track):
        """Formata dados de uma música do Spotify para nosso padrão"""
        try:
            # Artistas
            artists = []
            if track.get('artists'):
                artists = [artist['name'] for artist in track['artists']]
            
            # Imagem da capa
            cover_image = None
            if track.get('album', {}).get('images'):
                # Pegar imagem de tamanho médio
                images = track['album']['images']
                if images:
                    cover_image = images[0]['url']  # Primeira imagem (maior)
                    # Procurar imagem de ~300px
                    for img in images:
                        if 200 <= img.get('width', 0) <= 400:
                            cover_image = img['url']
                            break
            
            # Gêneros (do álbum, se disponível)
            genres = []
            if track.get('album', {}).get('genres'):
                genres = track['album']['genres']
            
            return {
                'title': track.get('name', ''),
                'artist': ', '.join(artists),
                'album': track.get('album', {}).get('name', ''),
                'year': self._extract_year(track.get('album', {}).get('release_date')),
                'duration': track.get('duration_ms', 0) // 1000,  # converter para segundos
                'track_number': track.get('track_number'),
                'spotify_id': track.get('id'),
                'external_url': track.get('external_urls', {}).get('spotify'),
                'preview_url': track.get('preview_url'),
                'cover_image_url': cover_image,
                'genre': ', '.join(genres) if genres else None,
                'popularity': track.get('popularity', 0),
                'explicit': track.get('explicit', False),
                'is_local': False,
                'is_public': True
            }
            
        except Exception as e:
            print(f"❌ Erro ao formatar dados da música: {str(e)}")
            return None
    
    def _extract_year(self, release_date):
        """Extrai o ano de uma data de lançamento"""
        if not release_date:
            return None
        
        try:
            return int(release_date.split('-')[0])
        except:
            return None


# Instância global do serviço
spotify_service = SpotifyService() 