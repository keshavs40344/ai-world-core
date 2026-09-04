import sys
import unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/world_assets/edge-json-shield")
from service import EngineService

class TestGeneratedAsset(unittest.TestCase):
    def test_execution(self):
        engine = EngineService()
        result = engine.execute("sample_key_1, sample_key_2")
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
