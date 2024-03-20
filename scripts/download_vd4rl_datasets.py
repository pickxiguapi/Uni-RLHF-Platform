import gdown

def download_google_drive_folder(folder_id):
    url = f'https://drive.google.com/drive/folders/{folder_id}'
    gdown.download_folder(url, quiet=False, use_cookies=False)

folder_id = '16CmKNZWIK907Cj5J-_zaEy4YuKOTjupK'  
download_google_drive_folder(folder_id)
