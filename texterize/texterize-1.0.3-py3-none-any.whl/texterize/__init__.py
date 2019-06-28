import sys
sys.path.append('.')

from src.filter_text import filterText
from src.build_chroma import buildChroma
from src.build_block import buildBlock
from src.write_file import write

OUTPUT_DIRECTORY = "./texterized_image"
SUPPORTED_FILE_TYPES = ["HTML", "Word"]

#main, input text as raw string
def create(text, img_path, write_path=OUTPUT_DIRECTORY, output_file_type="HTML", overwrite=True):
    '''
    params:
    -text: The text to be converted into an image, in string format
    -img_path: The path to the image that the texterized image should be based on
    -writePath: The filename/path to which the resulting document should be written
    -output_file_type: The desired format of the output file
    -overwrite: Bool representing whether an existing doc with the given filepath should be overwritten
    '''
    assert isinstance(text, str), f"Expected input of type string, found {type(text)}."
    assert output_file_type in SUPPORTED_FILE_TYPES, (f"Output file type {output_file_type} not supported.")

    text = filterText(text)
    chroma, chroma_shape = buildChroma(img_path, len(text))
    text_arr = buildBlock(text, chroma_shape)
    return write(text_arr, chroma, output_file_type, write_path, overwrite)
    
#Run create() using text in a .txt file, rather than as input
def createFromFile(text_path, img_path, write_path=OUTPUT_DIRECTORY, output_file_type="HTML", overwrite=True):
    '''
    params:
    -text_path: The path to the .txt file to pull the text from
    -write_path: The filename/path to which the resulting document should be written
    -img_path: The path to the image that the texterized image should be based on
    -output_file_type: The desired format of the output file
    -overwrite: Bool representing whether an existing doc with the given filepath should be overwritten
    '''
    try:
        f = open(text_path, "r")
        text = f.read()
        f.close()
    except:
        raise Exception(f"Could not open file {text_path}, aborting.")
    return create(text, img_path, write_path, output_file_type, overwrite)

TEST_PATH = "../test/test_files/test_3.txt"
TEST_IMG_PATH = "../test/test_img/test_2.jpg"
FILE_TYPE = "HTML"
WRITE_PATH = "../test/output_files/texterize_test"
OVERWRITE = True

createFromFile(TEST_PATH, TEST_IMG_PATH, output_file_type=FILE_TYPE, write_path=WRITE_PATH, overwrite=OVERWRITE)