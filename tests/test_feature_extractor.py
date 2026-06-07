"""
Tests para el extractor de características
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security_checker.feature_extractor import JavaCodeAnalyzer, extract_features_from_code

class TestJavaCodeAnalyzer:
    """Tests para JavaCodeAnalyzer"""
    
    def test_extract_features_empty_code(self):
        """Test con código vacío"""
        features = JavaCodeAnalyzer.extract_features("")
        assert features is not None
        assert all(v == 0.0 for v in features.values())
    
    def test_extract_features_simple_code(self):
        """Test con código simple"""
        code = """
        public class Hello {
            public static void main(String[] args) {
                System.out.println("Hello");
            }
        }
        """
        features = JavaCodeAnalyzer.extract_features(code)
        
        assert features['code_length'] > 0
        assert features['line_count'] > 0
        assert features['token_count'] > 0
        assert features['keyword_count'] > 0
    
    def test_extract_features_dangerous_functions(self):
        """Test detectando funciones peligrosas"""
        code = """
        Runtime rt = Runtime.getRuntime();
        Process p = rt.exec("command");
        """
        features = JavaCodeAnalyzer.extract_features(code)
        assert features['dangerous_function_count'] > 0
    
    def test_extract_features_sql_injection(self):
        """Test detectando SQL injection"""
        code = """
        String query = "SELECT * FROM users WHERE id = " + userId;
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(query);
        """
        features = JavaCodeAnalyzer.extract_features(code)
        assert features['sql_pattern_count'] > 0
    
    def test_extract_features_sanitization(self):
        """Test detectando sanitización"""
        code = """
        String query = "SELECT * FROM users WHERE id = ?";
        PreparedStatement pstmt = conn.prepareStatement(query);
        pstmt.setInt(1, userId);
        """
        features = JavaCodeAnalyzer.extract_features(code)
        assert features['sanitization_count'] > 0
    
    def test_extract_features_exception_handling(self):
        """Test detectando manejo de excepciones"""
        code = """
        try {
            // risky operation
        } catch (SQLException e) {
            logger.error("Error", e);
        }
        """
        features = JavaCodeAnalyzer.extract_features(code)
        assert features['try_catch_count'] > 0
    
    def test_extract_features_to_array(self):
        """Test convirtiendo features a array"""
        code = "public class Test { }"
        features_array, feature_names = extract_features_from_code(code)
        
        assert features_array.shape[0] == 1
        assert features_array.shape[1] == len(feature_names)
        assert len(feature_names) == 14
    
    def test_bracket_depth(self):
        """Test calculando profundidad de llaves"""
        code = "{{ {{ }} }}"
        depth = JavaCodeAnalyzer._calculate_bracket_depth(code)
        assert depth == 4
    
    def test_count_keywords(self):
        """Test contando palabras clave"""
        code = "public static void main(String[] args) { if (true) { } }"
        count = JavaCodeAnalyzer._count_keywords(code)
        assert count > 0
    
    def test_all_features_present(self):
        """Test que todas las características están presentes"""
        code = "public class Test { public void test() { } }"
        features = JavaCodeAnalyzer.extract_features(code)
        
        expected_features = [
            'code_length', 'line_count', 'token_count', 'bracket_depth',
            'brace_count', 'parenthesis_count', 'keyword_count', 'comment_ratio',
            'dangerous_function_count', 'sql_pattern_count', 'system_call_count',
            'reflection_count', 'sanitization_count', 'try_catch_count'
        ]
        
        for feature in expected_features:
            assert feature in features, f"Feature {feature} missing"

class TestFeatureExtraction:
    """Tests para función extract_features_from_code"""
    
    def test_returns_tuple(self):
        """Test que retorna tupla"""
        code = "public class Test { }"
        result = extract_features_from_code(code)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_array_shape(self):
        """Test forma del array"""
        code = "public class Test { }"
        features_array, feature_names = extract_features_from_code(code)
        
        assert features_array.shape[0] == 1  # Un registro
        assert features_array.shape[1] == len(feature_names)
    
    def test_feature_names_sorted(self):
        """Test que feature names están ordenados"""
        code = "public class Test { }"
        _, feature_names = extract_features_from_code(code)
        
        assert feature_names == sorted(feature_names)
    
    def test_handles_null_code(self):
        """Test manejo de código None"""
        result = extract_features_from_code(None)
        features_array, feature_names = result
        assert features_array is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
