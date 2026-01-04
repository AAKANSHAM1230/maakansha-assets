import sys
import os
from datetime import datetime

# Add the project root to the python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.employee import Employee
from src.agents.it_agent import ITProvisionAgent

def run_tests():
    agent = ITProvisionAgent(config_path="config.yaml")

    test_cases = [
        {
            "name": "Jane Doe",
            "role": "Senior AI SCE", 
            "expected": "MacBook Pro 16-inch (M3 Max)",
            "reason": "Should match keyword 'sce' or 'ai'"
        },
        {
            "name": "Bob Ross",
            "role": "Creative Lead", 
            "expected": "MacBook Air 15-inch",
            "reason": "Should match keyword 'creative'"
        },
        {
            "name": "Alice Manager",
            "role": "HR Generalist", 
            "expected": "Chromebook Enterprise",
            "reason": "No keyword match -> Default asset"
        },
        {
            "name": "Sam Altman", 
            "role": "CEO", 
            "expected": "MacBook Pro 14-inch (M3 Pro)",
            "reason": "Should match keyword 'c-suite' or implied executive role rules"
        }
    ]

    passed = 0
    total = len(test_cases)

    for case in test_cases:
        #Employee object
        emp = Employee(
            name=case["name"],
            role=case["role"],
            start_date=datetime.now()
        )

        result = agent.run(emp)


        if result == case["expected"]:
            print(f"PASS: {case['role']} -> {result}")
            passed += 1
        else:
            print(f"FAIL: {case['role']}")
            print(f"Expected: {case['expected']}")
            print(f"Got:      {result}")
            print(f"Reason:   {case['reason']}")
    print(f"Tests Complete. {passed}/{total} passed.")

if __name__ == "__main__":
    run_tests()