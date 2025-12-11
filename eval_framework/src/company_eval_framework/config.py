"""Configuration models using Pydantic."""

import yaml
from typing import Dict, Optional, Any
from pydantic import BaseModel, ConfigDict


class AdapterConfig(BaseModel):
    """Configuration for the adapter that calls the app."""
    
    model_config = ConfigDict(extra="allow")
    
    module: str
    function: str


class DatasetConfig(BaseModel):
    """Configuration for the dataset."""
    
    model_config = ConfigDict(extra="allow")
    
    mode: str  # "static" or "synthetic"
    path: Optional[str] = None
    size: Optional[int] = None
    context_field: Optional[str] = None


class EvalConfig(BaseModel):
    """Main evaluation configuration."""
    
    model_config = ConfigDict(extra="allow")
    
    app_name: str
    app_type: str
    adapter: AdapterConfig
    dataset: DatasetConfig
    eval_suite: str
    thresholds: Dict[str, Dict[str, Any]]


def load_eval_config(config_path: str) -> EvalConfig:
    """Load evaluation config from YAML file.
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        EvalConfig object
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return EvalConfig(**config_dict)
