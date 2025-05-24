# To run these tests, execute:
# python -m unittest test_everwing_data.py
# or for more verbose output:
# python -m unittest -v test_everwing_data.py

import unittest
import sys
import os
import json # For json.dumps in test_serialize_to_json and json.JSONDecodeError
import copy # For deepcopying test data

# Add the root directory to sys.path to allow importing Everwing_data
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Initialize globals that will hold the functions to test
Everwing_data_module = None
compress_to_lz_string_func = None
decompress_lz_string_func = None
parse_json_func = None
serialize_to_json_func = None
prepare_dragons_for_update_func = None
maximize_player_currency_func = None
unlock_and_maximize_characters_func = None

try:
    import Everwing_data as ed_module
    Everwing_data_module = ed_module
    # Assign functions to global Nones so they are definitely set if import works
    compress_to_lz_string_func = ed_module.compress_to_lz_string
    decompress_lz_string_func = ed_module.decompress_lz_string
    parse_json_func = ed_module.parse_json
    serialize_to_json_func = ed_module.serialize_to_json
    prepare_dragons_for_update_func = ed_module.prepare_dragons_for_update
    maximize_player_currency_func = ed_module.maximize_player_currency
    unlock_and_maximize_characters_func = ed_module.unlock_and_maximize_characters
    print("Successfully imported Everwing_data module for testing.")
except ImportError as e_module:
    print("Failed to import Everwing_data module ({}). Trying specific functions...".format(e_module))
    # This fallback is less ideal but provided for robustness in various execution contexts.
    try:
        from Everwing_data import (
            compress_to_lz_string, decompress_lz_string,
            parse_json, serialize_to_json,
            prepare_dragons_for_update,
            maximize_player_currency,
            unlock_and_maximize_characters
        )
        compress_to_lz_string_func = compress_to_lz_string
        decompress_lz_string_func = decompress_lz_string
        parse_json_func = parse_json
        serialize_to_json_func = serialize_to_json
        prepare_dragons_for_update_func = prepare_dragons_for_update
        maximize_player_currency_func = maximize_player_currency
        unlock_and_maximize_characters_func = unlock_and_maximize_characters
        print("Successfully imported specific functions from Everwing_data.")
    except ImportError as e_specific:
        print("Critical: Failed to import any functions from Everwing_data for testing: {}".format(e_specific))
        # Tests will be skipped if functions are not found by the test methods.

