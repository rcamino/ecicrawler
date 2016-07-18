import codecs
import os
import re

from lxml.etree import HTMLParser, parse


blanck_re = re.compile(r"[\n\r\t]+")


def append_text(old_text, new_text):
    if len(new_text) == 0:
        return old_text
    elif len(old_text) == 0:
        return new_text
    else:
        return old_text + "\n" + new_text


def extract_text(html_file_path):
    with codecs.open(html_file_path, "r", "utf8") as html_file:
        dom = parse(html_file, parser=HTMLParser(encoding="utf8"))
    lines = dom.xpath("//*[not(self::style) and not(self::script)]/text()")
    lines = map(lambda line: blanck_re.sub("", line), lines)
    lines = map(lambda line: line.strip(), lines)
    lines = filter(lambda line: len(line) > 0, lines)
    return "\n".join(lines)


def extract_text_recursively(directory_path):
    text = ""
    for file_name in os.listdir(directory_path):
        if file_name.startswith("."):
            continue
        file_path = os.path.join(directory_path, file_name)
        if os.path.isdir(file_path):
            new_text = extract_text_recursively(file_path)
        else:
            new_text = extract_text(file_path)
        text = append_text(text, new_text)
    return text


def extract_text_by_year(source_directory_path, target_directory_path):
    if not os.path.exists(target_directory_path):
        os.makedirs(target_directory_path)
    for file_name in os.listdir(source_directory_path):
        if file_name.endswith(".html"):
            source_file_path = os.path.join(source_directory_path, file_name)
            text = extract_text(source_file_path)
            year = file_name[:-len(".html")]
            year_directory = os.path.join(source_directory_path, year)
            if os.path.isdir(year_directory):
                text = append_text(text, extract_text_recursively(year_directory))
            target_file_path = os.path.join(target_directory_path, year + ".txt")
            with codecs.open(target_file_path, "w", "utf8") as target_file:
                target_file.write(text)


if __name__ == "__main__":
    extract_text_by_year("data/web", "data/text")
