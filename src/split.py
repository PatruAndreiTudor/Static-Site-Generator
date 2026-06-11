from textnode import *
from htmlnode import *
import re
from enum import Enum

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) ->list[TextNode]:
    result=[]
    for node in old_nodes:
        if node.text_type!=TextType.TEXT:
            result.append(node)
        else:
            splitted=node.text.split(delimiter)
            if len(splitted)%2==0:
                raise ValueError("invalid markdown, formatting section not closed with the delimiter")
            new_nodes=[]
            for i,part in enumerate(splitted):
                if part == "":
                    continue
                if i%2==0:
                    new_nodes.append(TextNode(part,TextType.TEXT))
                else:
                    new_nodes.append(TextNode(part,text_type))
            result.extend(new_nodes)
        
    return result
         
def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    matches=re.findall(r"!\[([^\]]*)]\(([^\)]*)\)", text)
    return matches

def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    matches=re.findall(r"\[([^\]]*)]\(([^\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes=[]
    for node in old_nodes:
        if node.text_type!=TextType.TEXT:
            new_nodes.append(node)
        else:
            extracted=extract_markdown_images(node.text)
            if extracted==[]:
                new_nodes.append(node)
                continue
            remaining_text=node.text
            for image in extracted: 
                image_split= remaining_text.split(f"![{image[0]}]({image[1]})", 1)
                if image_split[0] != "":
                    new_nodes.append(TextNode(image_split[0],TextType.TEXT)) 
                new_nodes.append(TextNode(image[0],TextType.IMAGE,image[1]))
                remaining_text=image_split[1]
            if remaining_text != "":
                new_nodes.append(TextNode(remaining_text,TextType.TEXT))
    return new_nodes




def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes=[]
    for node in old_nodes:
        if node.text_type !=TextType.TEXT:
            new_nodes.append(node)
        else:
            extracted=extract_markdown_links(node.text)
            if extracted==[]:
                new_nodes.append(node)
                continue
            remaining_text=node.text
            for link in extracted:
                link_split=remaining_text.split(f"[{link[0]}]({link[1]})", 1)
                if link_split[0] != "":
                    new_nodes.append(TextNode(link_split[0],TextType.TEXT))
                new_nodes.append(TextNode(link[0],TextType.LINK,link[1]))
                remaining_text= link_split[1]
            if remaining_text!="":
                new_nodes.append(TextNode(remaining_text,TextType.TEXT))
    return new_nodes

def text_to_textnodes(text: str) ->list[TextNode]:
    new_nodes=[TextNode(text, TextType.TEXT)]
    new_nodes=split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes=split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
    new_nodes=split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes=split_nodes_image(new_nodes)
    new_nodes=split_nodes_link(new_nodes)
    return new_nodes

def markdown_to_blocks(markdown: str) -> list[str]:
    splitted= markdown.split("\n\n")
    
    result=[]
    for string in splitted:
        stripped=string.strip()
        if stripped=="":
            continue
        result.append(stripped)
    return result

class BlockType(Enum):
    PARAGRAPH="paragraph"
    HEADING="heading"
    CODE="code"
    QUOTE="quote"
    UNORDERED_LIST="unordered_list"
    ORDERED_LIST="ordered_list"
    NORMAL="normal"

def block_to_block_type(block: str) ->BlockType:
    if block.startswith(("# ","## ","### ","#### ","##### ","###### ")):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    splitted=block.split("\n")    
    if all(line.startswith(("> ", ">")) for line in splitted):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in splitted):
        return BlockType.UNORDERED_LIST
    if all(line.startswith(f"{i+1}. ") for i,line in enumerate(splitted)):
        return BlockType.ORDERED_LIST
    return BlockType.NORMAL

def count_helper(block: str) -> int:
    count=0
    for char in block:
        if char=="#":
            count+=1
        else:
            break
    return count

def text_to_children_helper(text: str) ->list[HTMLNode]:
    text_nodes=text_to_textnodes(text)
    children=[]
    for node in text_nodes:
        children.append(text_node_to_html_node(node))
    return children

def block_to_html_node(block: str) ->HTMLNode:
    block_type=block_to_block_type(block)
    if block_type ==BlockType.NORMAL:
        replaced=" ".join(block.split("\n"))
        children=text_to_children_helper(replaced)
        return ParentNode("p", children)
    if block_type ==BlockType.HEADING:
        count=count_helper(block)
        text=block[count+1:]
        children=text_to_children_helper(text)
        return ParentNode(f"h{count}",children)
    if block_type ==BlockType.CODE:
        
        code_split=block.split("\n")
        text="\n".join(code_split[1:-1]) + "\n"
        text_node_code=TextNode(text,TextType.TEXT)
        html_node_code=text_node_to_html_node(text_node_code)
        code_node= ParentNode("code",[html_node_code])
        pre_node= ParentNode("pre", [code_node])
        return pre_node
    if block_type ==BlockType.QUOTE:
        quote_split=block.split("\n")
        quote_cleaned=[]
        for quote in quote_split:
            cquote=quote.lstrip("> ")
            quote_cleaned.append(cquote)
        rejoined=" ".join(quote_cleaned)
        children=text_to_children_helper(rejoined)
        return ParentNode("blockquote", children)
    if block_type ==BlockType.UNORDERED_LIST:
        splitted=block.split("\n")
        cleaned=[]
        for line in splitted:
            stripped=line[2:].strip()
            node=text_to_children_helper(stripped)
            unord_node= ParentNode("li",node)
            cleaned.append(unord_node)
        return ParentNode("ul", cleaned)
    if block_type ==BlockType.ORDERED_LIST:
        splitted=block.split("\n")
        cleaned=[]
        for line in splitted:
            stripped=line.split(". ", 1)
            node=text_to_children_helper(stripped[1])
            unord_node= ParentNode("li",node)
            cleaned.append(unord_node)
        return ParentNode("ol", cleaned)

def markdown_to_html_node(markdown: str) ->ParentNode:
    blocks=markdown_to_blocks(markdown)
    all_nodes=[]
    for block in blocks:
        node=block_to_html_node(block)
        all_nodes.append(node)
    return ParentNode("div",all_nodes)