class TestEverwingData(unittest.TestCase):

    def test_lz_string_compression_decompress(self):
        """Test that a string can be compressed and then decompressed to its original form."""
        if not compress_to_lz_string_func or not decompress_lz_string_func:
            self.skipTest("LZString functions (compress/decompress) not available for testing.")
        
        original_string = "Hello, Everwing! This is a test string for LZString."
        compressed = compress_to_lz_string_func(original_string)
        self.assertIsNotNone(compressed, "Compression should not return None.")
        self.assertIsInstance(compressed, str, "Compressed output should be a string.")
        
        decompressed = decompress_lz_string_func(compressed)
        self.assertIsNotNone(decompressed, "Decompression should not return None.")
        self.assertEqual(decompressed, original_string, "Decompressed string should match the original.")

    def test_parse_json_valid(self):
        """Test parsing a valid JSON string."""
        if not parse_json_func:
            self.skipTest("parse_json function not available for testing.")
            
        json_string = '{"name": "Test Dragon", "level": 10, "active": true, "value": null}'
        expected_dict = {"name": "Test Dragon", "level": 10, "active": True, "value": None}
        parsed = parse_json_func(json_string)
        self.assertEqual(parsed, expected_dict)

    def test_parse_json_invalid_syntax(self):
        """Test parsing an invalid JSON string (syntax error)."""
        if not parse_json_func:
            self.skipTest("parse_json function not available for testing.")

        json_string = '{"name": "Test Dragon", "level": 10, "active": true,' # Missing closing brace and trailing comma
        parsed = parse_json_func(json_string)
        self.assertIsNone(parsed, "Parsing invalid JSON (syntax error) should return None.")

    def test_parse_json_invalid_type(self):
        """Test parsing a non-string type."""
        if not parse_json_func:
            self.skipTest("parse_json function not available for testing.")
        
        parsed = parse_json_func(12345) # Pass an integer instead of a string
        self.assertIsNone(parsed, "Parsing non-string input should return None.")


    def test_serialize_to_json(self):
        """Test serializing a Python dictionary, expecting double dumps."""
        if not serialize_to_json_func:
            self.skipTest("serialize_to_json function not available for testing.")

        python_dict = {"item": "Dragon Egg", "value": 100, "attributes": None}
        # Expected: dumps(dumps(python_dict))
        expected_inner_json_str = json.dumps(python_dict) 
        expected_outer_json_str = json.dumps(expected_inner_json_str)
        
        serialized = serialize_to_json_func(python_dict)
        self.assertEqual(serialized, expected_outer_json_str)

    def test_prepare_dragons_for_update(self):
        """Test updating dragon maturity and XP values based on corrected logic."""
        if not prepare_dragons_for_update_func:
            self.skipTest("prepare_dragons_for_update function not available for testing.")

        flat_sample_dragons_data = [
            {'Maturity': {'value': 1, 'key': 'm1'}}, 
            {'XP': {'value': 100, 'maximum': 1000, 'key': 'x1'}},
            {'Maturity': {'value': 2, 'key': 'm2'}}, 
            {'XP': {'value': 60000, 'maximum': 62800, 'key': 'x2'}}, # Original L2
            {'Maturity': {'value': 3, 'key': 'm3'}}, 
            {'XP': {'value': 125000, 'maximum': 125800, 'key': 'x3'}} # Original L3
        ]
        
        # Corrected expectation: If maturity becomes 3, XP should be 125800.
        expected_dragons_data = [
            {'Maturity': {'value': 3, 'key': 'm1'}}, # Original L1 -> L3
            {'XP': {'value': 125800, 'maximum': 125800, 'key': 'x1'}}, # XP maxed for L3
            {'Maturity': {'value': 3, 'key': 'm2'}}, # Original L2 -> L3
            {'XP': {'value': 125800, 'maximum': 125800, 'key': 'x2'}}, # XP maxed for new L3
            {'Maturity': {'value': 3, 'key': 'm3'}}, # Original L3 -> L3 (no change)
            {'XP': {'value': 125800, 'maximum': 125800, 'key': 'x3'}}  # XP maxed for L3
        ]
        
        data_to_test = copy.deepcopy(flat_sample_dragons_data)
        updated_dragons = prepare_dragons_for_update_func(data_to_test)
        self.assertEqual(updated_dragons, expected_dragons_data)

    def test_maximize_player_currency(self):
        """Test maximizing coin and trophy currency."""
        if not maximize_player_currency_func:
            self.skipTest("maximize_player_currency function not available for testing.")
            
        sample_state_data = {
            'instances': {
                'currency_coin_1': {'schemaPrimativeID': 'currency:coin', 'balance': 100},
                'currency_trophy_1': {'schemaPrimativeID': 'currency:trophy', 'balance': 5},
                'other_item_1': {'schemaPrimativeID': 'item:other', 'value': 50}
            }
        }
        expected_state_data = {
            'instances': {
                'currency_coin_1': {'schemaPrimativeID': 'currency:coin', 'balance': 999999},
                'currency_trophy_1': {'schemaPrimativeID': 'currency:trophy', 'balance': 999999},
                'other_item_1': {'schemaPrimativeID': 'item:other', 'value': 50}
            }
        }
        state_data_copy = copy.deepcopy(sample_state_data)
        maximize_player_currency_func(state_data_copy)
        self.assertEqual(state_data_copy, expected_state_data)
            
    def test_unlock_and_maximize_characters(self):
        """Test unlocking characters and maximizing their levels."""
        if not unlock_and_maximize_characters_func:
            self.skipTest("unlock_and_maximize_characters function not available for testing.")

        sample_state_data = {
            'instances': {
                'char_lenore': {
                    'schemaPrimativeID': 'character:lenore_item_character', 
                    'state': 'locked',
                    'stats': ['stat_lenore_level']
                },
                'stat_lenore_level': {'schemaPrimativeID': 'stat:level', 'value': 1, 'maximum': 50},
                'char_fiona': {
                    'schemaPrimativeID': 'character:fiona_item_character', 
                    'state': 'idle',
                    'stats': ['stat_fiona_level']
                },
                'stat_fiona_level': {'schemaPrimativeID': 'stat:level', 'value': 25, 'maximum': 50},
                'other_item': {'schemaPrimativeID': 'item:generic'}
            }
        }
        expected_state_data = {
            'instances': {
                'char_lenore': {
                    'schemaPrimativeID': 'character:lenore_item_character', 
                    'state': 'idle', 
                    'stats': ['stat_lenore_level']
                },
                'stat_lenore_level': {'schemaPrimativeID': 'stat:level', 'value': 50, 'maximum': 50},
                'char_fiona': {
                    'schemaPrimativeID': 'character:fiona_item_character', 
                    'state': 'idle', 
                    'stats': ['stat_fiona_level']
                },
                'stat_fiona_level': {'schemaPrimativeID': 'stat:level', 'value': 50, 'maximum': 50},
                'other_item': {'schemaPrimativeID': 'item:generic'}
            }
        }
        state_data_copy = copy.deepcopy(sample_state_data)
        unlock_and_maximize_characters_func(state_data_copy)
        self.assertEqual(state_data_copy, expected_state_data)

if __name__ == '__main__':
    # This allows running the tests directly if the script is executed.
    # Note: The agent uses `python -m unittest test_everwing_data.py` which is preferred.
    unittest.main()
