from getUserSongs import get_songs
from dimensional import get_dimensional_emotion

def get_emotion():
    metadata = get_songs()
    emotion = get_dimensional_emotion(metadata)
    print(emotion)

if __name__ == "__main__":
    get_emotion()