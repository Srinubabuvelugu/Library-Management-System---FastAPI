from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.books import router as books_router
from routers.users import router as users_router
from routers.borrows import router as borrows_router


app = FastAPI(
    title="Library Management System",
    description="REST API for managing library books, members, and borrowing",
    version="1.0.0"
)

# include API Router
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(users_router)
app.include_router(borrows_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy"}