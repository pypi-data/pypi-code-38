from click import get_terminal_size


# use click.get_terminal_size instead of standard lib os.get_terminal_size because of error handling
# (necessary for unit tests)

def fill_terminal_columns_on_both_sides_of_text(text: str, filler_character: str, minimum_filling_per_side=0) -> str:
    assert len(filler_character) == 1
    terminal_columns, terminal_lines = get_terminal_size()
    if terminal_columns < len(text):
        return text
    else:
        left_over_space = terminal_columns - len(text)
        if left_over_space < minimum_filling_per_side * 2:
            left_over_space = minimum_filling_per_side * 2
        left_side_character_count = left_over_space // 2
        right_side_character_count = left_over_space - left_side_character_count
        return (left_side_character_count * filler_character) + text + (right_side_character_count * filler_character)
