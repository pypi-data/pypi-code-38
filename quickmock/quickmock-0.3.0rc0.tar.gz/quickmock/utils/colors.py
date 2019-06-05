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

import colorama


def colorize(text, message_type=None):
    """Function that colorizes a message

    Args:
        text (str): The string to be colorized.
        message_type (str): Possible options include "ERROR", "WARNING",
            "SUCCESS", "INFO" or "BOLD".

    Returns:
        string: Colorized if the option is correct, including a tag at the end
            to reset the formatting.
    """
    formatted_text = str(text)
    # Set colors
    if "ERROR" in message_type:
        formatted_text = colorama.Fore.RED + formatted_text
    elif "WARNING" in message_type:
        formatted_text = colorama.Fore.YELLOW + formatted_text
    elif "SUCCESS" in message_type:
        formatted_text = colorama.Fore.GREEN + formatted_text
    elif "INFO" in message_type:
        formatted_text = colorama.Fore.BLUE + formatted_text

    # Set emphashis mode
    if "BOLD" in message_type:
        formatted_text = colorama.Style.BRIGHT + formatted_text

    return formatted_text + colorama.Style.RESET_ALL
