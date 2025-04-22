#music app <16apr>
import os
import tkinter as tk
from tkinter import filedialog
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from pydub import AudioSegment
import tempfile
from pydub.utils import which
import zipfile
import urllib.request
import shutil
import sys


#i have no idea about this code 
#but it works so i will keep it for now

def show_download_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    percent = int(downloaded * 100 / total_size) if total_size > 0 else 0
    sys.stdout.write(f"\r⬇️  Downloading ffmpeg... {percent}%")
    sys.stdout.flush()
    if downloaded > 0:
        print(f"\nDebug: Downloaded {downloaded} of {total_size} bytes")


def setup_ffmpeg():
    if which("ffmpeg"):
        print("✅ ffmpeg is already available.")
        return

    print("⚠️ ffmpeg not found. Downloading portable version...")

    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    download_path = "ffmpeg.zip"
    extract_path = "bin"

    # Download the zip with progress
    urllib.request.urlretrieve(ffmpeg_url, download_path, reporthook=show_download_progress)
    print("\n📦 Download complete. Extracting...")

    # Extract it
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    # Find the ffmpeg.exe inside the extracted folders
    for root, dirs, files in os.walk(extract_path):
        if "ffmpeg.exe" in files:
            ffmpeg_exe_path = os.path.join(root, "ffmpeg.exe")
            break
    else:
        raise FileNotFoundError("ffmpeg.exe not found after extraction!")

    # Set ffmpeg path manually for pydub
    AudioSegment.converter = ffmpeg_exe_path
    print(f"✅ ffmpeg configured: {ffmpeg_exe_path}")

    # Clean up zip
    os.remove(download_path)


# Call this before playing .m4a files
setup_ffmpeg()




# tell pydub to use the local ffmpeg binary
AudioSegment.converter = which("ffmpeg") or os.path.join(os.getcwd(), "ffmpeg.exe")



import pygame
#for the music player
pygame.mixer.init()
print("🎧 Pygame mixer initialized.")

#for the music metadata
#asks the user to chose a folder or just use the default music folder
def choose_music_folder(d3fau1t = True):
    if d3fau1t:
        return os.path.join(os.path.expanduser("~"), "Music")
    
    return filedialog.askdirectory(title="Select Music Folder")
    
    

