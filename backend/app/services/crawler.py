from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


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

    def get_bulletin_links(self) -> List[str]:
        """Extract bulletin PDF links from the SGG AJAX endpoint."""
        links: List[str] = []
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

                    links.append(absolute_url)
                    seen.add(absolute_url)

                    if len(links) >= self.nbre_pages:
                        break

                if links:
                    return links
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

            links.append(absolute_url)
            seen.add(absolute_url)

            if len(links) >= self.nbre_pages:
                break

        return links

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
        parsed = urlparse(url)
        name = Path(parsed.path).name
        if not name:
            return False

        stem = Path(name).stem
        suffix = Path(name).suffix
        return any(self.raw_dir.glob(f"{stem}*{suffix}"))

    def download_bulletin(self, bulletin_link: str) -> Optional[Path]:
        """Download one bulletin document into backend/data/raw."""
        if self._already_downloaded(bulletin_link):
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

            print(f"Downloaded {bulletin_link} -> {target_path}")
            return target_path
        except requests.RequestException as exc:
            print(f"Failed to download {bulletin_link}: {exc}")
            return None

    def run(self) -> List[Path]:
        """Fetch bulletin links and download the requested number of documents."""
        print(f"Fetching bulletin links from {self.base_url}")
        links = self.get_bulletin_links()
        if not links:
            print("No bulletin links found.")
            return []

        downloaded_files: List[Path] = []
        for bulletin_link in links[: self.nbre_pages]:
            downloaded = self.download_bulletin(bulletin_link)
            if downloaded is not None:
                downloaded_files.append(downloaded)

        print(f"Finished at {datetime.now(timezone.utc).isoformat()}. Downloaded {len(downloaded_files)} file(s).")
        return downloaded_files


if __name__ == "__main__":
    crawler = SGGCrawler(nbre_pages=2)
    crawler.run()

