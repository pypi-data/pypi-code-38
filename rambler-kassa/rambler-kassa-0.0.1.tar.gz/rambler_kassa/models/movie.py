from datetime import date
from pydantic import BaseModel, validator
from typing import List, Optional


class Movie(BaseModel):
    OriginalName: str
    Genre: List[str]
    Country: List[str]
    ViewCountDaily: int
    AgeRestriction: str
    Thumbnail: str
    Cast: List[str]
    Description: str
    Director: str
    CreatorName: Optional[str]
    CreatorObjectID: Optional[int]
    Year: str
    Duration: str
    HorizonalThumbnail: Optional[str]
    IsNonStop: bool
    SubCreationIDs: List[int]
    Rating: str
    Trailers: Optional[str]
    Frames: Optional[str]
    ReleaseDate: date
    KinoplanID: Optional[int]
    ObjectID: int
    ClassType: str
    Name: str
    AfishaClassID: int
    AfishaObjectID: int

    @validator('Genre', 'Country', 'Cast', pre=True, whole=True)
    def str_to_list(cls, v):
        res = v.split(',')
        if not res or not res[0]:
            return []
        return res
