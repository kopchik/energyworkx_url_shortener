import random
import string

from fastapi import FastAPI, HTTPException, Response
from pydantic import AnyHttpUrl, BaseModel, typing, validator


SHORTCODE_LENGTH = 6
ALLOWED_CHARS = set(string.ascii_lowercase + string.digits + "_")

app = FastAPI(
    title="Repo Octosearch", description="A code for an interview.", version="1.0.0"
)


class DuplicateShortcode(Exception):
    """The code is already in use"""


class Storage:
    allowed_chars = string.ascii_lowercase + string.digits + "_"
    code_lenght = 6

    def __init__(self):
        self.storage = {}

    def put(self, code, data):
        if code in self.storage:
            raise DuplicateShortcode
        self.storage[code] = data
        return code

    def get(self, code):
        return self.storage.get(code)


storage = Storage()


class UnknownShortcode(HTTPException):
    def __init__(self, detail):
        super().__init__(status_code=412, detail=detail)


class InvalidShortcode(HTTPException):
    def __init__(self, detail):
        super().__init__(status_code=412, detail=detail)


class AlreadyInUse(HTTPException):
    def __init__(self, detail):
        super().__init__(status_code=409, detail=detail)


########
# POST #
########


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    shortcode: typing.Optional[str]

    @validator("shortcode")
    def _validate_shortcode(cls, shortcode):
        validate_shortcode(shortcode)
        return shortcode


class ShortenResponse(BaseModel):
    shortcode: str


@app.post("/shorten", response_model=ShortenResponse, status_code=201)
async def post(request: ShortenRequest):
    shortcode = request.shortcode
    if not shortcode:
        shortcode = generate_unique_code()
    url = request.url
    try:
        shortcode = storage.put(code=shortcode, data=url)
    except DuplicateShortcode:
        raise AlreadyInUse(f"Code is already used: {shortcode}")
    return ShortenResponse(shortcode=shortcode)


def validate_shortcode(shortcode):
    if len(shortcode) != SHORTCODE_LENGTH:
        raise InvalidShortcode(f"length is not equal {SHORTCODE_LENGTH}")

    if not set(shortcode).issubset(ALLOWED_CHARS):
        raise InvalidShortcode(
            f"invalid characters in shortcode. Allowed characters: {ALLOWED_CHARS}"
        )


def generate_unique_code(self):
    while True:
        code = [random.choice(self.allowed_chars) for _ in range(self.code_lenght)]
        code = "".join(code)
        if not storage.get(code):
            return code


#######
# GET #
#######


@app.get("/{shortcode}", status_code=302)
async def get(shortcode: str, response: Response):
    url = storage.get(shortcode)
    if not url:
        raise HTTPException(status_code=404, detail=f"shortcode {shortcode} not found")

    response.headers["Location"] = str(url)
    return {}


#########
# STATS #
#########


@app.get("/{shortcode}/status")
async def get_stats():
    {
        "created": "2017-05-10T20:45:00.000Z",
        "lastRedirect": "2018-05-16T10:16:24.666Z",
        "redirectCount": 6,
    }
