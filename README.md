# HTSTEM's Discord Bots

## HTSTEM-Bote  
Script file: `main.py`  
Arguments: `None`  
Requirements: `feedparser`, `discord.py`  
Files required: `bot-token.txt` (will use first line as token and ignore all other lines)  
Notes: Uses `videoURLS.txt` in the same directory as the script. This is automatically created by the script when not detected.  

## Joinbot  
Script file: `logbot.py`  
Arguments: `None`  
Requirements: `discord.py`  
Files required: `bot-token.txt` (will use first and second line as tokens and ignore all other lines)  
Notes: Creates folders called `bot-1` and sometimes `bot-2` which store user message counts. Folder structure: `./bot-<bot_number>/<server_id>/<month>/` containing files `<user_id>.txt` where the first line is the message count and the second line is the user's name.  
