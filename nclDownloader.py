#!/bin/python3

import requests

from bs4 import BeautifulSoup
from pprint import pprint
from sys import stdout

UA_STR: str = "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"


def validator(bookID: str) -> bool:
    if not bookID.startswith("N"):
        print("BookId should starts with 'N'")
        return False
    return True


def metadata_fetcher(bookID: str) -> dict:
    print("Fetching book data...")
    return {
        x: y
        for x, y in list(
            zip(
                *[
                    iter(
                        [
                            i.text.strip()
                            .replace("\u3000", "")
                            .replace("\n", "")
                            .replace("\xa0", "")
                            for i in (
                                BeautifulSoup(
                                    requests.get(
                                        f"https://taiwanebook.ncl.edu.tw/zh-tw/book/{bookID}",
                                        headers={"User-Agent": UA_STR},
                                    ).text,
                                    "html.parser",
                                )
                                .find_all("div", class_="row")[2]
                                .find_all("div")
                            )
                            if "JavaScript" not in i.text and "檢視電子書" not in i.text
                        ][2:]
                    )
                ]
                * 2
            )
        )
    }


def downloader(bookID: str) -> bool:
    ref = f"https://taiwanebook.ncl.edu.tw/pdfjs_dual/web/viewer.html?file=/ebkFiles/{bookID}/{bookID}.PDF&r2l=true"
    with requests.get(
        f"https://taiwanebook.ncl.edu.tw/ebkFiles/{bookID}/{bookID}.PDF",
        headers={
            "User-Agent": UA_STR,
            "Referer": ref,
        },
        stream=True,
    ) as req:
        if req.status_code != 200:
            print(f"Error! {req.status_code}")
            return False
        with open(f"{bookID}.pdf", "wb") as fp:
            total_size = int(req.headers.get("Content-Length"))
            print("Total " + str(total_size))
            chunk_size = 2048 * 4
            for i, chunk in enumerate(req.iter_content(chunk_size=chunk_size)):
                c = i * chunk_size / total_size * 100
                stdout.write(f"\r{round(c, 4)}%")
                stdout.flush()
                fp.write(chunk)
            fp.flush()
            fp.close()
        print("OK\n")
        return True


if __name__ == "__main__":
    if not validator(bookID := input("Input bookID:")):
        print("Error: BookID is Invalid")
        exit(1)
    for k, v in metadata_fetcher(bookID).items():
        print(f"{k} : {v}")
    print("-" * 16)
    if input("Download it ?[Y/N]") in ["Y", "y"]:
        downloader(bookID)
        exit(0)
    print("Abort.")
    exit(2)
