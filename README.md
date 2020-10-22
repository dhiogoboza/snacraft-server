<img src="/pictures/icon.png?raw=true" align="right" title="Snacraft Logo" width="120">

# Snacraft Server
[![License: MIT](https://img.shields.io/badge/license-Apache%202-blue.svg?style=flat)](https://opensource.org/licenses/Apache-2.0) [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dhiogoboza/snacraft-server/issues)

This project is the server side source from Snacraft game. This game is a classical snake multiplayer game. It is available in the [web](http://classic-snakeio.appspot.com/) and [Google Play](https://play.google.com/store/apps/details?id=io.snacraft.game).

## Dependencies

It is required `gunicorn` and `python2`. To install `gunicorn` type:
```
sudo apt install gunicorn
```

To solve python dependencies use this option if you want run in an virtual environment with `pipenv`:
```
pipenv --two shell
```

It is also possible to install dependencies in your system:
```
pip install -r requirements.txt
```

## Running

To run in development mode type:

```
gunicorn -k flask_sockets.worker main:app
```

## Pictures

<img src="/pictures/screenshot01.png?raw=true">
<img src="/pictures/screenshot02.png?raw=true">
<img src="/pictures/screenshot03.png?raw=true">
