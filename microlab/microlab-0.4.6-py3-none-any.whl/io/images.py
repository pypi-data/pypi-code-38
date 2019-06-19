from microlab.io.files import delete_file
import cv2
import os


# Create
def create_image(path, image, verbose=False):
    if verbose:
        print('[  C  ]  {}'.format(path), end='.....')
    if os.path.isfile(path):
        if verbose:
            print('[ OK ] replace old image file')
    else:
        if verbose:
            print('[ OK ] create new image file')
    cv2.imwrite(filename=path,img=image)


# Read
def read_image(path, verbose=False):
    if verbose:
        print('[  R  ]  {}'.format(path), end='.....')
    if os.path.isfile(path):
        image = cv2.imread(filename=path)
        if verbose:
            print('[ OK ] read from image file')
        return image
    else:
        if verbose:
            print('[ !! ] file not found')
        return None


# Update
def update_image(path,image, verbose=False ):
    if verbose:
        print('[  U  ]  {}'.format(path), end='.....')
    if os.path.isfile(path):
        cv2.imwrite(filename=path, img=image)
        if verbose:
            print('[ OK ] update old image file')
    else:
        if verbose:
            print('[ !! ] file not found')


# Delete
def delete_image(path, verbose=False):
    delete_file(path=path, verbose=verbose)
