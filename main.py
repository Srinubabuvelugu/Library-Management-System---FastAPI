from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.books import router as books_router



app = FastAPI(
    title="Library Management System",
    description="REST API for managing library books, members, and borrowing",
    version="1.0.0"
)

# include auth_routs
app.include_router(auth_router)
app.include_router(books_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy"}