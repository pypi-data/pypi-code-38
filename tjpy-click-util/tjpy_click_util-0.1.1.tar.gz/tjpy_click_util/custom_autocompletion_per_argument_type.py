# import click
# import click._bashcomplete as internal_click_bashcomplete
#
# from typing import List
#
# _original_click_get_user_autocompletions = internal_click_bashcomplete.get_user_autocompletions
# assert _original_click_get_user_autocompletions is not None
#
#
# def _extended_get_user_autocompletions(ctx: click.Context,
#                                        args: List[str],
#                                        incomplete: str,
#                                        cmd_param: click.Parameter):
#     if cmd_param.type.autocomplete is not None:
#         def delegate_autocomplete_call_to_type(ctx_again,
#                                                args_again,
#                                                incomplete_again):
#             return cmd_param.type.autocomplete(ctx, args, incomplete, cmd_param)
#
#         cmd_param.autocomplete = delegate_autocomplete_call_to_type
#     return _original_click_get_user_autocompletions(ctx, args, incomplete, cmd_param)
#
#
# def enable_autocompletion_on_argument_type():
#     internal_click_bashcomplete.get_user_autocompletions = _extended_get_user_autocompletions
