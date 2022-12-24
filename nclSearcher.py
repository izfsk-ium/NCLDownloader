#!/bin/python3

"""
Search NCL Library
"""

from bs4 import BeautifulSoup

from rich.console import Console
from rich.table import Column, Table
from json import dump

import requests

UA_STR: str = "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"
BASE_URL: str = (
    "https://taiwanebook.ncl.edu.tw/zh-tw/search/all/%22{keyWord}%22/all/asc/grid/1"
)


class Searcher:
    def __init__(self, keyWord: str) -> None:
        self.keyWord: str = keyWord
        self.baseURL: str = f"https://taiwanebook.ncl.edu.tw/zh-tw/search/all/%22{self.keyWord}%22/all/asc/grid/"
        self.totalPage: int = self.getTotalPageNumber()

        print("Total Pages:" + str(self.totalPage))

    def getPageContent(self, pageNumber):
        return requests.get(
            f"{self.baseURL}{pageNumber}", headers={"User-Agent": UA_STR}
        )

    def getTotalPageNumber(self):
        try:
            return len(
                BeautifulSoup(self.getPageContent(1).text, "html.parser")
                .find_all("select")[0]
                .find_all("option")
            )
        except IndexError:
            print("Nothing found!")
            exit(1)

    def processPages(self):
        for number in range(1, self.totalPage + 1):
            yield [
                {
                    "ID": i.find("a", class_="header")
                    .attrs.get("href", "Unknown/Unknown")
                    .split("/")[-1],
                    "Title": i.find("a", class_="header").text,
                    "Author": i.find("span", class_="author").text,
                    "Date": i.find("span", class_="date").text,
                    "Publisher": i.find("span", class_="publisher").text,
                }
                for i in BeautifulSoup(
                    self.getPageContent(number).text, "html.parser"
                ).find_all("div", class_="item")[1:]
            ]

def saver(raw: any):
    with open("search_result.json", "w") as fp:
        dump(raw, fp, ensure_ascii=False)
        fp.flush()
        fp.close()


if __name__ == "__main__":
    console = Console()
    keyWord: str = input("Input search keyword:").strip()
    all_items = list()

    for page_items in Searcher(keyWord).processPages():
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID")
        table.add_column("Title", justify="left")
        table.add_column("Author", justify="left")
        table.add_column("Date", justify="left")
        table.add_column("Publisher", justify="left")

        for item in page_items:
            table.add_row(
                item["ID"],
                item["Title"],
                item["Author"],
                item["Date"],
                item["Publisher"],
            )
            all_items.append(item)
        console.print(table)
        try:
            input("Press any key to continue...")
        except KeyboardInterrupt:
            saver(all_items)

        saver(all_items)
