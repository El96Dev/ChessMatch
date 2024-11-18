import os
from fastapi import UploadFile, HTTPException, status


def check_image_size(image: UploadFile, kb_size_limit: int) -> bool:
    image.file.seek(0, 2)
    file_size_kbytes = image.file.tell()/1024
    image.file.seek(0)
    return file_size_kbytes <= kb_size_limit


def save_avatar(user_id: int, image: UploadFile):
    file_path = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + image.content_type.split("/")[-1]
    with open(file_path, 'wb') as f:
        f.write(image.file.read())


def check_avatar_exists(user_id: int):
    jpeg_filepath = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + ".jpeg"
    png_filepath = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + ".png"
    return os.path.exists(jpeg_filepath) or os.path.exists(png_filepath)    


def delete_avatar(user_id: int):
    jpeg_filepath = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + ".jpeg"
    png_filepath = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + ".png"
    if os.path.exists(jpeg_filepath):
        os.remove(jpeg_filepath)
    elif os.path.exists(png_filepath):
        os.remove(png_filepath)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Custom avatar was not found!") 


def get_image_filepath(user_id: int):
    jpeg_filepath = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + ".jpeg"
    png_filepath = os.path.dirname(__file__) + "/../../../images/" + str(user_id) + ".png"
    default_filepath = os.path.dirname(__file__) + "/../../../images/default.jpg"
    if os.path.exists(jpeg_filepath):
        return jpeg_filepath
    elif os.path.exists(png_filepath):
        return png_filepath
    elif os.path.exists(default_filepath):
        return default_filepath 
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image was not found!")