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
import pygame
pygame.init()
pygame.mixer.init()
import threading
from tkinter import ttk
current_song_length = 0





#----------------------------------------
ffmpeg_dir = os.path.join(os.path.dirname(__file__), "bin", "ffmpeg-7.1.1-essentials_build", "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_dir
os.environ["FFMPEG_BINARY"] = os.path.join(ffmpeg_dir, "ffmpeg.exe")
os.environ["FFPROBE_BINARY"] = os.path.join(ffmpeg_dir, "ffprobe.exe")
 #---------------------------------------

is_paused = False
current_song_path = None
last_index = -1
current_song_index = -1
song_list_wrapper = [[]]
global song_listbox
listbox_index = -1
global global_song_list






app_directory = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(app_directory, "bin", "ffmpeg-7.1.1-essentials_build", "bin", "ffmpeg.exe")
ffprobe_path = os.path.join(app_directory, "bin", "ffmpeg-7.1.1-essentials_build", "bin", "ffprobe.exe")

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path
print("ffmpeg and ffprobe configured at:", ffmpeg_path)
print("ffmpeg:", AudioSegment.converter)
print("ffprobe:", AudioSegment.ffprobe)








def play_song_threaded(path, status_callback=None, window=None):
    global current_song_path, is_paused
    current_song_path = current_song_path
    is_paused = False

    def convert_and_play():
        print("⏳ Converting and loading...")
        if status_callback:
            status_callback("⏳ Converting and loading...")

        # Remove temp.wav file if it already exists
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

        try:
            # Check if the file has valid ID3 metadata
            if path.endswith('.mp3'):
                audio = EasyID3(path)
                audio_title = audio.get('title', [None])[0]
                if audio_title is None:
                    raise ValueError(f"Missing ID3 tag (title) in {path}")
        except Exception as e:
            print(f"Error with {path}: {e}")
            if status_callback:
                status_callback(f"❌ Error: {e}")
            return

        # Convert to wav using pydub (supports .m4a and .mp3)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            temp_wav_path = tmp_file.name

        try:
            sound = AudioSegment.from_file(path)
            sound.export(temp_wav_path, format="wav")
            pygame.mixer.music.load(temp_wav_path)
            pygame.mixer.music.play()

            global current_song_length
            song = AudioSegment.from_file(temp_wav_path)
            current_song_length = len(song) / 1000




            if status_callback:
                status_callback(f"✅ Now playing:🎶")

            if listbox_index is not None:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(listbox_index)
                listbox.activate(listbox_index)
                listbox.see(listbox_index)
        except Exception as e:
            print(f"Error loading audio: {e}")
            if status_callback:
                status_callback(f"❌ Error loading audio: {e}")

    threading.Thread(target=convert_and_play).start()
     # duration in seconds

    #check_song_finished()







#def check_song_finished():
    #global main_window  # this is your tk window
    #if not pygame.mixer.music.get_busy() and not is_paused:
        #play_next_song()
    #else:
        #main_window.after(1000, check_song_finished)


#def play_next_song():
    #global current_song_path, is_paused, music_files, listbox_index, listbox, global_song_list, music__folder

    #if global_song_list:
        #listbox_index = (listbox_index + 1) % len(global_song_list)
        #next_song_path = os.path.join(music__folder, global_song_list[listbox_index][1])
        #current_song_path = next_song_path
        #is_paused = False
        #play_song_threaded(next_song_path)

        ## Also update listbox selection visually
        #listbox.selection_clear(0, tk.END)
        #listbox.selection_set(listbox_index)
        #listbox.activate(listbox_index)




#i have no idea about this code 
#but it works so i will keep it for now
#yooooo finallyyyyyyyyyyyyy its workinggggggggggggggg yeahhhhhhhhhhh
def setup_ffmpeg():
    app_directory = os.path.dirname(os.path.abspath(__file__))

# Set the FFmpeg and FFprobe paths relative to the app directory
    ffmpeg_path = os.path.join(app_directory, "bin", "ffmpeg-7.1.1-essentials_build", "bin", "ffmpeg.exe")
    ffprobe_path = os.path.join(app_directory, "bin", "ffmpeg-7.1.1-essentials_build", "bin", "ffprobe.exe")

# Set the FFmpeg paths for pydub
    

    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path

    # Get the base path where the script is located


    
    
    if os.path.exists(ffmpeg_path):
        AudioSegment.converter = ffmpeg_path  # Set ffmpeg path for pydub
        AudioSegment.ffprobe = ffprobe_path  # Set ffprobe path for pydub
        print(f"✅ ffmpeg and ffprobe configured at: {ffmpeg_path}")
    else:
        print("❌ ffmpeg not found in the bundled app!")




# Call this before playing .m4a files
setup_ffmpeg()

# Explicitly tell pydub where ffmpeg and ffprobe are


#for the music player
pygame.mixer.init()
print("🎧 Pygame mixer initialized.")

#for the music metadata
#asks the user to chose a folder or just use the default music folder
def choose_music_folder(d3fau1t = True):
    if d3fau1t:
        return os.path.join(os.path.expanduser("~"), "Music")
    
    return filedialog.askdirectory(title="Select Music Folder")
    
global_song_list = []
def list_music_files(folder_path):
    global_song_list.clear()  # Clears the list before adding again
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return []

    for file in os.listdir(folder_path):
        if file.endswith(('.mp3', '.m4a')):  # Check for mp3 and m4a files
            full_path = os.path.join(folder_path, file)
            try:
                # Check if file is valid and readable
                if not os.path.isfile(full_path):
                    print(f"Skipping invalid file: {file}")
                    continue

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
                    display_name = file  # Fallback to filename if no title

            except Exception as e:
                print(f"Error reading metadata for {file}: {e}")
                display_name = file  # Fallback to filename if metadata read fails

            global_song_list.append((display_name, file))  # Add the song to the list

    return global_song_list




    
#finds all the files with mp3 and save them


music__folder = choose_music_folder()
music_files = list_music_files(music__folder)


    


#GUI------------------------------#################
def show_gui(initial_song_list, music_folder):
    
    song_list_wrapper = [initial_song_list]


    window = tk.Tk()
    window.title("d1sc🎧")
    global main_window
    main_window = window

    

    def update_progress():
        if pygame.mixer.music.get_busy():
            current_pos = pygame.mixer.music.get_pos() / 1000  # in seconds
            if current_song_length:
                progress = (current_pos / current_song_length) * 100
                progress_var.set(progress)
        window.after(1000, update_progress)

    update_progress()




    



    top_frame = tk.Frame(window, bg="#1e1e2f")
    top_frame.pack(side="top", pady=10, anchor="w")

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

    status_label = tk.Label(
        window, text="🔈 Ready to play!",
        font=("Segoe UI", 14),
        fg="#f1f1f1", bg="#1e1e2f"
    )
    status_label.pack(pady=5)


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

    global listbox

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

    bottom_frame = tk.Frame(window, bg="#2a2a40")
    bottom_frame.pack(side="bottom", fill="x", pady=20)
    #to make the bottom frame fill the window

#to create proper listbox and add the songs to it
    def update_listbox(new_song_list):
        song_list_wrapper[0] = new_song_list  # Update the wrapper list
        listbox.delete(0, tk.END)  # Clear existing list
        for song in new_song_list:
            listbox.insert(tk.END, f" 🎵{song[0]}")


         
    def play_song(event):

        print("🔊 play_song triggered!")
        

        selected_index = listbox.curselection()
        if selected_index:
            real_index = selected_index[0]
            _, filename = song_list_wrapper[0][real_index]  # get actual file name from the original list
            song_path = os.path.join(music_folder, filename)
            current_song_index = real_index


            
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                play_song_threaded(song_path, status_callback=lambda msg: status_label.config(text=msg))
  # Use the threaded function
                print(f"▶️ Playing: {song_path}")


            except Exception as e:
                print(f"Failed to play: {song_path}")
                print(f"Error: {e}")

        global current_song_path, is_paused
        current_song_path = song_path
        is_paused = False







                
        
            # Update the label to show the currently playing song
    listbox.bind("<Double-Button-1>", play_song)
    last_index = -1

        

    def on_enter(e): change_btn.config(bg="#6c63ff")
    def on_leave(e): change_btn.config(bg="#3c3f58")

    
#to change button

    change_btn = tk.Button( 

    top_frame,
    text="📁Change Folder",
    command=change_folder,
    width=12,  # 
    height=1,  # 
    relief="solid",  # 
    bd=3,  # Border width
    highlightthickness=0,  #

    font=("Segoe UI", 10, "bold"),
    bg="#2a2a40",  #
    fg="#f1f1f1",  # Text color
    activebackground="#555577",  # 
    activeforeground="#ffffff",  #
    borderwidth=3,  # 
    padx=10,  # 
    pady=5,
    cursor="hand2" # 
        
        

    )
    change_btn.pack(side = "left", pady=10)
    change_btn.bind("<Enter>", on_enter)
    change_btn.bind("<Leave>", on_leave)


    def on_in(e): refresh_btn.config(bg="#6c63ff")
    def on_out(e): refresh_btn.config(bg="#3c3f58")

    # Add refresh button to reload the song list
    refresh_btn = tk.Button( 
    top_frame,
    text="🔄Refresh",
    command=lambda: update_listbox(list_music_files(music_folder)),
    width=12,  # 
    height=1,  #
    relief="solid",  
    bd=3,  #
    highlightthickness=0,
    font=("Segoe UI", 10, "bold"),  
    bg="#2a2a40",  #
    fg="#f1f1f1",  # Text color
    activebackground="#555577",  #
    activeforeground="#ffffff",  #
    borderwidth=3,  #
    padx=10,  #
    pady=5,
    cursor="hand2"  #

    
)
    def toggle_play_pause():
        global is_paused, current_song_path

        if current_song_path:
            if is_paused:
                pygame.mixer.music.unpause()
                is_paused = False
                status_label.config(text="▶️ Resumed")
            elif pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                is_paused = True
                status_label.config(text="⏸️ Paused")
            else:
                play_song_threaded(current_song_path, status_callback=lambda msg: status_label.config(text=msg))
                is_paused = False
                status_label.config(text="▶️ Replaying")
        else:
            status_label.config(text="🔇 No song loaded")



    
    play_pause_btn = tk.Button(
    bottom_frame,
    text="⏯️ Play/Pause",
    command=toggle_play_pause,
    width=12,
    height=1,
    relief="solid",
    bd=3,
    font=("Segoe UI", 10, "bold"),
    bg="#2a2a40",
    fg="#f1f1f1",
    activebackground="#555577",
    activeforeground="#ffffff",
    padx=10,
    pady=5,
    cursor="hand2"
)
    play_pause_btn.pack(side="left", pady=10)
    window.bind("<space>", lambda e: toggle_play_pause())





    refresh_btn.pack(side="left",pady=10)
    refresh_btn.bind("<Enter>", on_in)
    refresh_btn.bind("<Leave>", on_out)



    last_index = -1  # this will keep track of the last hovered index

    def on_listbox_hover(event):
        global last_index
        widget = event.widget
        index = widget.nearest(event.y)

        if index != last_index:
            if 0 <= last_index < widget.size():
                widget.itemconfig(last_index, bg="#2a2a40", fg="#f1f1f1")

        # Highlight new
            widget.itemconfig(index, bg="#6c63ff", fg="#ffffff")
            last_index = index



    def clear_listbox_hover():
        global last_index
        if 0 <= last_index < listbox.size():
            listbox.itemconfig(last_index, bg="#2a2a40", fg="#f1f1f1")
        last_index = -1
     

    #def check_song_finished():
        #if not pygame.mixer.music.get_busy() and not is_paused:
            #play_next_song()
        #else:
            #window.after(1000, check_song_finished)  # check again in 1 sec

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Scale(bottom_frame, variable=progress_var, from_=0, to=100,
                         orient="horizontal", length=300, style="Horizontal.TScale")

    progress_bar.pack(side='left', fill='x', expand=True,padx =10)


    listbox.bind("<Motion>", on_listbox_hover)
    listbox.bind("<Leave>", lambda e: clear_listbox_hover())

    style = ttk.Style()
    style.theme_use('default')

    style.configure("Horizontal.TScale",
    background="#1e1e2f",       # Match your app bg
    troughcolor="white",      # The track/bar area
    sliderthickness=10,         # Size of the handle
    sliderlength=10,            # Length of the handle
    borderwidth=0)

# Optionally, for darker thumb:
    style.map("Horizontal.TScale",
    background=[("active", "#6c63ff")],
    troughcolor=[("active", "#2a2a40")])







    update_listbox(initial_song_list)
#to update the listbox with the initial song list

    window.mainloop()

    

if music_files:
    show_gui(music_files, music__folder)
else:
    print("No music files found in the selected folder.")