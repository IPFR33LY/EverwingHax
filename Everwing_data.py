# -*- coding: utf-8 -*-
"""
Everwing_data.py

This script interacts with the Everwing game's backend to modify game state.
It allows users to perform actions such as upgrading dragons, maximizing currency,
and unlocking characters.

Compatibility: Python 2.7 / Python 3 (after modifications)
"""

from ast import literal_eval # Still used by get_everwing_session_token if response isn't direct JSON.
from json import dumps, loads
import json # Added for json.loads and json.JSONDecodeError
import requests

from p3lzstring import LZString

# --- Global Constants ---
BASE_URL = "https://wintermute-151001.appspot.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
DEFAULT_TIMEOUT = 15 # seconds for requests

USER_ID = None # To be set by user input at runtime

# --- Helper Functions ---

def decompress_lz_string(lz_encoded_string):
    """
    Decompresses a Base64 encoded LZString.
    """
    try:
        return LZString.decompressFromBase64(lz_encoded_string)
    except Exception as e:
        print("Error: Failed to decompress LZString: {}".format(e))
        return None

def compress_to_lz_string(data_string):
    """
    Compresses a string using LZString and encodes it to Base64.
    """
    try:
        compressed = LZString.compressToBase64(data_string)
        return compressed
    except Exception as e:
        print("Error: Failed to compress to LZString: {}".format(e))
        return None

def parse_json(json_string):
    """
    Parses a JSON string into a Python object using json.loads().
    This is safer and more standard for JSON parsing than literal_eval.
    """
    try:
        return json.loads(json_string) # Changed from literal_eval
    except (json.JSONDecodeError, TypeError) as e: # TypeError if json_string is not string-like
        print("Error: Failed to parse JSON string: {}. String was: {}".format(e, str(json_string)[:100]))
        return None

def serialize_to_json(python_object):
    """
    Serializes a Python object into a JSON string.
    The object is first dumped to a JSON string, then that string itself is dumped.
    This double serialization is specific to the expected format by the Everwing game server.
    """
    try:
        return dumps(dumps(python_object))
    except TypeError as e:
        print("Error: Failed to serialize object to JSON: {}".format(e))
        return None

# --- Game Interaction Functions ---

