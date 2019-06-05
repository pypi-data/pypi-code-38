###############################################################################
#
#   Copyright 2018-2019 Telefónica
#
#   Quickmock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import json
import sys
import textwrap

from quickmock.utils.colors import colorize


def create_template(args):
    """Create a template file based on the user input

    Args:
        args (parsed_args): Parsed arguments from the entry_point
    """
    template = {
        "responses": {}
    }

    welcome = f"""
                    {colorize("Quickmock Template Creator", "SUCCESS BOLD")}
                    {colorize("==========================", "BOLD")}

                    Coded with {colorize("♥", "ERROR")} @ {colorize("Telefónica", "INFO BOLD")}


    This assistant will help you to create a valid quickmock template.
    Note: The contents in brackets will be assumed as default.

    """
    print(textwrap.dedent(welcome))

    end = False
    try:
        print("Setting default information...")
        template["host"] = input("> Hostname reachability [0.0.0.0]: ") or "0.0.0.0"

        while True:
            try:
                port_str = input("> Server [5000]: ")
                port = 5000 if not port_str else int(port_str)

                if port >= 1 and port <= 65535:
                    template["port"] = port
                else:
                    print("Invalid input. Port SHOULD be in the range [1, 65535].")
                    continue
            except ValueError:
                print("Invalid input. Port SHOULD be an int.")
                continue
            else:
                break

        while not end:
            print("\nConfiguring a new mocked endpoint:")
            method = input("> Insert HTTP method [GET]: ").upper()

            if not method:
                method = "GET"
            elif method not in ["GET", "POST", "PUT", "DELETE"]:
                print("Invalid HTTP method.")
                continue

            if method not in template["responses"].keys():
                template["responses"][method] = {}

            # Deal with valid paths
            while True:
                try:
                    path = input("> Insert a new path (e. g.: 'api/v1/test'): ")
                    if not path:
                        print("Invalid input. Path cannot be 'None'.")
                        continue
                    elif path[0] == '/':
                        print("Invalid input. The first parameter SHOULD NOT be a '/'.")
                        continue

                    if path not in template["responses"][method]:
                        template["responses"][method][path] = []

                    print(f"\nStarting to request new responses for '{path}'...")
                    index = 0
                    # Deal with more responses
                    more_responses = True
                    while more_responses:
                        index += 1
                        print(f"\nRetrieving information for response {index}...")
                        # TODO: Add new response
                        response = {}

                        while True:
                            try:
                                response["status"] = int(input(f"({path}) > Insert HTTP status code: "))
                            except ValueError:
                                print("Invalid input. Status SHOULD be an int.")
                                continue
                            else:
                                break

                        response["mimetype"] = input(f"({path}) > Insert mimetype [application/json]: ") or "application/json"

                        return_str = input(f"({path}) > Insert return data: ")
                        if response["mimetype"] == "application/json":
                            try:
                                response["return"] = json.loads(return_str)
                            except Exception as e:
                                print("Invalid data input. The passed info SHOULD be a JSON.")
                        else:
                            response["return"] = return_str

                        # Configure additional optional checks
                        checks = {}

                        while True:
                            with_headers = input(f"({path}) > Do you want to add headers validation? (y/N): ").upper()

                            if with_headers != "N":
                                try:
                                    valid_headers = input(f"({path}) > Type valid headers (as a dict): ")
                                    error = input(f"({path}) > Type the error response (as a dict): ")
                                    # TODO: Check error
                                    checks["headers"] = {
                                        "valid": json.loads(valid_headers),
                                        "error": json.loads(error)
                                    }
                                except Exception as e:
                                    print("Invalid headers input. The passed info SHOULD be a JSON.")
                                else:
                                    break
                            else:
                                break

                        while True:
                            with_data = input(f"({path}) > Do you want to add data validation? (y/N): ").upper()

                            if with_data != "N":
                                try:
                                    valid_data = input(f"({path}) > Type valid data (as a dict): ")
                                    error = input(f"({path}) > Type the error response (as a dict): ")
                                    # TODO: Check error
                                    checks["data"] = {
                                        "valid": json.loads(valid_data),
                                        "error": json.loads(error)
                                    }
                                except Exception as e:
                                    print("Invalid data input. The passed info SHOULD be a JSON.")
                                else:
                                    break
                            else:
                                break

                        # Build final response
                        full_response = {
                            "response": response
                        }
                        if checks:
                            full_response["checks"] = checks

                        print(f"Appending new response: {json.dumps(full_response, indent=2)}")
                        template["responses"][method][path].append(full_response)

                        # Closing the response creation loop
                        new_responses = input(f"({path}) > Do you want to add new responses to '{path}'? (y/N): ").upper()
                        if new_responses == "N" or new_responses == "":
                            more_responses = False

                except ValueError:
                    print("Invalid input. Path is not a valid path.")
                    continue
                else:
                    break

            # Closing the path creation loop
            new_paths = input(f"({path}) > Do you want to add a new endpoint? (y/N): ").upper()
            if new_paths == "N" or new_paths == "":
                end = True

        print(f"Generated configuration file:\n{json.dumps(template, indent=2)}")
        if not args.output_only:
            try:
                with open(args.template_file, "w") as oF:
                    oF.write(json.dumps(template, indent=2))
            except Exception as e:
                print("Output file unreachable. Exiting...")
                sys.exit(2)

    except KeyboardInterrupt:
        print("\nManually stopped by the user. Exiting...")
        sys.exit(1)
