import zipfile


def unzip(src_zip_file, dest="."):
    zip_ref = zipfile.ZipFile(src_zip_file, 'r')
    zip_ref.extractall(dest)
    zip_ref.close()