# URL shortener

## Usage

Create and activate a virtual environment. The run the followwing commands from root directory of this repository:
```
pip install -r requirements.txt
pytest
uvicorn url_shortener:app --workers 1
```

By default the API is available on http://127.0.0.1:8000/ .
The automatically created documentation is on http://127.0.0.1:8000/docs .


## Quirks

1. No storage persistence
1. The storage is not shared between workers, use only one worker when
1. Code could be better split into modules
1. Little to no documentation


