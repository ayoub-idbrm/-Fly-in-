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
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    data.append(line)

        except OSError as e:
            raise ParsingError(f"failed to open '{path}: {e}")

        return data



