import PIL
from PIL import Image
from PIL import ImageGrab
import httpx
from typing import Union, List
from pathlib import Path
import os
import yaml
import urllib
import base64
from datetime import datetime, timedelta
import pyperclip
from io import BytesIO

ACCESS_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

def get_config_path() -> Path:
    # find config file
    # 1. home_dir / .config/clipocr/config.yaml
    home_dir_config = Path.home() / ".config" / "clipocr" / "config.yaml"
    if home_dir_config.exists():
        return home_dir_config
    else:
        raise FileNotFoundError(
            "config file not found, please place a yaml file"
            " in ~/.config/clipocr/config.yaml"
            "with appid, api_key, and sec_key entry in it"
        )


def get_state_path() -> Path:
    # home_dir/ .config/clipocr/state.yaml
    state_file = Path.home() / ".config" / "clipocr" / "state.yaml"
    return state_file


def get_access_token_and_write_to_state_file(config_dict: dict) -> str:
    client = httpx.Client()
    params = {
        "grant_type": "client_credentials",
        "client_id": config_dict["api_key"],
        "client_secret": config_dict["sec_key"],
    }
    resp = client.post(ACCESS_TOKEN_URL, params=params)
    access_token = resp.json()["access_token"]
    # get current time
    now = datetime.now()
    state_dict = {
        "access_token": access_token,
        "expire_time": now + timedelta(seconds=resp.json()["expires_in"]),
    }
    state_path = get_state_path()
    with open(state_path, "w") as f:
        yaml.safe_dump(state_dict, f)
    return access_token


def get_access_token_wrapper():
    state_path = get_state_path()
    if state_path.exists():
        with open(state_path, "r") as f:
            state = yaml.safe_load(f)
            if state["expire_time"] > datetime.now():
                access_token = state["access_token"]
            else:
                config_path = get_config_path()
                config_dict = read_config_dict(config_path)
                access_token = get_access_token_and_write_to_state_file(config_dict)
    else:
        config_path = get_config_path()
        config_dict = read_config_dict(config_path)
        access_token = get_access_token_and_write_to_state_file(config_dict)
    return access_token


def read_config_dict(config_path: Union[str, os.PathLike]) -> dict:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        return config


def base64_and_url_encode(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=75)
    buffered.seek(0)
    image_bytes = buffered.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return image_base64

def image_validation_and_encode(image: Image) -> Union[str, None]:
    # bigger than 15px
    # smaller than 8192px
    # size less than 15mb after base64 and urlencode
    if image.size[0] >= 15 and image.size[1] >= 15:
        if image.size[0] <= 4096 and image.size[1] <= 4096:
            encoded_image = base64_and_url_encode(image)
            if len(encoded_image.encode("utf-8")) <= 15 * 1024 * 1024:
                return encoded_image
    else:
        return None

def parse_words_result(words_result: List[dict]) -> str:
    word_list = []
    for word in words_result:
        word_list.append(word["words"])
    return "\n".join(word_list)


def baidu_ocr(image: Image, access_token: str) -> str:
    client = httpx.Client(headers={"Content-Type": "application/x-www-form-urlencoded"})
    encoded_image = image_validation_and_encode(image)
    if encoded_image is None:
        raise ValueError("image is invalid")
    post_data = {
        "image": encoded_image,
        "access_token": access_token,
        "language_type": "auto_detect",
        "detect_direction": "true",
    }
    resp = client.post(OCR_URL, data=post_data)
    words_result = resp.json()["words_result"]
    return words_result


def ocr_clipboard():
    image = ImageGrab.grabclipboard()
    access_token = get_access_token_wrapper()
    words_result = baidu_ocr(image, access_token)
    plain_text = parse_words_result(words_result)
    # paste to clipboard
    pyperclip.copy(plain_text)

if __name__ == "__main__":
    ocr_clipboard()