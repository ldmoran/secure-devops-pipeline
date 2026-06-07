"""
Configuración para Render deployment
"""
import os
from pathlib import Path

class Config:
    """Configuración base"""
    DEBUG = False
    TESTING = False
    
class DevelopmentConfig(Config):
    """Desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Producción (Render)"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing"""
    TESTING = True

# Seleccionar config según ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    """Obtiene la configuración según ambiente"""
    env = os.getenv('FLASK_ENV', 'production')
    return config.get(env, ProductionConfig)
