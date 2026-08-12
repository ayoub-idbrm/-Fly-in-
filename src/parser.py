from pydantic import BaseModel
import sys
import re


class ParsingError(Exception):
    """raise an error in with catch it in the parsing"""
    pass



class Parsing():


    def read_file(self, path):
        data = []
        try:
            with open(path) as file:
                content = file.read()
                if not content:
                    print("ERROR: the file is empty ")
                    sys.exit()
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    data.append(line)

        except OSError as e:
            raise ParsingError(f"failed to open '{path}: {e}")

        if not data:
            print("ERROR: the file content only comment and blank no data")
            sys.exit(1)

        name, number = data[0].split(":")

        if not name == "nb_drones":
            raise ParsingError("the file should start with nb_drones")

        number = number.strip()

        if not number:
            raise ParsingError("nb_drones is missing a value")

        if not number.isdigit():
            raise ParsingError(f"nb_drones value must be an integer, got '{number}'")

        nb = int(number)
        if nb > 10000:
            raise ParsingError(f"the number is too large max is 10000 got '{nb}'")
        if nb < 0 or nb == 0:
            raise ParsingError(f"the nuber should be bigger than 0")

        return data

try: 
    path = "maps/challenger/01_the_impossible_dream.txt"
    test = Parsing()
    print(test.read_file(path))
except ParsingError as e:
    print(e)

