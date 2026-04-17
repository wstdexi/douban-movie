import re
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from app.config.settings import settings
from app.database.migration import init_db
from app.database.session import SessionLocal
from app.models.movies import Movie


def fetch_page(start: int, timeout: int = 10) -> str:
    response = requests.get(
        settings.douban_base_url,
        headers=settings.douban_headers,
        params={"start": start},
        timeout=timeout,
    )
    response.raise_for_status()
    # Force UTF-8 to avoid Chinese text mojibake.
    response.encoding = "utf-8"
    return response.text


def _parse_votes(votes_text: str) -> int:
    cleaned = votes_text.replace(",", "").replace("，", "").strip()
    match = re.search(r"(\d+)", cleaned)
    return int(match.group(1)) if match else 0


def _extract_comments_text(item) -> str:
    star_spans = item.select("div.star span")
    for span in star_spans:
        text = span.get_text(strip=True)
        if "人评价" in text or "人评论" in text:
            return text

    # Fallback: parse full item text when DOM structure changes.
    full_text = item.get_text(" ", strip=True)
    match = re.search(r"(\d[\d,，]*)\s*人(?:评价|评论)", full_text)
    return f"{match.group(1)}人评价" if match else ""


def parse_movies(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    movies: List[Dict[str, str]] = []

    for item in soup.select("ol.grid_view li"):
        title_tag = item.select_one("span.title")
        rating_tag = item.select_one("span.rating_num")
        comment_text = _extract_comments_text(item)
        quote_tag = item.select_one("span.inq") or item.select_one("p.quote span")
        link_tag = item.select_one("div.hd a")

        movies.append(
            {
                "title": title_tag.get_text(strip=True) if title_tag else "",
                "rating": rating_tag.get_text(strip=True) if rating_tag else "",
                "comments_count": comment_text,
                "quote": quote_tag.get_text(strip=True) if quote_tag else "",
                "url": link_tag.get("href", "") if link_tag else "",
            }
        )

    return movies


def crawl_douban_top250(delay_seconds: float = 1.0) -> List[Dict[str, str]]:
    all_movies: List[Dict[str, str]] = []
    for start in range(0, 250, 25):
        try:
            html = fetch_page(start=start)
            page_movies = parse_movies(html)
            all_movies.extend(page_movies)
            print(f"已抓取 start={start}，本页 {len(page_movies)} 条")
        except requests.RequestException as exc:
            print(f"请求失败 start={start}: {exc}")
        time.sleep(delay_seconds)
    return all_movies


def save_movies(movies: List[Dict[str, str]]) -> int:
    upserted = 0
    with SessionLocal() as session:
        existing_map = {
            movie.url: movie for movie in session.scalars(select(Movie)).all() if movie.url
        }

        for movie in movies:
            if not movie["url"]:
                continue

            existing = existing_map.get(movie["url"])
            if existing:
                existing.title = movie["title"]
                existing.rating = float(movie["rating"]) if movie["rating"] else None
                existing.comments_count = _parse_votes(movie["comments_count"])
                existing.quote = movie["quote"]
            else:
                db_movie = Movie(
                    title=movie["title"],
                    rating=float(movie["rating"]) if movie["rating"] else None,
                    comments_count=_parse_votes(movie["comments_count"]),
                    quote=movie["quote"],
                    url=movie["url"],
                )
                session.add(db_movie)
                existing_map[movie["url"]] = db_movie
            upserted += 1

        session.commit()
    return upserted


def main() -> None:
    init_db()
    movies = crawl_douban_top250()
    upserted = save_movies(movies)
    print(f"抓取 {len(movies)} 条，入库/更新 {upserted} 条。")


if __name__ == "__main__":
    main()
