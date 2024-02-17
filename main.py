from pypresence import Presence
from config import CLIENT_ID
import time
import requests as rq
import win32gui

client_id = CLIENT_ID
RPC = Presence(client_id)

def get_info_windows():
    import win32api
    import win32gui
    import win32process
    import pywintypes
    from pathlib import Path

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    windows = []

    window = win32gui.FindWindow("SpotifyMainWindow", None)
    old = win32gui.GetWindowText(window)

    def find_spotify_uwp(hwnd, windows):
        text = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        if classname == "Chrome_WidgetWin_0" and len(text) > 0:
            _, proc_id = win32process.GetWindowThreadProcessId(hwnd)
            proc_h = win32api.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, proc_id)
            path = win32process.GetModuleFileNameEx(proc_h, None)
            win32api.CloseHandle(proc_h)

            if Path(path).name == "Spotify.exe":
                windows.append(text)
                return False

    if old:
        windows.append(old)
    else:
        try:
            win32gui.EnumWindows(find_spotify_uwp, windows)
        except pywintypes.error:
            pass

    if len(windows) == 0:
        raise SpotifyClosed

    try:
        artist, track = windows[0].split(" - ", 1)
    except ValueError:
        artist = ""
        track = windows[0]

    if windows[0].startswith("Spotify"):
        raise SpotifyPaused

    return track, artist

def getFile():
    file = rq.get("http://localhost:1337/getCurrentFilename")
    return file.json()["name"]

RPC.connect()

while True:
    current_file = getFile()
    RPC.update(state="listening: " + get_info_windows()[1] + " - " + get_info_windows()[0],
        details="Working on: " + current_file,
        large_image="big_imagetest",
        large_text="random image", 
        buttons=[{"label": "web", "url": "https://0xpure.com"}],
    )
    time.sleep(1)
