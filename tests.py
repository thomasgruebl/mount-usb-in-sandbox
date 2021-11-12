import unittest
import helpers


class BasicTest(unittest.TestCase):
    def test_sites_json(self):
        self.assertIsNotNone(helpers.get_network_interfaces())


if __name__ == '__main__':
    unittest.main()