def list_music_files(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return []
    song_list = [] #to store the songs
    for file in os.listdir(folder_path):
        if file.endswith(('.mp3','.m4a')):
            full_path = os.path.join(folder_path, file)
            try:
                if file.endswith('.mp3'):
                    audio = EasyID3(full_path)
                    title = audio.get('title', [None])[0]
                    artist = audio.get('artist', [""])[0]

                elif file.endswith('.m4a'):
                    audio = MP4(full_path)
                    title = audio.tags.get('\xa9nam', [None])[0]
                    artist = audio.tags.get('\xa9ART', [""])[0]

                


                if title:
                    display_name = f"{title} - {artist}" if artist else title
                else:
                    display_name = file
            except Exception:
                display_name = file #if the file is not a valid mp3 file
            song_list.append((display_name, file)) #add the song to the list
    return song_list #return the list of songs

    
#finds all the files with mp3 and save them


music__folder = choose_music_folder()
music_files = list_music_files(music__folder)



#GUI------------------------------#################
def show_gui(initial_song_list, music_folder):
    song_list_wrapper = [initial_song_list]


    window = tk.Tk()
    window.title("d1sc🎧")

    window.config(bg = "#1e1e2f")
    window.state("zoomed")#for fullscreen on windows
    
    title_label = tk.Label(
        window, text="🎶 d1sc Music Player", font=("Segoe UI", 30, "bold"),
        fg="#f1f1f1", bg="#1e1e2f"
    )
    title_label.pack(pady=20)

    # 🟢 Define this BEFORE using it inside other functions
    folder_label = tk.Label(
        window, text=f"📁 Folder: {music_folder}",
        font=("Segoe UI", 12),
        fg="#b0b0b0", bg="#1e1e2f"
    )
    folder_label.pack(pady=5)
      # Fullscreen on Windows

    def change_folder():
        new_folder = choose_music_folder(d3fau1t =False)  # Ask user to pick new folder
        if new_folder:
            music_files = list_music_files(new_folder)
            update_listbox(music_files)
            folder_label.config(text=f"📁 Folder: {new_folder}")
            nonlocal music_folder
            music_folder = new_folder


#for first title and label
    label = tk.Label( 
        
        window, text="🎧 Your Songs:", font=("Segoe UI", 18, "bold"),
    fg="#f1f1f1", bg="#1e1e2f"
    
    )

    label.pack(pady=10)
#create a frame for the listbox and scrollbar
    listbox_frame= tk.Frame(window)
    scrollbar = tk.Scrollbar(listbox_frame)

    listbox = tk.Listbox(
        listbox_frame,
        width=60,                 # wider listbox
        height=20,
        yscrollcommand=scrollbar.set,
        font=("Segoe UI", 16, "bold"),   # bigger and bold font
        bg="#2a2a40",
        fg="#f1f1f1",
        selectbackground="#9b5de5",
        selectforeground="#ffffff",
        relief="flat",
        bd=0,
        activestyle='none',
        highlightthickness=0)
    
    scrollbar.config(command= listbox.yview)
    scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
    listbox.pack(side = tk.LEFT, fill = tk.BOTH, expand =True)
    #to make the listbox expand with the window

    listbox_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
#to create proper listbox and add the songs to it
    def update_listbox(new_song_list):
        song_list_wrapper[0] = new_song_list  # Update the wrapper list
        listbox.delete(0, tk.END)  # Clear existing list
        for song in new_song_list:
            listbox.insert(tk.END, f" 🎵{song[0]}")   # indent for spacing
               

    

    def play_song(event):
        print("🔊 play_song triggered!")
        

        selected_index = listbox.curselection()
        if selected_index:
            real_index = selected_index[0]
            _, filename = song_list_wrapper[0][real_index]  # get actual file name from the original list
            song_path = os.path.join(music_folder, filename)


            
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()


                if filename.endswith(".m4a"):
                    audio = AudioSegment.from_file(song_path, format="m4a")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        temp_wav_path = tmp_file.name
                        audio.export(temp_wav_path, format="wav")

                    pygame.mixer.music.load(temp_wav_path)

                else:
                    pygame.mixer.music.load(song_path)

                pygame.mixer.music.play()
                print(f"▶️ Playing: {song_path}")

            except Exception as e:
                print(f"Failed to play: {song_path}")
                print(f"Error: {e}")
                    

                        
                        

                        
                        
                    


                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                print(f"▶️ Playing: {song_path}")
            except Exception:
                print(f"Failed to play: {song_path}")
        
            # Update the label to show the currently playing song
    listbox.bind("<Double-Button-1>", play_song)

        

    def on_enter(e): change_btn.config(bg="#6c63ff")
    def on_leave(e): change_btn.config(bg="#3c3f58")
#to change button

    change_btn = tk.Button( 
        
        window, text="🎵 Change Folder", command=change_folder,
        font=("Segoe UI", 14), bg="#9b5de5", fg="white",
        activebackground="#00bbf9", relief="flat", padx=20, pady=10,
        cursor="hand2"

    )
    change_btn.pack(pady=20)
    change_btn.bind("<Enter>", on_enter)
    change_btn.bind("<Leave>", on_leave)


    # Add refresh button to reload the song list
    refresh_btn = tk.Button( 

    window, text="🔄 Refresh List", command=lambda: update_listbox(list_music_files(music_folder)),
    font=("Segoe UI", 14), bg="#6c63ff", fg="white",
    relief="flat", padx=20, pady=10,
    cursor="hand2"
)
    refresh_btn.pack(pady=10)


    update_listbox(initial_song_list)
#to update the listbox with the initial song list

    window.mainloop()

    



if music_files:
    show_gui(music_files, music__folder)
else:
    print("No music files found in the selected folder.")







    