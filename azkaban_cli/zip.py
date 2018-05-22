import logging
import zipfile
import os

def zip_directory(path, zip_name):
    absolute_path = os.path.abspath(path)

    if not os.path.isdir(absolute_path):
        logging.error('No such directory: %s' % absolute_path)
        return None

    # Where .zip will be created
    zip_path = os.path.join(absolute_path, zip_name)

    # Create .zip
    zf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(path):
        # ensure .zip root dir will be the path basename
        zip_root = root.replace(path, '', 1)

        for file in files:
            # local file path
            file_path = os.path.join(root, file)

            # .zip file path
            zip_file_path = os.path.join(zip_root, file)

            # skip adding .zip files to our zip
            if zip_file_path.endswith('.zip'):
                continue

            # add local file to zip
            zf.write(file_path, zip_file_path)

    zf.close()

    return zip_path
