from datetime import datetime
from sqlmodel import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Book
from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.execute(statement,session)
        return result.scalars().all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)
        return result.scalars().first()

    async def create_book(
        self, book_data: BookCreateModel, session: AsyncSession
    ):
        book_data_dict = book_data.dict()  # .dict() is a more appropriate way to access the data from Pydantic models

        new_book = Book(**book_data_dict)

        new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d")


        session.add(new_book)
        await session.commit()

        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update:
            update_data_dict = update_data.dict()

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return None
