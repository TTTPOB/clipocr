# Usage

## Setup

### Install

#### Windows

Download the `exe` file from release

#### Mac/Linux
Install the dependencies, and run `pyinstaller bin.py --noconsole -F` 

#### Config

apply an api key from [baidu](https://cloud.baidu.com/doc/OCR/index.html).
config file example
```yaml
appid: xxxxx
api_key: xxxxx
sec_key: xxxxx
```
fill in the config file and save it to `C:/Users/${username}/.config/clipocr/config.yaml`

Then copy a picture to clipboard, run `clipocr.exe`, wait a second, and the text will appear in the clipboard.


## In cooperation with Snipaste
Go to snipaste settings - `Control (控制)` - `Add new command (添加新命令)`, add a new command with following: `snip -o clipboard;exec(C:\Tools\Programs\Media\clipocr.exe)` (Please replace the path with your own path to place the `clipocr.exe`) and bind whatever shortcut you want. Press it and it will automatically copy the text to clipboard.