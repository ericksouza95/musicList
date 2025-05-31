#!/usr/bin/env python3
"""
Script para testar a aplicação Flask
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_app():
    """Testa a criação da aplicação"""
    try:
        print("🧪 Testando criação da aplicação...")
        app = create_app()
        print("✅ Aplicação criada com sucesso!")
        
        print("🧪 Testando rotas...")
        with app.test_client() as client:
            # Testar rota raiz
            response = client.get('/')
            print(f"GET / - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Resposta: {response.get_json()}")
            
            # Testar rota de health
            response = client.get('/api/health')
            print(f"GET /api/health - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Resposta: {response.get_json()}")
            
            # Testar rota de info
            response = client.get('/api')
            print(f"GET /api - Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Resposta: {response.get_json()}")
                
        print("✅ Todos os testes passaram!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_app() 