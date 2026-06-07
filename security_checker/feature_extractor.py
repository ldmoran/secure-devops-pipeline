"""
Feature Extractor para código Java
Extrae características relevantes para clasificación de vulnerabilidades
"""
import re
import ast
from typing import Dict, List
import numpy as np

class JavaCodeAnalyzer:
    """Analizador de características de código Java"""
    
    # Palabras clave Java
    KEYWORDS = {
        'public', 'private', 'protected', 'static', 'final', 'abstract',
        'class', 'interface', 'extends', 'implements', 'new', 'return',
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
        'continue', 'try', 'catch', 'finally', 'throw', 'throws'
    }
    
    # Funciones peligrosas
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'Runtime.getRuntime', 'ProcessBuilder', 'Query',
        'createStatement', 'executeQuery', 'executeUpdate', 'System.exit',
        'System.load', 'System.loadLibrary', 'Constructor.newInstance',
        'Method.invoke', 'Field.get', 'Field.set'
    }
    
    # Patrones de inyección SQL
    SQL_PATTERNS = [
        r'executeQuery\s*\(',
        r'executeUpdate\s*\(',
        r'Statement\s*=',
        r'SELECT\s+',
        r'INSERT\s+',
        r'UPDATE\s+',
        r'DELETE\s+',
        r'DROP\s+'
    ]
    
    # Patrones de sanitización
    SANITIZATION_PATTERNS = [
        r'PreparedStatement',
        r'parameterized',
        r'sanitize',
        r'escape',
        r'validate',
        r'whitelist',
        r'htmlEncode',
        r'urlEncode'
    ]
    
    @staticmethod
    def extract_features(code: str) -> Dict[str, float]:
        """
        Extrae características del código
        
        Args:
            code: Código fuente Java
            
        Returns:
            Diccionario con características
        """
        if not code or not isinstance(code, str):
            return JavaCodeAnalyzer._get_empty_features()
        
        features = {}
        
        # Características básicas
        features['code_length'] = len(code)
        features['line_count'] = code.count('\n') + 1
        features['token_count'] = len(re.findall(r'\w+', code))
        
        # Complejidad
        features['bracket_depth'] = JavaCodeAnalyzer._calculate_bracket_depth(code)
        features['brace_count'] = code.count('{') + code.count('}')
        features['parenthesis_count'] = code.count('(') + code.count(')')
        
        # Palabras clave
        features['keyword_count'] = JavaCodeAnalyzer._count_keywords(code)
        features['comment_ratio'] = JavaCodeAnalyzer._calculate_comment_ratio(code)
        
        # Peligro
        features['dangerous_function_count'] = JavaCodeAnalyzer._count_dangerous_functions(code)
        features['sql_pattern_count'] = JavaCodeAnalyzer._count_sql_patterns(code)
        features['system_call_count'] = code.lower().count('system.')
        features['reflection_count'] = code.lower().count('.getmethod') + code.lower().count('.getfield')
        
        # Sanitización
        features['sanitization_count'] = JavaCodeAnalyzer._count_sanitization(code)
        features['try_catch_count'] = JavaCodeAnalyzer._count_try_catch(code)
        
        # Normalizar características
        features = JavaCodeAnalyzer._normalize_features(features)
        
        return features
    
    @staticmethod
    def _get_empty_features() -> Dict[str, float]:
        """Retorna diccionario de características con valores 0"""
        return {
            'code_length': 0.0,
            'line_count': 0.0,
            'token_count': 0.0,
            'bracket_depth': 0.0,
            'brace_count': 0.0,
            'parenthesis_count': 0.0,
            'keyword_count': 0.0,
            'comment_ratio': 0.0,
            'dangerous_function_count': 0.0,
            'sql_pattern_count': 0.0,
            'system_call_count': 0.0,
            'reflection_count': 0.0,
            'sanitization_count': 0.0,
            'try_catch_count': 0.0
        }
    
    @staticmethod
    def _calculate_bracket_depth(code: str) -> int:
        """Calcula la profundidad máxima de llaves"""
        print("CODE:", code)
        depth = 0
        max_depth = 0
        for char in code:
            if char == '{':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == '}':
                depth = max(0, depth - 1)
        return max_depth
    
    @staticmethod
    def _count_keywords(code: str) -> int:
        """Cuenta palabras clave Java"""
        count = 0
        for keyword in JavaCodeAnalyzer.KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            count += len(re.findall(pattern, code, re.IGNORECASE))
        return count
    
    @staticmethod
    def _calculate_comment_ratio(code: str) -> float:
        """Calcula el ratio de comentarios"""
        comment_chars = len(re.findall(r'//.*|/\*.*?\*/', code, re.DOTALL))
        total_chars = len(code)
        return comment_chars / total_chars if total_chars > 0 else 0.0
    
    @staticmethod
    def _count_dangerous_functions(code: str) -> int:
        """Cuenta llamadas a funciones peligrosas"""
        count = 0
        for func in JavaCodeAnalyzer.DANGEROUS_FUNCTIONS:
            count += len(re.findall(r'\b' + re.escape(func) + r'\b', code, re.IGNORECASE))
        return count
    
    @staticmethod
    def _count_sql_patterns(code: str) -> int:
        """Cuenta patrones potenciales de SQL injection"""
        count = 0
        for pattern in JavaCodeAnalyzer.SQL_PATTERNS:
            count += len(re.findall(pattern, code, re.IGNORECASE))
        return count
    
    @staticmethod
    def _count_sanitization(code: str) -> int:
        """Cuenta mecanismos de sanitización"""
        count = 0
        for pattern in JavaCodeAnalyzer.SANITIZATION_PATTERNS:
            count += len(re.findall(r'\b' + pattern + r'\b', code, re.IGNORECASE))
        return count
    
    @staticmethod
    def _count_try_catch(code: str) -> int:
        """Cuenta bloques try-catch"""
        return len(re.findall(r'\btry\b.*?\bcatch\b', code, re.IGNORECASE | re.DOTALL))
    
    @staticmethod
    def _normalize_features(features: Dict[str, float]) -> Dict[str, float]:
        """Normaliza características"""
        # Log transform para características de conteo
        log_features = ['code_length', 'token_count', 'brace_count', 'parenthesis_count']
        for key in log_features:
            if key in features and features[key] > 0:
                features[key] = np.log1p(features[key])
        
        return features


def extract_features_from_code(code: str) -> np.ndarray:
    """
    Función auxiliar para extraer features como array
    
    Args:
        code: Código Java
        
    Returns:
        Array numpy con características
    """
    features_dict = JavaCodeAnalyzer.extract_features(code)
    feature_names = sorted(features_dict.keys())
    features_array = np.array([features_dict[name] for name in feature_names]).reshape(1, -1)
    return features_array, feature_names
