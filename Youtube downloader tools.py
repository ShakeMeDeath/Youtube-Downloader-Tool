import os
import subprocess
from yt_dlp import YoutubeDL

def DownloadSong(url):
    output_dir = "/home/shakemedeath/Music"

    yt_dlp_options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'writethumbnail': True,
        'noplaylist': True,
        'quiet': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }
        ]
    }

    with YoutubeDL(yt_dlp_options) as ydl:
        info = ydl.extract_info(url)

    song_name = info.get("track") or info.get("title", "Unknown Song")
    title = "".join(c for c in info.get("title", "Unknown Song") if c.isalnum() or c in " -_").strip()
    artist = info.get("artist", "Unknown Artist")

    upload_Date = info.get("upload_date", "Unknown Upload Date")
    if upload_Date != "Unknown Upload Date" and len(upload_Date) == 8:
        upload_Date = f"{upload_Date[:4]}-{upload_Date[4:6]}-{upload_Date[6:]}"
    else:
        upload_Date = "Unknown"

    base_path = os.path.join(output_dir, title)
    audio_path = base_path + ".mp3"

    possible_exts = [".jpg", ".webp", ".png"]
    thumbnail_path = None

    for ext in possible_exts:
        candidate = base_path + ext
        if os.path.exists(candidate):
            # Always rename thumbnail to JPG
            new_thumb_path = base_path + ".jpg"
            os.rename(candidate, new_thumb_path)
            thumbnail_path = new_thumb_path
            break

    if thumbnail_path is None:
        raise FileNotFoundError("Thumbnail image format not supported!")

    cropped_thumb = base_path + "_cover.jpg"

    # Crop the thumbnail to square
    subprocess.run([
        'ffmpeg', '-y', '-i', thumbnail_path,
        '-vf', 'crop=in_h:in_h',
        cropped_thumb
    ], check=True)

    # TEMP output file to avoid in-place overwrite
    temp_output = os.path.join(output_dir, f"{title}_tagged_temp.mp3")

    # ✅ Use the correct variable: cropped_thumb instead of undefined jpg_thumb
    subprocess.run([
        'ffmpeg', '-y', '-i', audio_path, '-i', cropped_thumb,
        '-map', '0:0', '-map', '1:0',
        '-c', 'copy',
        '-id3v2_version', '3',
        '-metadata:s:v', 'title=Album cover',
        '-metadata:s:v', 'comment=Cover (front)',
        '-metadata', f"title={song_name}",
        '-metadata', f"artist={artist}",
        '-metadata', f"date={upload_Date}",
        temp_output
    ], check=True)

    os.replace(temp_output, audio_path)
    os.remove(thumbnail_path)
    os.remove(cropped_thumb)

    print(f"\n✅ Done! {song_name} by {artist}\n")

# Example usage
URLs = ["https://youtu.be/Gn7-Abuh2DE?si=_a9itS_sL_XQRXuU"]

for song in URLs:
    DownloadSong(song)