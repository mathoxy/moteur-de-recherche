from __future__ import annotations

import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.utils.document_metadata import normalize_publication_date, save_file_metadata


class SGGCrawler:
    """Crawler for downloading bulletin documents listed on the SGG page."""

    base_url = "https://www.sgg.gov.ma/BulletinOfficiel.aspx"
    ajax_url = "https://www.sgg.gov.ma/DesktopModules/MVC/TableListBO/BO/AjaxMethod"
    module_id = "2873"
    tab_id = "775"

    def __init__(self, nbre_pages: int = 1):
        self.nbre_pages = max(1, int(nbre_pages))
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def fetch_page(self, url: str, timeout: int = 20) -> Optional[str]:
        """Fetch a page and return its HTML text."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"Failed to fetch {url}: {exc}")
            return None

    def _get_request_verification_token(self) -> Optional[str]:
        """Extract the anti-forgery token required by the bulletin AJAX endpoint."""
        html = self.fetch_page(self.base_url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        token_input = soup.find("input", attrs={"name": "__RequestVerificationToken"})
        if token_input is None:
            return None

        token = token_input.get("value", "").strip()
        return token or None

    def get_bulletin_documents(self) -> List[dict[str, Any]]:
        """Extract bulletin PDF links and metadata from the SGG AJAX endpoint."""
        documents: List[dict[str, Any]] = []
        seen: set[str] = set()

        token = self._get_request_verification_token()
        if token is not None:
            try:
                response = self.session.post(
                    self.ajax_url,
                    data={"ModuleId": self.module_id, "TabId": self.tab_id},
                    headers={
                        "ModuleId": self.module_id,
                        "TabId": self.tab_id,
                        "RequestVerificationToken": token,
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": self.base_url,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                items = response.json()
                for item in items:
                    bo_url = item.get("BoUrl")
                    if not bo_url:
                        continue

                    absolute_url = urljoin(self.base_url, bo_url)
                    parsed = urlparse(absolute_url)
                    if not parsed.scheme.startswith("http"):
                        continue
                    if not parsed.path.lower().endswith(".pdf"):
                        continue
                    if absolute_url in seen:
                        continue

                    documents.append(
                        {
                            "title": f"Bulletin Officiel n° {item.get('BoNum', '')}".strip(),
                            "document_type": "Bulletin officiel",
                            "document_number": item.get("BoNum"),
                            "publication_date": normalize_publication_date(item.get("BoDate")),
                            "source_url": absolute_url,
                            "language": "fr",
                            "article": None,
                            "bo_id": item.get("BoId"),
                        }
                    )
                    seen.add(absolute_url)

                    if len(documents) >= self.nbre_pages:
                        break

                if documents:
                    return documents
            except (requests.RequestException, ValueError) as exc:
                print(f"Failed to fetch bulletin API data: {exc}")

        html = self.fetch_page(self.base_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "").strip()
            if not href:
                continue

            absolute_url = urljoin(self.base_url, href)
            parsed = urlparse(absolute_url)
            if not parsed.scheme.startswith("http"):
                continue
            if not parsed.path.lower().endswith(".pdf"):
                continue
            if absolute_url in seen:
                continue

            documents.append(
                {
                    "title": Path(parsed.path).stem,
                    "document_type": "Bulletin officiel",
                    "document_number": None,
                    "publication_date": None,
                    "source_url": absolute_url,
                    "language": "fr",
                    "article": None,
                    "bo_id": None,
                }
            )
            seen.add(absolute_url)

            if len(documents) >= self.nbre_pages:
                break

        return documents

    def get_bulletin_links(self) -> List[str]:
        """Backward-compatible helper that returns bulletin URLs only."""
        return [document["source_url"] for document in self.get_bulletin_documents()]

    def _safe_filename(self, url: str, content_type: str = "") -> str:
        """Build a filesystem-safe filename from a URL."""
        parsed = urlparse(url)
        name = Path(parsed.path).name
        if not name:
            digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
            name = f"{digest}.pdf" if "pdf" in content_type.lower() else f"{digest}.html"

        target = self.raw_dir / name
        suffix = target.suffix
        stem = target.stem
        counter = 1
        while target.exists():
            target = self.raw_dir / f"{stem}-{counter}{suffix}"
            counter += 1
        return target.name

    def _already_downloaded(self, url: str) -> bool:
        """Check whether this bulletin already exists in the raw directory."""
        return self._existing_download_path(url) is not None

    def _existing_download_path(self, url: str) -> Optional[Path]:
        """Return the first matching file already stored for this bulletin URL."""
        parsed = urlparse(url)
        name = Path(parsed.path).name
        if not name:
            return None

        stem = Path(name).stem
        suffix = Path(name).suffix
        for candidate in self.raw_dir.glob(f"{stem}*{suffix}"):
            if candidate.is_file():
                return candidate
        return None

    def download_bulletin(self, bulletin: dict[str, Any] | str) -> Optional[Path]:
        """Download one bulletin document into backend/data/raw."""
        if isinstance(bulletin, str):
            bulletin = {"source_url": bulletin}

        bulletin_link = bulletin["source_url"]
        existing_path = self._existing_download_path(bulletin_link)

        if existing_path is not None:
            sidecar_path = existing_path.with_suffix(".json")
            if not sidecar_path.exists():
                save_file_metadata(
                    existing_path,
                    {
                        "title": bulletin.get("title"),
                        "document_type": bulletin.get("document_type"),
                        "document_number": bulletin.get("document_number"),
                        "publication_date": bulletin.get("publication_date"),
                        "source_url": bulletin.get("source_url"),
                        "language": bulletin.get("language", "fr"),
                        "article": bulletin.get("article"),
                        "bo_id": bulletin.get("bo_id"),
                        "downloaded_at": datetime.now(timezone.utc).isoformat(),
                    },
                )

            print(f"Skipping already downloaded file: {bulletin_link}")
            return None

        try:
            with self.session.get(bulletin_link, stream=True, timeout=30) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                if "pdf" not in content_type.lower() and not urlparse(bulletin_link).path.lower().endswith(".pdf"):
                    print(f"Skipping non-PDF response for {bulletin_link} ({content_type})")
                    return None

                filename = self._safe_filename(bulletin_link, content_type)
                target_path = self.raw_dir / filename

                with target_path.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)

            save_file_metadata(
                target_path,
                {
                    "title": bulletin.get("title"),
                    "document_type": bulletin.get("document_type"),
                    "document_number": bulletin.get("document_number"),
                    "publication_date": bulletin.get("publication_date"),
                    "source_url": bulletin.get("source_url"),
                    "language": bulletin.get("language", "fr"),
                    "article": bulletin.get("article"),
                    "bo_id": bulletin.get("bo_id"),
                    "downloaded_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            print(f"Downloaded {bulletin_link} -> {target_path}")
            return target_path
        except requests.RequestException as exc:
            print(f"Failed to download {bulletin_link}: {exc}")
            return None

    def run(self) -> List[Path]:
        """Fetch bulletin links and download the requested number of documents."""
        print(f"Fetching bulletin links from {self.base_url}")
        bulletins = self.get_bulletin_documents()
        if not bulletins:
            print("No bulletin links found.")
            return []

        downloaded_files: List[Path] = []
        for bulletin in bulletins[: self.nbre_pages]:
            downloaded = self.download_bulletin(bulletin)
            if downloaded is not None:
                downloaded_files.append(downloaded)

        print(f"Finished at {datetime.now(timezone.utc).isoformat()}. Downloaded {len(downloaded_files)} file(s).")
        return downloaded_files


if __name__ == "__main__":
    crawler = SGGCrawler(nbre_pages=2)
    crawler.run()

