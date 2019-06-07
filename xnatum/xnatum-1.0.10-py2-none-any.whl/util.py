import os, shutil, tempfile, bz2

# Function to manipulate bz files
def unbzip(filepath, dest=None):
    newfile = filepath.rsplit(".", 1)[0]
    # If the results will be moved to other destination
    if dest:
        newfile = os.path.join(dest, os.path.basename(newfile))

    with open(newfile, "wb") as new_file, bz2.BZ2File(filepath, "rb") as file:
        for data in iter(lambda: file.read(100 * 1024), b""):
            new_file.write(data)


# Function to create a temporary zip file
# data_in = folder if is a string or files if a list
# Ignores subfolders
def tmp_zip(data_in, prefix="xnat_"):
    tmpdir = tempfile.mkdtemp()
    try:
        files = os.listdir(data_in) if isinstance(data_in, str) else data_in
        # Moving all files to temporary directory
        for subfile in files:
            # When data_in is a folder, it completes the path
            if isinstance(data_in, str):
                subfile = os.path.join(data_in, subfile)
            # Uncompressing bz files
            # TODO: Uncompress gz and zip
            if subfile.endswith(".bz"):
                unbzip(subfile, tmpdir)
            else:
                shutil.copy2(subfile, tmpdir)

        # Creating temporary zip name
        fzip = tempfile.NamedTemporaryFile(prefix=prefix)
        fzip.close()

        shutil.make_archive(fzip.name, "zip", tmpdir)
    finally:
        shutil.rmtree(tmpdir)

    return fzip.name + ".zip"
