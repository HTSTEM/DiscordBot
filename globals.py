TESTING = True  # Use this to toggle between production IDs and testing IDs

TOKEN_FILE = "bot-token.txt"
HTSTEM_BOTE_TOKEN_NUMBER = 0
GAMEBOT_TOKEN_NUMBER = 1

PREFIX = "sb?"

OWNER_ID = "140564059417346049"
HTSTEM_ID = "282219466589208576"
YT_ROLE_ID = "289942717419749377"
BOTE_SPAM = ["282500390891683841", "290757101914030080", "229595785346416640"]

MODERATOR_ROLE_ID_STEM = "282661854076076033"

CARY_YT_URL = "https://www.youtube.com/feeds/videos.xml?user=carykh"
VIDEO_ANNOUNCE_CHANNEL = "282225245761306624"

IMAGE_FORMATS = ["jpg", "jpeg", "gif", "png"]

DEVELOPERS = ["161508165672763392", "140564059417346049"]
DEVELOPERS_ERROR_PINGS = ["161508165672763392"]

if TESTING:
    OWNER_ID = "161508165672763392"
    HTSTEM_ID = "290573725366091787"
    YT_ROLE_ID = "320939806530076673"
    VIDEO_ANNOUNCE_CHANNEL = "290757101914030080"
    MODERATOR_ROLE_ID_STEM = "290573725366091787"

def clear_formatting(in_string):
    if not in_string.isspace():
        out_string = in_string.replace("`", "​`").replace("*", "​*").replace("_", "​_")  # .replace("", " ")
    else:
        out_string = "[empty string]"

    return out_string
