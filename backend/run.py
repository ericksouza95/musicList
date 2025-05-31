#!/usr/bin/env python3
"""
Arquivo principal para executar a aplicação Flask
"""
import os
from app import create_app

# Criar a aplicação
app = create_app()

if __name__ == '__main__':
    # Configurações de desenvolvimento
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"🎵 Music List API iniciando...")
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"🔧 Debug: {debug_mode}")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    ) 