def get_request(url, timeout=DEFAULT_TIMEOUT):
    """Wrapper for requests.get with error handling and timeout."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        print("Error: HTTP error for URL {}: {}".format(url, e))
    except requests.exceptions.Timeout as e:
        print("Error: Request timed out for URL {}: {}".format(url, e))
    except requests.exceptions.RequestException as e:
        print("Error: Request failed for URL {}: {}".format(url, e))
    return None

def post_request(url, data, headers, timeout=DEFAULT_TIMEOUT):
    """Wrapper for requests.post with error handling and timeout."""
    try:
        response = requests.post(url, data=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        print("Error: HTTP error for URL {}: {} - Response: {}".format(url, e, response.content if response else 'N/A'))
    except requests.exceptions.Timeout as e:
        print("Error: Request timed out for URL {}: {}".format(url, e))
    except requests.exceptions.RequestException as e:
        print("Error: Request failed for URL {}: {}".format(url, e))
    return None


def get_everwing_session_token(user_identifier):
    session_url = "{}/game/session/everwing/{}".format(BASE_URL, user_identifier)
    print("Fetching session token from: {}".format(session_url))
    response = get_request(session_url)
    if response:
        try:
            # The original game client might have used literal_eval if the server
            # sometimes returned non-strict JSON. Sticking to response.json() for now.
            token_data = response.json() 
            return token_data
        except json.JSONDecodeError as e: 
            print("Error: Could not decode JSON response for session token: {}".format(e))
            print("Response content: {}".format(response.text))
            # Fallback to literal_eval if direct JSON parsing fails, as per original parse_json's intent.
            # This is a concession to potential non-standard server responses.
            print("Attempting fallback parsing with literal_eval for session token...")
            try:
                token_data_fallback = literal_eval(response.text)
                print("Fallback parsing successful.")
                return token_data_fallback
            except (ValueError, SyntaxError) as eval_e:
                print("Error: Fallback parsing with literal_eval also failed: {}".format(eval_e))
                return None
    return None


def get_default_game_state(user_identifier):
    game_state_url = "{}/game/state/everwing/default/{}".format(BASE_URL, user_identifier)
    print("Fetching default game state from: {}".format(game_state_url))
    response = get_request(game_state_url)
    return response.content if response else None


def get_current_server_time():
    time_url = "{}/game/time".format(BASE_URL)
    response = get_request(time_url)
    if response:
        try:
            return round(float(response.content), ndigits=0)
        except ValueError as e:
            print("Error: Could not parse server time: {}. Content: {}".format(e, response.content))
    return None


def post_data_to_wintermute(payload_data, session_token_str):
    action_url = "{}/game/action".format(BASE_URL)
    headers = {
        "Host": "wintermute-151001.appspot.com",
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br", 
        "Content-Type": "application/json;charset=utf-8",
        "x-wintermute-session": session_token_str,
        "Connection": "keep-alive"
    }
    print("Posting data to Wintermute server at: {}".format(action_url))
    response = post_request(action_url, data=unicode(payload_data) if sys.version_info[0] < 3 else str(payload_data), headers=headers)
    if response:
        print("Post to Wintermute successful. Server response: {}".format(response.content[:200]))
    else:
        print("Failed to post data to Wintermute.")
        print("Request payload (first 100 chars): {}".format(str(payload_data)[:100]))
        print("Request headers: {}".format(headers))


# --- Game Logic Modification Functions ---

def find_instance_by_key_substring(state_data, target_substring):
    if 'instances' not in state_data:
        print("Warning: 'instances' key not found in state_data for find_instance_by_key_substring.")
        return 'Found Nothing'
    # Changed iteritems() to items() for Python 3 compatibility
    for key, instance_data in state_data['instances'].items(): 
        if target_substring in key:
            return instance_data
    return 'Found Nothing'

def build_xp_maturity_list(state_data):
    xp_maturity_items = []
    if 'instances' not in state_data:
        print("Warning: 'instances' key not found in state_data for build_xp_maturity_list.")
        return xp_maturity_items

    # Changed iteritems() to items()
    for key, instance_data in state_data['instances'].items():
        schema_primitive_id = instance_data.get('schemaPrimativeID', '')
        if instance_data.get('stats') and 'sidekick' in schema_primitive_id:
            for stat_key in instance_data['stats']:
                related_stat_data = find_instance_by_key_substring(state_data, stat_key)
                if related_stat_data != 'Found Nothing':
                    stat_schema_id = related_stat_data.get('schemaPrimativeID', '')
                    if 'maturity' in stat_schema_id:
                        xp_maturity_items.append({'Maturity': related_stat_data})
                    elif 'xp' in stat_schema_id:
                        xp_maturity_items.append({'XP': related_stat_data})
    return xp_maturity_items

def prepare_dragons_for_update(dragon_list_data):
    if not dragon_list_data or len(dragon_list_data) % 2 != 0:
        print("Warning: dragon_list_data is empty or has an odd number of items. Cannot process pairs.")
        return dragon_list_data

    for i in range(0, len(dragon_list_data), 2):
        maturity_item = dragon_list_data[i]
        xp_item = dragon_list_data[i+1]

        if 'Maturity' not in maturity_item or not isinstance(maturity_item['Maturity'], dict):
            print("Warning: Invalid Maturity data at index {}.".format(i))
            continue
        if 'XP' not in xp_item or not isinstance(xp_item['XP'], dict):
            print("Warning: Invalid XP data at index {}.".format(i+1))
            continue

        maturity_data = maturity_item['Maturity']
        xp_data = xp_item['XP']

        if maturity_data.get('value') is not None:
            original_maturity_value = maturity_data['value']
            maturity_data['value'] = 3 # Max maturity

            # Corrected logic: If new maturity is 3, XP should be max for level 3 (125800)
            if maturity_data['value'] == 3:
                xp_data['value'] = 125800
                xp_data['maximum'] = 125800
            # This part of the original logic might be redundant if the above covers all cases for new L3
            # elif original_maturity_value == 3:
            #     xp_data['value'] = 125800
            #     xp_data['maximum'] = 125800
            # elif original_maturity_value == 2: # Dragon was L2, now L3
            #     xp_data['value'] = 125800 # Max XP for new max maturity
            #     xp_data['maximum'] = 125800
            # elif original_maturity_value == 1: # Dragon was L1, now L3
            #     xp_data['value'] = 125800 # Max XP for new max maturity
            #     xp_data['maximum'] = 125800
            else: # Should not be reached if maturity_data['value'] is always set to 3 above.
                  # However, to be safe, ensure max XP if it ends up here.
                 xp_data['value'] = 125800
                 xp_data['maximum'] = 125800
    return dragon_list_data


def update_state_data_from_list(processed_dragon_list, state_data):
    if 'instances' not in state_data:
        print("Warning: 'instances' key not found in state_data for update_state_data_from_list.")
        return

    for item_data in processed_dragon_list:
        if "Maturity" in item_data and isinstance(item_data["Maturity"], dict) and 'key' in item_data["Maturity"]:
            key_to_update = item_data['Maturity']['key']
            if key_to_update in state_data['instances']:
                state_data['instances'][key_to_update] = item_data['Maturity']
            else:
                print("Warning: Key '{}' for Maturity update not found in state_data instances.".format(key_to_update))
        elif "XP" in item_data and isinstance(item_data["XP"], dict) and 'key' in item_data["XP"]:
            key_to_update = item_data['XP']['key']
            if key_to_update in state_data['instances']:
                state_data['instances'][key_to_update] = item_data['XP']
            else:
                print("Warning: Key '{}' for XP update not found in state_data instances.".format(key_to_update))


def maximize_player_currency(state_data):
    if 'instances' not in state_data:
        print("Warning: 'instances' key not found in state_data for maximize_player_currency.")
        return

    updated_count = 0
    # Changed iteritems() to items()
    for instance_id, instance_content in state_data['instances'].items(): 
        try:
            schema_id = instance_content.get('schemaPrimativeID', '')
            if schema_id == "currency:trophy" or schema_id == "currency:coin":
                instance_content['balance'] = 999999
                updated_count +=1
        except TypeError:
             print("Warning: Invalid instance_content for ID {} in maximize_player_currency.".format(instance_id))
    if updated_count > 0:
        print("Maximized currency for {} items.".format(updated_count))
    else:
        print("No currency items found to maximize.")


def unlock_and_maximize_characters(state_data):
    character_schema_ids = [
        'character:lenore_item_character', 'character:coin_item_character',
        'character:sophia_item_character', 'character:jade_item_character',
        'character:arcana_item_character', 'character:fiona_item_character',
        'character:standard_item_character', 'character:magnet_item_character'
    ]
    if 'instances' not in state_data:
        print("Warning: 'instances' key not found in state_data for unlock_and_maximize_characters.")
        return

    updated_char_count = 0
    # Changed iteritems() to items()
    for instance_id, instance_content in state_data['instances'].items():
        try:
            if not isinstance(instance_content, dict):
                print("Warning: Instance {} is not a dictionary.".format(instance_id))
                continue

            schema_id = instance_content.get('schemaPrimativeID', '')
            if schema_id in character_schema_ids:
                updated_char_count +=1
                if instance_content.get('state') == 'locked':
                    instance_content['state'] = 'idle'
                    print("Unlocked character: {}".format(schema_id))

                if instance_content.get('stats') and len(instance_content['stats']) > 0:
                    character_stat_key = instance_content['stats'][0]
                    if character_stat_key in state_data['instances'] and \
                       isinstance(state_data['instances'][character_stat_key], dict):
                        stat_instance = state_data['instances'][character_stat_key]
                        stat_instance['value'] = stat_instance.get('maximum', 50)
                        print("Maximized level for character: {}".format(schema_id))
                    else:
                        print("Warning: Stat key '{}' for {} not found or invalid in instances.".format(character_stat_key, schema_id))
        except TypeError:
             print("Warning: Invalid instance_content for ID {} in unlock_and_maximize_characters.".format(instance_id))
        except KeyError as e:
            print("Warning: Missing key {} for instance {} in unlock_and_maximize_characters.".format(e, instance_id))
    if updated_char_count > 0:
        print("Processed {} characters for unlocking/maximization.".format(updated_char_count))
    else:
        print("No characters found to unlock/maximize.")

# Python 2/3 compatibility for raw_input and unicode
import sys
if sys.version_info[0] < 3:
    input_func = raw_input
    unicode_func = unicode
else:
    input_func = input
    unicode_func = str

# --- Main Execution Block ---

def get_user_input_for_actions():
    choices = {}
    choices['upgrade_dragons'] = input_func('Do you want to upgrade all current Dragons to max? (Y/n): ').strip().upper() == 'Y'
    choices['maximize_currency'] = input_func('Do you want to maximize currency (coins and trophies)? (Y/n): ').strip().upper() == 'Y'
    choices['unlock_characters'] = input_func('Do you want to unlock all characters and maximize their levels? (Y/n): ').strip().upper() == 'Y'
    return choices

def process_game_modifications(state_data, choices):
    if choices.get('upgrade_dragons'):
        print("\nStarting dragon upgrade process...")
        xp_mat_list = build_xp_maturity_list(state_data)
        if xp_mat_list:
            prepared_dragons = prepare_dragons_for_update(xp_mat_list)
            update_state_data_from_list(prepared_dragons, state_data)
            print("Dragon upgrade process complete.")
        else:
            print("No dragon data found or suitable for upgrade.")
    else:
        print("\nSkipping dragon upgrades.")

    if choices.get('maximize_currency'):
        print("\nStarting currency maximization...")
        maximize_player_currency(state_data)
        print("Currency maximization complete.")
    else:
        print("\nSkipping currency maximization.")

    if choices.get('unlock_characters'):
        print("\nStarting character unlocking and maximization...")
        unlock_and_maximize_characters(state_data)
        print("Character unlocking and maximization complete.")
    else:
        print("\nSkipping character modifications.")


def load_and_decode_state(raw_state_content):
    try:
        # Ensure raw_state_content is a string before loading
        if not isinstance(raw_state_content, (str, bytes)): # bytes for Py3 if it's binary
             print("Error: Raw state content is not a string or bytes.")
             return None, None
        initial_user_data = loads(raw_state_content)
    except (json.JSONDecodeError, TypeError) as e:
        print("Error: Could not parse initial raw state content as JSON: {}".format(e))
        return None, None

    encoded_game_state_str = initial_user_data.get('state', '')
    if not encoded_game_state_str.startswith('lz-string::'):
        print("Error: Game state is not in the expected 'lz-string::' format.")
        return initial_user_data, None
    
    actual_encoded_state = encoded_game_state_str[11:]
    decompressed_state_str = decompress_lz_string(str(actual_encoded_state))
    if not decompressed_state_str:
        print("Error: Failed to decompress game state string.")
        return initial_user_data, None

    # The decompressed state is a JSON string, which needs to be parsed again.
    # This was previously parse_json, now directly using json.loads for the inner structure.
    try:
        state_data_json_representation = json.loads(decompressed_state_str)
    except (json.JSONDecodeError, TypeError) as e:
        print("Error: Failed to parse decompressed game state (json_representation) into JSON object: {}".format(e))
        return initial_user_data, None
    
    # This final loads was likely the one failing if state_data_json_representation was already a dict
    # If state_data_json_representation is the actual dict, no further loads needed.
    # The original code had: state_data = loads(state_data_json_representation)
    # This implies state_data_json_representation was expected to be a *string* that is valid JSON,
    # which is what parse_json (using literal_eval) would have handled differently from json.loads.
    # Given the double serialization in serialize_to_json, the decompressed_state_str is
    # a string representing another JSON string. So, first json.loads on decompressed_state_str
    # gets the inner JSON string. Second json.loads gets the actual dict.
    try:
        state_data = json.loads(state_data_json_representation) 
        return initial_user_data, state_data
    except (json.JSONDecodeError, TypeError) as e: # If state_data_json_representation is not a string.
        # This case implies state_data_json_representation was already the dictionary.
        if isinstance(state_data_json_representation, dict):
            print("Info: state_data_json_representation was already a dict.")
            return initial_user_data, state_data_json_representation
        print("Error: Could not load final state_data from JSON representation: {}".format(e))
        return initial_user_data, None


def main():
    global USER_ID

    USER_ID = input_func('Please Input User ID: ')
    if not USER_ID:
        print("Error: User ID cannot be empty. Exiting.")
        return

    print("\n--- Step 1: Fetching Default Game State ---")
    raw_state_content = get_default_game_state(USER_ID)
    if not raw_state_content:
        print("Error: Failed to fetch game state. Exiting.")
        return

    print("\n--- Step 2: Decoding Game State ---")
    initial_user_data, state_data = load_and_decode_state(raw_state_content)
    if state_data is None:
        print("Error: Could not load or decode game state. Exiting.")
        return

    print("\n--- Step 3: User Choices for Modifications ---")
    user_choices = get_user_input_for_actions()

    print("\n--- Step 4: Processing Game Modifications ---")
    process_game_modifications(state_data, user_choices)

    print("\n--- Step 5: Saving Modified State (Backup) ---")
    try:
        with open('statefile_modified.txt', 'w') as f:
            f.write(dumps(state_data, sort_keys=True, indent=4))
        print("Modified state data backed up to statefile_modified.txt")
    except IOError as e:
        print("Error: Could not write modified state file: {}".format(e))

    print("\n--- Step 6: Preparing Final Payload ---")
    final_state_json_string = serialize_to_json(state_data)
    if not final_state_json_string:
        print("Error: Failed to serialize final state data. Exiting.")
        return

    final_encoded_state = compress_to_lz_string(final_state_json_string)
    if not final_encoded_state:
        print("Error: Failed to compress final state data. Exiting.")
        return
        
    initial_user_data['state'] = 'lz-string::' + final_encoded_state
    
    server_time = get_current_server_time()
    if server_time is not None:
        initial_user_data['timestamp'] = server_time
        initial_user_data['server_timestamp'] = server_time
    else:
        print("Warning: Could not fetch server time. Timestamps might be incorrect or missing.")
        initial_user_data['timestamp'] = round(0.0) 
        initial_user_data['server_timestamp'] = round(0.0)

    try:
        final_payload_to_post = dumps(initial_user_data)
    except TypeError as e:
        print("Error: Failed to dump final payload: {}. Exiting.".format(e))
        return

    print("\n--- Step 7: Posting Updated Data ---")
    session_token_data = get_everwing_session_token(USER_ID)
    if not session_token_data or 'token' not in session_token_data:
        print("Error: Failed to get valid session token. Cannot post changes. Exiting.")
        return
    
    post_data_to_wintermute(final_payload_to_post, str(session_token_data['token']))
    
    print("\n-------------------------------")
    print("Script finished.")

if __name__ == '__main__':
    main()
    print("Exiting program.")
