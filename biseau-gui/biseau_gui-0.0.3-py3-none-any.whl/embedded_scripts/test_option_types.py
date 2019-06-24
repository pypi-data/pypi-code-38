"""Testing and showing of available option types for the run_on function."""

import inspect

NAME = 'test option types'

def run_on(models, *,
           a_natural_number:int=42,
           a_float:float=3.1415,
           a_bool:bool=True,  # should be checked at startup !
           a_short_text:str="Hello!",
           a_multiline_text:str="Hello!\nHow are you?",
           a_list_of_items:['a', 'b', 'c', 'd']='a',
           # a_set_of_items:{'a', 'b', 'c', 'd'}={'a', 'b'},
           a_file:open='out.txt',
           an_existing_file:(open, 'r')='existing.txt',
           a_writable_file:(open, 'w')='writable.txt',
           a_range:range(12, 21, 3)=15,
           ):
    print('\nTEST_OPTION_TYPES.OPTIONS:', inspect.getfullargspec(run_on))
    for arg in inspect.getfullargspec(run_on).kwonlydefaults:
        argval = locals()[arg]
        if isinstance(argval, str): argval = argval.replace('\n', '\\n')
        yield f'link("{arg}","{argval}").'
