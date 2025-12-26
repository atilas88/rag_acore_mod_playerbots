# src/generation/prompt_builder.py
"""
Builds specialized prompts based on query type
"""

from typing import List, Dict

class PromptBuilder:    
    
    def __init__(self):
        self.query_types = {
            'configuration': ['config', 'setting', 'configure', 'setup', 'parámetro'],
            'debugging': ['error', 'bug', 'problema', 'no funciona', 'crash', 'fallo'],
            'implementation': ['cómo hacer', 'implementar', 'crear', 'agregar', 'añadir', 'código'],
            'explanation': ['qué es', 'cómo funciona', 'explicar', 'entender'],
        }
    
    def build_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Build prompt based on query type"""
        query_type = self._detect_query_type(query)
        
        if query_type == 'configuration':
            return self._build_config_prompt(query, chunks)
        elif query_type == 'debugging':
            return self._build_debug_prompt(query, chunks)
        elif query_type == 'implementation':
            return self._build_implementation_prompt(query, chunks)
        elif query_type == 'explanation':
            return self._build_explanation_prompt(query, chunks)
        else:
            return self._build_general_prompt(query, chunks)
    
    def _detect_query_type(self, query: str) -> str:
        """Detect query type based on keywords"""
        query_lower = query.lower()
        
        for qtype, keywords in self.query_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return qtype
        
        return 'general'
    
    def _build_config_prompt(self, query: str, chunks: List[Dict]) -> str:

        context = self._format_chunks(chunks)

        return f"""Eres un experto en configuración de AzerothCore y mod-playerbots.

        DOCUMENTACIÓN DE CONFIGURACIÓN:
        {context}

        PREGUNTA DEL USUARIO: {query}

        Proporciona una respuesta estructurada con:

        1. **Configuración exacta necesaria:**
        - Archivo de configuración
        - Parámetros específicos
        - Valores recomendados

        2. **Explicación:**
        - Qué hace cada parámetro
        - Por qué usar estos valores

        3. **Ejemplo de configuración:**
        ```conf
        [Ejemplo aquí]

            Consideraciones importantes:
                Advertencias
                Efectos secundarios
                Compatibilidad

        Si la información no está completa en la documentación, indícalo claramente y sugiere dónde buscar más información."""


    def _build_debug_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Prompt for debugging"""
        context = self._format_chunks(chunks)
    
        return f"""Eres un experto en debugging de AzerothCore y mod-playerbots.

        CÓDIGO Y DOCUMENTACIÓN RELEVANTE:
        {context}

        PROBLEMA REPORTADO: {query}

        Analiza el problema y proporciona:

            Diagnóstico:
                Posibles causas del problema
                Qué componentes están involucrados

            Verificación:
                Archivos y funciones a revisar
                Logs específicos a buscar
                Cómo reproducir el problema

            Soluciones:
                Solución principal (con código si aplica)
                Alternativas
                Workarounds temporales

            Prevención:
                Cómo evitar el problema en el futuro
                Mejores prácticas relacionadas

        Sé específico con nombres de funciones, clases, archivos y líneas de código cuando sea posible."""

    
    def _build_implementation_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Prompt for implementation guidance"""
        context = self._format_chunks(chunks)
        
        return f"""Eres un experto desarrollador de AzerothCore y mod-playerbots.

        EJEMPLOS DE CÓDIGO Y PATRONES:
        {context}

        TAREA A IMPLEMENTAR: {query}

        Proporciona una guía completa:

        1. **Approach:**
        - Estrategia recomendada
        - Patrones a seguir
        - Arquitectura sugerida

        2. **Implementación:**
        ```cpp
        // Código de ejemplo siguiendo los patrones del proyecto
        ```

        3. **Archivos a modificar:**
        - Lista de archivos
        - Qué cambiar en cada uno
        - Orden de implementación

        4. **Testing:**
        - Cómo probar la implementación
        - Casos de prueba importantes
        - Comandos de verificación

        5. **Consideraciones:**
        - Performance
        - Seguridad
        - Compatibilidad con mods existentes

        Usa los patrones de código mostrados en la documentación y sigue las convenciones del proyecto."""
    
    def _build_explanation_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Prompt for explanations"""
        context = self._format_chunks(chunks)
        
        return f"""Eres un experto en AzerothCore y mod-playerbots que explica conceptos de forma clara.

        DOCUMENTACIÓN RELEVANTE:
        {context}

        PREGUNTA: {query}

        Proporciona una explicación clara y estructurada:

        1. **Concepto principal:**
        - Definición simple
        - Para qué sirve

        2. **Cómo funciona:**
        - Explicación técnica
        - Diagrama conceptual si es útil
        - Flujo de ejecución

        3. **Componentes involucrados:**
        - Clases principales
        - Funciones importantes
        - Relaciones entre componentes

        4. **Ejemplo práctico:**
        - Caso de uso real
        - Código de ejemplo si aplica

        5. **Referencias:**
        - Archivos relacionados
        - Documentación adicional

        Usa analogías cuando sea útil y mantén un balance entre simplicidad y profundidad técnica."""

    def _build_general_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Prompt for general queries"""
        context = self._format_chunks(chunks)
        
        return f"""Eres un experto en AzerothCore y mod-playerbots.

        DOCUMENTACIÓN RELEVANTE:
        {context}

        PREGUNTA: {query}

        Proporciona una respuesta precisa y útil basándote en la documentación proporcionada.

        Incluye:
        - Respuesta directa a la pregunta
        - Ejemplos o código cuando sea relevante
        - Referencias a archivos o funciones específicas
        - Información adicional útil relacionada

        Si la documentación no contiene información suficiente para responder completamente, indícalo claramente y sugiere dónde el usuario podría encontrar más información."""

    def _format_chunks(self, chunks: List[Dict]) -> str:
        """Format chunks for inclusion in the prompt"""
        if not chunks:
            return "No relevant information available."
    
        formatted_parts = []
    
        for i, chunk_data in enumerate(chunks, 1):
            chunk = chunk_data.get('chunk', {})
            metadata = chunk_data.get('metadata', {})
        
            header = f"""

            {'='*70} SOURCE {i}: {metadata.get('filename', 'desconocido')} Path: {metadata.get('filepath', 'N/A')} Module: {metadata.get('module', 'N/A')} Category: {metadata.get('category', 'N/A')} """ 
            
            if metadata.get('subsystem'): 
                header += f"Subsystem: {metadata['subsystem']}\n"

            if metadata.get('tags'):
                header += f"Tags: {', '.join(metadata['tags'][:5])}\n"
        
            if 'combined_score' in chunk_data:
                header += f"Relevance: {chunk_data['combined_score']:.2f}\n"
            elif 'similarity' in chunk_data:
                header += f"Similarity: {chunk_data['similarity']:.2f}\n"

            header += '='*70
        
            content = chunk.get('content', '')
        
            formatted_parts.append(f"{header}\n\n{content}\n")
    
        return '\n'.join(formatted_parts)
