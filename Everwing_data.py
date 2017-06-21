from ast import literal_eval
from json import dumps, loads
from urllib2 import Request, urlopen
from requests import post, get

from p3lzstring import LZString


def user_input(data):
    i = 0
    while i < len(data):
        if 'xp' in data[i]['dragondata']['sidekick_name'][9:][5:]:
            data[i]['dragondata']['value'] = data[i]['dragondata']['maximum']
            print (data[i]['dragondata']['value'])
        else:
            if 'maturity' in data[i]['dragondata']['sidekick_name'][9:][5:]:
                data[i]['dragondata']['value'] = data[i]['dragondata']['maximum']
                print (data[i]['dragondata']['value'])
        i = i + 1
    return data


def lz_string_decode(lzstring):
    lz_object = LZString.decompressFromBase64(lzstring)
    return lz_object


def dict_loop(p, check_list, scheme_pid):
    i = 0
    while i < len(state_dict['instances']):
        for key in state_dict['instances'].iterkeys():
            if p in key:
                return state_dict['instances'][key]
        i = i + 1
    return 'Found Nothing'


def build_xpmat_list(state_dict):
    i = 0
    while i < len(state_dict['instances']):
        list = []
        for key in state_dict['instances'].iterkeys():
            pg = float((float(i) / float(len(state_dict['instances'])) * float(100)))
            # update_progress(pg)
            schemePID = state_dict['instances'][str(key)]['schemaPrimativeID']
            dict_index = state_dict['instances'][str(key)]
            if 'stats' in dict_index.keys() and 'sidekick' in schemePID:
                check_list = []
                stat_keys = dict_index['stats']
                for stats in stat_keys:
                    data = dict_loop(stats, check_list, schemePID)
                    check_list.append(schemePID)
                    if 'maturity' in data['schemaPrimativeID']:
                        list.append({'Maturity': data})
                    if 'xp' in data['schemaPrimativeID']:
                        list.append({'XP': data})
        i = i + 1
        print "%s / %s" % (i, len(state_dict['instances']))
    return list


def conv2Json(jsonString, *args, **kwargs):
    jsonObject = literal_eval(jsonString)
    return jsonObject


def conv2JsonStr(jsonObject):
    jsonString = dumps(dumps(jsonObject))
    return jsonString


def ever_wing_token():
    req = Request("https://wintermute-151001.appspot.com/game/session/everwing/" + uID)
    response = urlopen(req)
    data = response.read()
    Token = conv2Json(data)
    return Token


def ever_wing_defaultaction():
    return


def lz_string_encode(object):
    lzObject = LZString.compressToBase64(object)
    print (lzObject)
    return lzObject


def default_state():
    url = 'https://wintermute-151001.appspot.com'
    gamestate_url = '/game/state/everwing/default/' + uID
    state = get(url + gamestate_url)
    return state.content


def post_to_winter(user_data, Token):
    user_data = unicode(user_data)
    headers = {"Host": "wintermute-151001.appspot.com",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
               "Accept": "application/json, text/plain, */*",
               "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate, br",
               "Content-Type": "application/json;charset=utf-8",
               "x-wintermute-session": str(Token['token']),
               "Connection": "keep-alive"}

    print (user_data)
    print (headers)
    post_data = post('https://wintermute-151001.appspot.com/game/action', data=user_data, headers=headers)
    return


def rebuild_loop(p, list, x, maturity, XP):
    i = 0
    if maturity == 'Maturity':
        while i < len(state_dict):
            for key in state_dict['instances'].iterkeys():
                if p in key:
                    state_dict['instances'][key] = list[x][maturity]
            i = i + 1
    if XP == 'XP':
        while i < len(state_dict):

            for key in state_dict['instances'].iterkeys():
                if p in key:
                    state_dict['instances'][key] = list[x][XP]
            i = i + 1
    return 'THIS IS IT'


