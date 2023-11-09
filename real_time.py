import urllib.parse
code = input("Enter the code: ")
def decode_auth_code(code):
    return urllib.parse.unquote(code)

print(decode_auth_code(code))