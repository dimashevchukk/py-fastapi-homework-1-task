import math

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, MovieModel
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter()


@router.get(
    "/movies/",
    response_model=MovieListResponseSchema,
)
async def get_movies(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
) -> MovieListResponseSchema:
    total_items = int(await db.scalar(select(func.count()).select_from(MovieModel)))
    if total_items == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found.",
        )

    total_pages = math.ceil(total_items / per_page)
    if page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found.",
        )

    offset = (page - 1) * per_page
    res = await db.execute(select(MovieModel).offset(offset).limit(per_page))
    movies = res.scalars().all()

    prev_page = f"/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = f"/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema,
)
async def get_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db)
) -> MovieDetailResponseSchema:
    movie = await db.get(MovieModel, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )

    return movie
