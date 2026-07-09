from pydantic import BaseModel

#input schemas
class BlogCreate(BaseModel):
    title:str
    content:str
    
#output schemas

class BlogResponse(BaseModel):
    id:int
    title:str
    content:str
    
    class  Config:
        from_attributes = True
        