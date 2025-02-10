<h1 align="center">"The Notes" -<a href="https://158.160.135.170/" target="_blank"> site to conver note sheets into music</a> 
<img src="https://github.com/blackcater/blackcater/blob/main/images/Hi.gif" height="32"/></h1>
<h3 align="center"><i> " Real magic in a couple of seconds! " </i></h3>
<hr>
To start the server:

```
python main.py
```

The weights of the model have already been uploaded to the <i> web/backend/neurak_network_utils/wghd </i> folder, but if you have a problem installing them, you can download them from Google Drive. To install use this:

```
gdown --folder https://drive.google.com/drive/folders/1C30EmNiFWdherD9xYbR6d89r27-sit6E --remaining-ok
``` 

:white_check_mark: the code has passed all flake8 checks

## Short description

The Notes is a web application that uses a neural network to automatically recognize sheet music and play it back in MP3 format. The project aims to simplify the process of converting traditional sheet music into digital format, which can be useful for musicians, music teachers, software developers and people with visual problems. Key components include a neural network for recognizing musical symbols, a module for converting notes to MP3, and a user-friendly graphical interface.

## Dependencies
- [ ]  **os;**
- [ ] Neural Network:
  - torch;
  - torchvision;
- [ ] DataBase:
  - sqlalchemy;
- [ ] Web:
  - fastapi;
  - gdown (for weights);
  - authx (for token);
- [ ] Note recognition:
  - PIL (pillow);
  - music21.

## Video presentation
...
