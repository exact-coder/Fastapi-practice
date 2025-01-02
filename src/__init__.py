from fastapi import FastAPI
from src.books.routes import book_router



version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Jahid hasan",
        "url": "https://github.com/exact-coder",
        "email": "hasanakash799@gmail.com"
    },
    # terms_of_service="httpS://example.com/tos",
    # openapi_url=f"{version_prefix}/openapi.json",
    # docs_url=f"{version_prefix}/docs",
    # redoc_url=f"{version_prefix}/redoc"
)



app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
