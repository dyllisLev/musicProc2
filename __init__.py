import os

try:
    import shazamio
except:
    os.system("pip install --upgrade shazamio")

try:
    import mutagen
except:
    os.system("pip install mutagen")

try:
    import lxml
except:
    os.system("pip install lxml")
