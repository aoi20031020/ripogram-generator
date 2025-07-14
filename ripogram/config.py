"""
Configuration management for ripogram.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for ripogram settings."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env file
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4")
        
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )
    
    def get_default_banned_chars(self) -> List[str]:
        """
        Get default banned characters from environment or return defaults.
        
        Returns:
            List of default banned characters
        """
        default_chars = os.getenv("DEFAULT_BANNED_CHARS", "さ,い")
        return [char.strip() for char in default_chars.split(",")]
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid
        """
        if not self.openai_api_key:
            return False
        
        if not self.model_name:
            return False
            
        return True
