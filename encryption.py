# encryption.py
# Contains the three cipher algorithms used in the project:
# Caesar, XOR and the Mossab Rotating Cipher (MRC).
# Each function returns the result text and a list of steps so the
# result page can show how the encryption/decryption was done.


# names shown in the menu
ALGORITHMS = {
    "caesar": "Caesar Cipher",
    "xor": "XOR Cipher",
    "mrc": "Mossab Rotating Cipher",
}


# ---------- Caesar Cipher ----------
def caesar_encrypt(text, key):
    key = int(key)
    result = ""
    steps = []
    for ch in text:
        if ch.isupper():
            x = ord(ch) - 65
            new = (x + key) % 26
            new_ch = chr(new + 65)
            result += new_ch
            steps.append(ch + "(" + str(x) + ") -> (" + str(x) + "+" + str(key) + ") mod 26 = " + str(new) + " -> " + new_ch)
        elif ch.islower():
            x = ord(ch) - 97
            new = (x + key) % 26
            new_ch = chr(new + 97)
            result += new_ch
            steps.append(ch + "(" + str(x) + ") -> (" + str(x) + "+" + str(key) + ") mod 26 = " + str(new) + " -> " + new_ch)
        else:
            result += ch
            steps.append(ch + " -> not a letter, kept the same")
    return result, steps


def caesar_decrypt(text, key):
    key = int(key)
    result = ""
    steps = []
    for ch in text:
        if ch.isupper():
            x = ord(ch) - 65
            new = (x - key + 26) % 26
            new_ch = chr(new + 65)
            result += new_ch
            steps.append(ch + "(" + str(x) + ") -> (" + str(x) + "-" + str(key) + "+26) mod 26 = " + str(new) + " -> " + new_ch)
        elif ch.islower():
            x = ord(ch) - 97
            new = (x - key + 26) % 26
            new_ch = chr(new + 97)
            result += new_ch
            steps.append(ch + "(" + str(x) + ") -> (" + str(x) + "-" + str(key) + "+26) mod 26 = " + str(new) + " -> " + new_ch)
        else:
            result += ch
            steps.append(ch + " -> not a letter, kept the same")
    return result, steps


# ---------- XOR Cipher ----------
# XOR is reversible: doing it twice with the same key gives the text back.
def xor_encrypt(text, key):
    key = int(key)
    result = ""
    steps = []
    for ch in text:
        code = ord(ch)
        new = code ^ key
        new_ch = chr(new)
        result += new_ch
        steps.append(ch + " (ASCII " + str(code) + ", " + format(code, "08b") + ") XOR " + str(key) + " = " + str(new) + " (" + format(new, "08b") + ") -> " + new_ch)
    return result, steps


def xor_decrypt(text, key):
    # same operation as encrypt
    return xor_encrypt(text, key)


# ---------- Mossab Rotating Cipher (MRC) ----------
# Encrypt: new ascii = ascii + key + position, then reverse the string.
# Decrypt: reverse the string back, then ascii - key - position.
def mrc_encrypt(text, key):
    key = int(key)
    steps = []

    # step 1 - shift every character
    middle = ""
    for i in range(len(text)):
        ch = text[i]
        new_code = ord(ch) + key + i
        new_ch = chr(new_code)
        middle += new_ch
        steps.append("i=" + str(i) + ": " + ch + "(" + str(ord(ch)) + ") + " + str(key) + " + " + str(i) + " = " + str(new_code) + " -> " + new_ch)

    steps.append("After shifting: " + middle)

    # step 2 - reverse it
    cipher = middle[::-1]
    steps.append("After reversing: " + cipher)

    return cipher, steps


def mrc_decrypt(text, key):
    key = int(key)
    steps = []

    # step 1 - reverse the cipher text first
    reversed_text = text[::-1]
    steps.append("Reversed back: " + reversed_text)

    # step 2 - undo the shift
    result = ""
    for i in range(len(reversed_text)):
        ch = reversed_text[i]
        new_code = ord(ch) - key - i
        new_ch = chr(new_code)
        result += new_ch
        steps.append("i=" + str(i) + ": " + ch + "(" + str(ord(ch)) + ") - " + str(key) + " - " + str(i) + " = " + str(new_code) + " -> " + new_ch)

    steps.append("Decrypted text: " + result)

    return result, steps


# small test to run this file on its own
if __name__ == "__main__":
    print(caesar_encrypt("HELLO", 3))
    print(xor_encrypt("HELLO", 3))
    print(mrc_encrypt("HELLO", 3))
