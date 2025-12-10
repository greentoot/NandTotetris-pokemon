def print_ascii_codes(input_string):
    input_string_modif = (input_string.replace(" ", "")).replace(".", "").replace(":", "").replace("-", "").replace("!", "").replace("'", "")
    print(f'function void print{input_string_modif}()',end="")
    print("{")
    for char in input_string:
        print("     ",end=" ")
        print(f"do Output.printChar({ord(char)});")
    print("return;")
    print("}" )
    print("")


print_ascii_codes("Le cocotier s'anime !")

