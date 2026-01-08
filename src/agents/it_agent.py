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
                # Try absolute path
                path = os.path.join(os.getcwd(), path)
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('it_provisioning', {})
        except Exception as e:
            logger.error(f"Config load error: {e}. Using defaults.")
            return {}

    def generate_email(self, name: str) -> str:
        # LOGIC: firstname.lastname@company.com
        clean = name.lower().replace(" ", ".")
        return f"{clean}@company.com"

    def run(self, employee: Employee) -> str:
        logger.info(f"Provisioning for: {employee.name}")
        
        role_normalized = employee.role.lower()
        rules = self.config.get('rules', [])
        default_asset = self.config.get('default_asset', "Standard Laptop")

        # 1. Check Config Rules
        for rule in rules:
            keywords = rule.get('keywords', [])
            asset = rule.get('asset')
            if any(k in role_normalized for k in keywords):
                return asset

        return default_asset