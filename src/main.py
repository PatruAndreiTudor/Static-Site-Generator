from textnode import TextNode,TextType
from copystatic import *
from gencontent import *

def main():
    prepare("static", "public")
    generate_pages_recursive("content", "template.html", "public")

main()