from os.path import commonprefix

# Return "word", "ord", "rd", "d"
def _iterate_text_by_leftmost_character(text):
    for i in range(len(text)):
        yield text[i:]

# Merge a word with the previous word based on their common content. E.g. recon + continue == recontinue
def merge(ctx, cmdline):
    args = cmdline.split(':')
    assert len(args) == 1

    action = ctx.copy_last_action()

    # The to-be-merged text.
    new_text = args[0]
    if not new_text:
        return action

    # Get the previous text up to the new text's length.
    last_text = ctx.last_text(len(new_text))

    # Check if we need to merge with a space character -- extra logic!
    replaces_space = new_text[0] == action.space_char
    if action.next_attach == False and not replaces_space:
        # If our meta doesn't replace a space, we need to acknowledge the space.
        # E.g. merging "beacon" and "continue" should be "beacon continue"
        # (Because "beacon" is not a prefix!)
        last_text += action.space_char
    elif action.next_attach == False and replaces_space:
        # If our meta does replace a space, we can ignore it in this case.
        # E.g. merging "how are you" and " are you" produces "how are you" in the merge case.
        # But in the nonmerge case, "who" and " are you" produces "who are you".
        new_text = new_text[1:]

    # Find the part of text that the two strings are joined by.
    text_join = ''
    for word_part in _iterate_text_by_leftmost_character(last_text):
        if new_text.startswith(word_part):
            text_join = word_part
            break

    # Subtract what the two strings are joined by to get the new output.
    output = new_text[len(text_join):]

    # Only do something if there is actual output.
    if output:
        action.text = output
        action.next_attach = False

    # TODO: Add to action.word

    return action