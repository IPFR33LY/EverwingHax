# coding=utf-8
"""
Copyright 2017 Marcel Dancak <dancakm@gmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.
"""

import math


keyStrBase64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
keyStrUriSafe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"
baseReverseDic = {}


class Object(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def getBaseValue(alphabet, character):
    if alphabet not in baseReverseDic:
        baseReverseDic[alphabet] = {}
        for i in range(len(alphabet)):  # Added space around `in`
            baseReverseDic[alphabet][alphabet[i]] = i
    return baseReverseDic[alphabet][character]


def _compress(uncompressed, bitsPerChar, getCharFromInt):
    if uncompressed is None:  # Changed `(uncompressed is None)` to `uncompressed is None`
        return ""

    context_dictionary = {}
    context_dictionaryToCreate = {}
    context_c = ""
    context_wc = ""
    context_w = ""
    context_enlargeIn = 2  # Compensate for the first entry which should not count
    context_dictSize = 3
    context_numBits = 2
    context_data = []
    context_data_val = 0
    context_data_position = 0

    for ii in range(len(uncompressed)):
        context_c = uncompressed[ii]
        if context_c not in context_dictionary:
            context_dictionary[context_c] = context_dictSize
            context_dictSize += 1
            context_dictionaryToCreate[context_c] = True

        context_wc = context_w + context_c
        if context_wc in context_dictionary:
            context_w = context_wc
        else:
            if context_w in context_dictionaryToCreate:
                if ord(context_w[0]) < 256:
                    for i in range(context_numBits):
                        context_data_val = (context_data_val << 1)
                        if context_data_position == bitsPerChar - 1:
                            context_data_position = 0
                            context_data.append(getCharFromInt(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                    value = ord(context_w[0])
                    for i in range(8):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bitsPerChar - 1:
                            context_data_position = 0
                            context_data.append(getCharFromInt(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1
                else:
                    value = 1
                    for i in range(context_numBits):
                        context_data_val = (context_data_val << 1) | value
                        if context_data_position == bitsPerChar - 1:
                            context_data_position = 0
                            context_data.append(getCharFromInt(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = 0  # Reset value for next iteration
                    value = ord(context_w[0])
                    for i in range(16):
                        context_data_val = (context_data_val << 1) | (value & 1)
                        if context_data_position == bitsPerChar - 1:
                            context_data_position = 0
                            context_data.append(getCharFromInt(context_data_val))
                            context_data_val = 0
                        else:
                            context_data_position += 1
                        value = value >> 1
                context_enlargeIn -= 1
                if context_enlargeIn == 0:
                    context_enlargeIn = math.pow(2, context_numBits)
                    context_numBits += 1
                del context_dictionaryToCreate[context_w]
            else:
                value = context_dictionary[context_w]
                for i in range(context_numBits):
                    context_data_val = (context_data_val << 1) | (value & 1)
                    if context_data_position == bitsPerChar - 1:
                        context_data_position = 0
                        context_data.append(getCharFromInt(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                    value = value >> 1

            context_enlargeIn -= 1
            if context_enlargeIn == 0:
                context_enlargeIn = math.pow(2, context_numBits)
                context_numBits += 1

            # Add wc to the dictionary.
            context_dictionary[context_wc] = context_dictSize
            context_dictSize += 1
            context_w = str(context_c)

    # Output the code for w.
    if context_w != "":
        if context_w in context_dictionaryToCreate:
            if ord(context_w[0]) < 256:
                for i in range(context_numBits):
                    context_data_val = (context_data_val << 1)
                    if context_data_position == bitsPerChar - 1:
                        context_data_position = 0
                        context_data.append(getCharFromInt(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                value = ord(context_w[0])
                for i in range(8):
                    context_data_val = (context_data_val << 1) | (value & 1)
                    if context_data_position == bitsPerChar - 1:
                        context_data_position = 0
                        context_data.append(getCharFromInt(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                    value = value >> 1
            else:
                value = 1
                for i in range(context_numBits):
                    context_data_val = (context_data_val << 1) | value
                    if context_data_position == bitsPerChar - 1:
                        context_data_position = 0
                        context_data.append(getCharFromInt(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                    value = 0  # Reset value for next iteration
                value = ord(context_w[0])
                for i in range(16):
                    context_data_val = (context_data_val << 1) | (value & 1)
                    if context_data_position == bitsPerChar - 1:
                        context_data_position = 0
                        context_data.append(getCharFromInt(context_data_val))
                        context_data_val = 0
                    else:
                        context_data_position += 1
                    value = value >> 1
            context_enlargeIn -= 1
            if context_enlargeIn == 0:
                context_enlargeIn = math.pow(2, context_numBits)
                context_numBits += 1
            del context_dictionaryToCreate[context_w]
        else:
            value = context_dictionary[context_w]
            for i in range(context_numBits):
                context_data_val = (context_data_val << 1) | (value & 1)
                if context_data_position == bitsPerChar - 1:
                    context_data_position = 0
                    context_data.append(getCharFromInt(context_data_val))
                    context_data_val = 0
                else:
                    context_data_position += 1
                value = value >> 1

        context_enlargeIn -= 1
        if context_enlargeIn == 0:
            # context_enlargeIn = math.pow(2, context_numBits) # Original line
            context_enlargeIn = int(math.pow(2, context_numBits)) # Ensure integer for range
            context_numBits += 1

    # Mark the end of the stream
    value = 2
    for i in range(context_numBits):
        context_data_val = (context_data_val << 1) | (value & 1)
        if context_data_position == bitsPerChar - 1:
            context_data_position = 0
            context_data.append(getCharFromInt(context_data_val))
            context_data_val = 0
        else:
            context_data_position += 1
        value = value >> 1

    # Flush the last char
    while True:
        context_data_val = (context_data_val << 1)
        if context_data_position == bitsPerChar - 1:
            context_data.append(getCharFromInt(context_data_val))
            break
        else:
            context_data_position += 1

    return "".join(context_data)


def _decompress(length, resetValue, getNextValue):
    dictionary = {}  # Changed from list to dict for clarity, though list was used as map
    enlargeIn = 4
    dictSize = 4
    numBits = 3
    entry = ""
    result = []

    data = Object(
        val=getNextValue(0),
        position=resetValue,
        index=1
    )

    for i in range(3): # Initialize dictionary with first 3 values
        dictionary[i] = chr(i) # Store characters, not integers, if these are char codes

    bits = 0
    maxpower = int(math.pow(2, 2)) # Ensure integer for range
    power = 1

    while power != maxpower:
        resb = data.val & data.position
        data.position >>= 1
        if data.position == 0:
            data.position = resetValue
            data.val = getNextValue(data.index)
            data.index += 1
        if resb > 0: # Simplified bit setting
            bits |= power
        power <<= 1

    next_val = bits  # Renamed from `next` as it's a keyword
    if next_val == 0:
        bits = 0
        maxpower = int(math.pow(2, 8)) # Ensure integer
        power = 1
        while power != maxpower:
            resb = data.val & data.position
            data.position >>= 1
            if data.position == 0:
                data.position = resetValue
                data.val = getNextValue(data.index)
                data.index += 1
            if resb > 0:
                bits |= power
            power <<= 1
        c = chr(bits)
    elif next_val == 1:
        bits = 0
        maxpower = int(math.pow(2, 16)) # Ensure integer
        power = 1
        while power != maxpower:
            resb = data.val & data.position
            data.position >>= 1
            if data.position == 0:
                data.position = resetValue
                data.val = getNextValue(data.index)
                data.index += 1
            if resb > 0:
                bits |= power
            power <<= 1
        c = chr(bits)
    elif next_val == 2:
        return ""

    dictionary[3] = c
    w = c
    result.append(c)
    # counter = 0 # Original counter, seems unused for logic
    while True:
        # counter += 1 # Original counter
        if data.index > length: # Check if data index exceeds length
            return ""

        bits = 0
        maxpower = int(math.pow(2, numBits)) # Ensure integer
        power = 1
        while power != maxpower:
            resb = data.val & data.position
            data.position >>= 1
            if data.position == 0:
                data.position = resetValue
                data.val = getNextValue(data.index)
                data.index += 1
            if resb > 0:
                bits |= power
            power <<= 1
        
        c_val = bits # Renamed c to c_val to avoid conflict with previous c

        if c_val == 0:
            bits = 0
            maxpower = int(math.pow(2, 8)) # Ensure integer
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = resetValue
                    data.val = getNextValue(data.index)
                    data.index += 1
                if resb > 0:
                    bits |= power
                power <<= 1

            dictionary[dictSize] = chr(bits)
            dictSize += 1
            c_val = dictSize - 1
            enlargeIn -= 1
        elif c_val == 1:
            bits = 0
            maxpower = int(math.pow(2, 16)) # Ensure integer
            power = 1
            while power != maxpower:
                resb = data.val & data.position
                data.position >>= 1
                if data.position == 0:
                    data.position = resetValue
                    data.val = getNextValue(data.index)
                    data.index += 1
                if resb > 0:
                    bits |= power
                power <<= 1
            dictionary[dictSize] = chr(bits)
            dictSize += 1
            c_val = dictSize - 1
            enlargeIn -= 1
        elif c_val == 2:
            return "".join(result)

        if enlargeIn == 0:
            enlargeIn = int(math.pow(2, numBits)) # Ensure integer
            numBits += 1

        if c_val in dictionary:
            entry = dictionary[c_val]
        else:
            if c_val == dictSize:
                entry = w + w[0]
            else:
                return None  # Error condition
        result.append(entry)

        # Add w + entry[0] to the dictionary.
        dictionary[dictSize] = w + entry[0]
        dictSize += 1
        enlargeIn -= 1

        w = entry
        if enlargeIn == 0:
            enlargeIn = int(math.pow(2, numBits)) # Ensure integer
            numBits += 1


class LZString(object):
    @staticmethod
    def compress(uncompressed):
        return _compress(uncompressed, 16, chr)

    @staticmethod
    def compressToUTF16(uncompressed):
        if uncompressed is None:
            return ""
        return _compress(uncompressed, 15, lambda a: chr(a + 32)) + " "

    @staticmethod
    def compressToBase64(uncompressed):
        if uncompressed is None:
            return ""
        res = _compress(uncompressed, 6, lambda a: keyStrBase64[a])
        # To produce valid Base64
        end = len(res) % 4
        # print(end) # Removed debug print
        if end > 0:
            res += "=" * (4 - end)
        return res

    @staticmethod
    def compressToEncodedURIComponent(uncompressed):
        if uncompressed is None:
            return ""
        return _compress(uncompressed, 6, lambda a: keyStrUriSafe[a])

    @staticmethod
    def decompress(compressed):
        if compressed is None:
            return ""
        if compressed == "":
            return None  # Or raise an error, depending on expected behavior
        return _decompress(len(compressed), 32768, lambda index: ord(compressed[index]))

    @staticmethod
    def decompressFromUTF16(compressed):
        if compressed is None:
            return ""
        if compressed == "":
            return None
        # Ensure lambda returns int, original was `compressed[index] - 32`
        # but `compressed[index]` is char, so `ord(compressed[index]) - 32`
        return _decompress(len(compressed), 16384, lambda index: ord(compressed[index]) - 32)


    @staticmethod
    def decompressFromBase64(compressed):
        if compressed is None:
            return ""
        if compressed == "":
            return None
        # Assuming getBaseValue returns an int
        return _decompress(len(compressed), 32, lambda index: getBaseValue(keyStrBase64, compressed[index]))

    @staticmethod
    def decompressFromEncodedURIComponent(compressed):
        if compressed is None:
            return ""
        if compressed == "":
            return None
        compressed = compressed.replace(" ", "+")
        # Assuming getBaseValue returns an int
        return _decompress(len(compressed), 32, lambda index: getBaseValue(keyStrUriSafe, compressed[index]))

# Add two blank lines before top-level functions and class definitions (PEP 8)
# (Manual check - already seems mostly compliant here or handled by structure)

# Add one blank line before method definitions within a class (PEP 8)
# (Manual check - already seems mostly compliant here or handled by structure)
