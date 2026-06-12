import os
from split import *
from textnode import *
from htmlnode import *
from pathlib import Path

def extract_title(markdown: str) -> str:
    splitted=markdown.split("\n")
    for line in splitted:
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("no h1 heading found")


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    file_obj=open(from_path)
    stored_from=file_obj.read()
    template_obj=open(template_path)
    stored_template=template_obj.read()
    html_text=markdown_to_html_node(stored_from)
    html_string=html_text.to_html()
    page_title=extract_title(stored_from)
    path_dir=os.path.dirname(dest_path)
    os.makedirs(path_dir, exist_ok=True)
    replaced_template_1= stored_template.replace("{{ Title }}", page_title)
    replaced_template_2=replaced_template_1.replace("{{ Content }}", html_string)
    replaced_template_3=replaced_template_2.replace('href="/', f'href="{basepath}')
    replaced_template_4=replaced_template_3.replace('src="/', f'src="{basepath}')
    with open(dest_path, mode="w") as f:
        f.write(replaced_template_4)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    content_path=Path(dir_path_content)
    for path_object in content_path.iterdir():
        dest_object= Path(dest_dir_path)
        dst= dest_object / path_object.name
        if path_object.is_file():
            dst=dst.with_suffix(".html")
            generate_page(path_object, template_path, dst, basepath)
        else:
            generate_pages_recursive(path_object, template_path, dst, basepath)


 