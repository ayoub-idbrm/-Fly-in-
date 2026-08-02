from pydantic import BaseModel



class ParsingError(Exception):
    """raise an error in with catch it in the parsing"""
    pass



class Parsing():

    def challenger_filles(self):
        challenger_data = ""
        try:
            with open("maps/challenger/01_the_impossible_dream.txt") as d:
                for line in d:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    challenger_data = challenger_data + line + "\n"
        except ParsingError as f:
            print(f)

        return challenger_data


    def easy_filles(self):
        easy_data_01 = ""
        try:
            with open("maps/easy/01_linear_path.txt") as a:
                for line in a:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    easy_data_01 = easy_data_01 + line + "\n"
        except ParsingError as d:
            print(d)
        easy_data_02 = ""
        try:
            with open("maps/easy/02_simple_fork.txt") as z:
                for line in z:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    easy_data_02 = easy_data_02 + line + "\n"
        except ParsingError as h:
            print(h)
        easy_data_03 = ""
        try:
            with open("maps/easy/03_basic_capacity.txt") as s:
                for line in s:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    easy_data_03 = easy_data_03 + line + "\n"
        except ParsingError as b:
            print(b)

        return list(easy_data_01, easy_data_02, easy_data_03)


    def hard_filles(self):
        hard_data_01 = ""
        try:
            with open("maps/hard/01_maze_nightmare.txt") as j:
                for line in j:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    hard_data_01 = hard_data_01 + line + "\n"
        except ParsingError as v:
            print(v)
        hard_data_02 = ""
        try:
            with open("maps/hard/02_capacity_hell.txt") as g:
                for line in g:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    hard_data_02 = hard_data_02 + line + "\n"
        except ParsingError as c:
            print(c)
        hard_data_03 = ""
        try:
            with open("maps/hard/03_ultimate_challenge.txt") as q:
                for line in q:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    hard_data_03 = hard_data_03 + line + "\n"
        except ParsingError as r:
            print(r)

        return list(hard_data_01, hard_data_02, hard_data_03)


    def medium_filles(self):
        medium_data_01 = ""
        try:
            with open("maps/medium/01_dead_end_trap.txt") as n:
                for line in n:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    medium_data_01 = medium_data_01 + line + "\n"
        except ParsingError as b:
            print(b)
        medium_data_02 = ""
        try:
            with open("maps/hard/02_capacity_hell.txt") as n:
                for line in n:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    medium_data_02 = medium_data_02 + line + "\n"
        except ParsingError as b:
            print(b)
        medium_data_03 = ""
        try:
            with open("maps/medium/03_priority_puzzle.txt") as m:
                for line in m:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    medium_data_03 = medium_data_03 + line + "\n"
        except ParsingError as b:
            print(b)

        return list(medium_data_01, medium_data_02, medium_data_03)







# def main():
#     """the main just for test"""
#     parer = Parsing()
#     test = parer.reading_files()
#     print(test)

# main()