def build_state_dict(list):
    i = 0
    while i < len(list):
        try:
            if list[i]["Maturity"]:
                key_index = list[i]['Maturity']['key']
                rebuild_loop(key_index, list, i, maturity='Maturity', XP=2)
                pass
        except KeyError:
            if list[i]['XP']:
                key_index = list[i]['XP']['key']
                rebuild_loop(key_index, list, i, XP='XP', maturity=3)

        i = i + 1
        print '%s / %s' % (i, len(list))
    return


def fuck_dat_currency():
    for instance in state_dict['instances']:

        try:
            if state_dict['instances'][instance]['schemaPrimativeID'] == "currency:trophy":
                state_dict['instances'][instance]['balance'] = 999999
            if state_dict['instances'][instance]['schemaPrimativeID'] == "currency:coin":
                state_dict['instances'][instance]['balance'] = 999999
        except Exception as e:
            print "%s" % e
    return


def rebuild_state(list, state_dict):
    i = 0
    while i < len(list):
        if list[i]['Maturity']['value']:
            list[i]['Maturity']['value'] = 3
        if list[i]['Maturity']['value'] == 3:
            list[i + 1]['XP']['value'] = 125800
            list[i + 1]['XP']['maximum'] = 125800
        if list[i]['Maturity']['value'] == 2:
            list[i + 1]['XP']['value'] = 62800
            list[i + 1]['XP']['maximum'] = 62800
        if list[i]['Maturity']['value'] == 1:
            list[i + 1]['XP']['value'] = 62800
            list[i + 1]['XP']['maximum'] = 62800
        i = i + 2
    return list


def get_dat_toonies():
    characterStrings = ['character:lenore_item_character', 'character:coin_item_character',
                        'character:sophia_item_character', 'character:jade_item_character',
                        'character:arcana_item_character', 'character:fiona_item_character',
                        'character:standard_item_character', 'character:magnet_item_character']
    for instance in state_dict['instances']:
        try:
            if state_dict['instances'][instance]['schemaPrimativeID'] in characterStrings:
                characterStat = state_dict['instances'][instance]['stats'][0]
                state_dict['instances'][characterStat]['value'] = state_dict['instances'][characterStat]['maximum']
                if state_dict['instances'][instance]['state'] == 'locked':
                    state_dict['instances'][instance]['state'] = 'idle'
        except Exception:
            print (Exception.message)
    return


if __name__ == '__main__':
    uID = raw_input('Please Input User ID: ')
    user_data = loads(default_state())
    state = user_data['state'][11:]
    print (state)
    state = lz_string_decode(str(state))
    state_json_str = conv2Json(state)
    state_dict = loads(state_json_str)
    input = raw_input('Do you wanna upgrade all current Dragons? (Y/n)')
    if input == 'Y':
        build_state_dict(rebuild_state(build_xpmat_list(state_dict), state_dict))
    else:
        print('-------------------------------')
        print("You must enter a 'Y' or 'n'!!")
        print('-------------------------------')

    input = raw_input('Do you wanna fuck da currency? (Y/n)')
    if input == 'Y':
        fuck_dat_currency()
    else:
        print('-------------------------------')
        print("You must enter a 'Y' or 'n'!!")
        print('-------------------------------')

    input = raw_input('Do you want all Characters / level 50? (Y/N)')
    if input == 'Y':
        get_dat_toonies()
    else:
        print('-------------------------------')
        print("You must enter a 'Y' or 'n'!!")
        print('-------------------------------')
    a = open('statefile.txt', 'w')
    a.write(dumps(state_dict, sort_keys=True, indent=4))
    a.close()
    state_dict = conv2JsonStr(state_dict)
    encoded_state = lz_string_encode(state_dict)
    encoded_state = 'lz-string::' + encoded_state
    user_data['state'] = encoded_state
    user_data['timestamp'] = round(float(get('https://wintermute-151001.appspot.com/game/time').content),
                                   ndigits=0)
    user_data['server_timestamp'] = round(
        float(get('https://wintermute-151001.appspot.com/game/time').content), ndigits=0)
    user_data = dumps(user_data)
    post_to_winter(user_data, ever_wing_token())
    print(user_data)
