import sys


class ParsingError(Exception):
    """Raise an error during parsing."""

    pass


class Parsing:

    def read_file(self, path: str) -> list[str]:
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
            raise ParsingError(f"failed to open '{path}': {e}")

        if not data:
            print("ERROR: the file content only comment and blank no data")
            sys.exit(1)

        name, number = data[0].split(":")

        if name != "nb_drones":
            raise ParsingError("the file should start with nb_drones")

        number = number.strip()

        if not number:
            raise ParsingError("nb_drones is missing a value")

        if not number.isdigit():
            raise ParsingError(
                f"nb_drones value must be an integer, got '{number}'"
            )

        nb = int(number)
        if nb > 10000:
            raise ParsingError(
                f"the number is too large max is 10000 got '{nb}'"
            )
        if nb <= 0:
            raise ParsingError("the number should be bigger than 0")

        valid_directives = {"start_hub", "end_hub", "hub", "connection"}
        valid_key_meta = {
            "zone", "color", "max_drones", "max_link_capacity"
        }
        valid_zones = {"normal", "blocked", "restricted", "priority"}

        for line in data[1:]:
            duplicate_keys = []
            if ":" not in line:
                raise ParsingError(
                    f"Invalid line format (missing ':'): '{line}'"
                )

            key = line.split(":", 1)[0].strip()

            if key not in valid_directives:
                raise ParsingError(f"ERROR: UNVALID KEY: '{key}'")

            if "[" in line or "]" in line:
                has_brackets = "[" in line and "]" in line
                valid_order = line.find("[") < line.find("]")
                if not (has_brackets and valid_order):
                    raise ParsingError(
                        f"Malformed brackets in line: '{line}'"
                    )

                if not line.endswith("]"):
                    raise ParsingError(
                        "Trailing content after closing "
                        f"bracket: '{line}'"
                    )

                start_idx = line.find("[") + 1
                bracket_content = line[start_idx:-1].strip()
                if not bracket_content:
                    raise ParsingError(
                        f"Empty brackets found in line: '{line}'"
                    )

                for attr in bracket_content.split():
                    if (
                        "=" not in attr
                        or attr.startswith("=")
                        or attr.endswith("=")
                    ):
                        raise ParsingError(
                            f"Invalid attribute '{attr}' in brackets. "
                            "Expected 'key=value'"
                        )
                    attr_key, value = attr.split("=")

                    if attr_key in duplicate_keys:
                        raise ParsingError(
                            f"ERROR: duplicate key '{attr_key}'"
                        )
                    duplicate_keys.append(attr_key)

                    if attr_key == "zone" and value not in valid_zones:
                        raise ParsingError(
                            f"ERROR: The Zone Should Be valid not '{value}'"
                        )

                    if attr_key not in valid_key_meta:
                        raise ParsingError(
                            f"ERROR: invalid key '{attr_key}'"
                        )

        return data
