"""Classe base para os passos do pipeline de conversão"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStep(ABC):
    """Classe base abstrata para todos os passos do pipeline"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Processa os dados e retorna o resultado"""
        pass
    
    def __str__(self):
        return f"Step: {self.name}"
    
    def log_info(self, message: str):
        """Log de informações do passo"""
        print(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log de avisos do passo"""
        print(f"[{self.name}] ⚠️  {message}")
    
    def log_error(self, message: str):
        """Log de erros do passo"""
        print(f"[{self.name}] ❌ {message}")
