from fastapi import FastAPI,Depends,HTTPException,Query
from database import engine,SessionLocal
from sqlalchemy.orm import Session
import model,schemas
from auth import verify_token,create_access_token

model.Base.metadata.create_all(bind=engine)
app=FastAPI()

#DB dependencies
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
    #home
    
@app.post("/login")
def login():
    return {"access_token":create_access_token({"user":"admin"}),
                                        "token_type":"bearer"
            }
@app.get("/")
def home():
    return {"message":"blog api  started"}

#create blog
@app.post("/blogs",response_model=schemas.BlogResponse)
def create_blog(blog:schemas.BlogCreate,db:Session=Depends(get_db),user=Depends(verify_token)):
    new_blog=model.Blog(title=blog.title,content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get("/blogs")
def getBlogs(page:int=1,limit:int=10,search:str=Query(default=""),db:Session=Depends(get_db)):
    query=db.query(model.Blog)
    if search:
        query=query.filter(model.Blog.title.ilike(f"%{search}%"))
    total=query.count()
    start=(page-1)*limit
    blogs=query.offset(start).limit(limit).all()
    return {"page":page,"limit":limit,"total":total,"blogs":blogs}
    

#read only one blog
@app.get("/blogs/{id}",response_model=schemas.BlogResponse)
def getBlog(id:int,db:Session=Depends(get_db)):
    blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404,detail=f"blog with id {id} not found")
    return blog

@app.put("/blogs/{id}",response_model=schemas.BlogResponse)
def updateBlog(id:int,blog:schemas.BlogCreate,db:Session=Depends(get_db),user=Depends(verify_token)):
    existing_blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not existing_blog:
        raise HTTPException(status_code=404,detail=f"blog with id {id} not found")
    existing_blog.title=blog.title
    existing_blog.content=blog.content
    db.commit()   
    return existing_blog

@app.delete("/blogs/{id}",response_model=schemas.BlogResponse)
def deleteBlog(id:int,db:Session=Depends(get_db),user=Depends(verify_token)):
    blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404,detail=f"blog with id {id} not found")
    db.delete(blog)
    db.commit()
    return blog