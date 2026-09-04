import sys
import unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/ventures/v_gpt_6_astra_1788514914")
from engine_service import EngineService

class TestEngineService(unittest.TestCase):
    def setUp(self):
        self.srv = EngineService()

    def test_nominal_execution(self):
        res = self.srv.process_data("hello_world")
        self.assertEqual(res["status"], "PROCESSED")
        self.assertIn("sha256", res)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.srv.process_data("")

if __name__ == "__main__":
    unittest.main()
