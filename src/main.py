from textnode import TextNode,TextType
from copystatic import *
from gencontent import *
import sys


def main():
    if len(sys.argv)>1:
        basepath=sys.argv[1]
    else:
        basepath = "/"
    if not basepath.endswith("/"):
        basepath= basepath + "/"
    prepare("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

main()