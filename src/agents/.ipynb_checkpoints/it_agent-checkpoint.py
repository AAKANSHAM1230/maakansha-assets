import yaml
import os
from src.models.employee import Employee
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ITProvisionAgent:
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> dict:
        try:
            if not os.path.exists(path):
                path = os.path.join(os.getcwd(), path)
            
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('it_provisioning', {})
        except Exception as e:
            logger.error(f"Config load error: {e}. Using defaults.")
            return {}

    def run(self, employee: Employee) -> str:
        logger.info(f"IT Agent processing: {employee.name} | Role: {employee.role}")
        
        role_normalized = employee.role.lower()
        
        rules = self.config.get('rules', [])
        default_asset = self.config.get('default_asset', "Standard Laptop")

        for rule in rules:
            keywords = rule.get('keywords', [])
            asset = rule.get('asset')
            
            if any(keyword in role_normalized for keyword in keywords):
                logger.info(f"Match found for '{employee.role}'. Assigning: {asset}")
                return asset

        logger.info(f"No specific match for '{employee.role}'. Assigning default: {default_asset}")
        return default_asset