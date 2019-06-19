from microlab.io.images import read_image, create_image, update_image
from microlab.io.files import delete_file
import os

dir = os.getcwd()
frames = os.path.join(dir, 'frames')

# image Data
filename = os.path.join(frames, '1.jpg')
img = read_image(path=filename, verbose=True)

# Create image
create_image(path=filename, image=img, verbose=True)

# Read image
image = read_image(path=filename, verbose=True)

# Update image
update_image(path=filename, image=image, verbose=True)

# Delete image
# delete_file(path=filename, verbose=True)