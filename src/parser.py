from pydantic import BaseModel
import sys


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
        return data

path = "maps/challenger/01_the_impossible_dream.txt"
test = Parsing()
print(test.read_file(path))

