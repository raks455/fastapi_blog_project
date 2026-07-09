from fastapi import FastAPI,Depends,HTTPException
from database import engine,SessionLocal
from sqlalchemy.orm import Session
import model,schemas


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
@app.get("/")
def home():
    return {"message":"blog api  started"}

#create blog
@app.post("/blogs",response_model=schemas.BlogResponse)
def create_blog(blog:schemas.BlogCreate,db:Session=Depends(get_db)):
    new_blog=model.Blog(title=blog.title,content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get("/blogs",response_model=list[schemas.BlogResponse])
def getBlogs(db:Session=Depends(get_db)):
    return db.query(model.Blog).all()

#read only one blog
@app.get("/blogs/{id}",response_model=schemas.BlogResponse)
def getBlog(id:int,db:Session=Depends(get_db)):
    blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404,detail=f"blog with id {id} not found")
    return blog

@app.put("/blogs/{id}",response_model=schemas.BlogResponse)
def updateBlog(id:int,blog:schemas.BlogCreate,db:Session=Depends(get_db)):
    existing_blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not existing_blog:
        raise HTTPException(status_code=404,detail=f"blog with id {id} not found")
    existing_blog.title=blog.title
    existing_blog.content=blog.content
    db.commit()   
    return existing_blog

@app.delete("/blogs/{id}",response_model=schemas.BlogResponse)
def deleteBlog(id:int,db:Session=Depends(get_db)):
    blog=db.query(model.Blog).filter(model.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404,detail=f"blog with id {id} not found")
    db.delete(blog)
    db.commit()
    return blog