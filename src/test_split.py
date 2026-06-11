import unittest
import re
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import LeafNode
from split import *
class TestSplit(unittest.TestCase):

    def test_1(self):
        example=split_nodes_delimiter(
            [TextNode("This is a _text_ node", TextType.TEXT)],
            "_",
            TextType.ITALIC
            )
        self.assertEqual(example,[TextNode(
            "This is a ", TextType.TEXT), TextNode("text", TextType.ITALIC), TextNode(" node", TextType.TEXT)])
    
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_image_2(self):
        matches = extract_markdown_images(
            "First part ![picture of us](https://imgur.com/something) second part ![pic 2](https://imgur.com/another)"
        )
        self.assertListEqual([("picture of us", "https://imgur.com/something"),("pic 2","https://imgur.com/another")], matches)

    def test_link(self):
        matches= extract_markdown_links("unos [numero uno](https://imgur.com/a) dos [numero dos](https://imgur.com/b)")
        self.assertListEqual([("numero uno", "https://imgur.com/a"),("numero dos","https://imgur.com/b")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_links(self):
        node= [
            TextNode("Hello [click this!](gif1.com) and [this](gif2.com)", TextType.TEXT),
            TextNode("This is bold", TextType.BOLD),
            TextNode("Hello again [click this!](gif3.com) but don't forget this", TextType.TEXT),
            TextNode("This is text but without links", TextType.TEXT)
            ]
        new_nodes=split_nodes_link(node)

        self.assertListEqual(
            [
               TextNode("Hello ", TextType.TEXT), 
               TextNode("click this!", TextType.LINK, "gif1.com"),
               TextNode(" and ", TextType.TEXT), 
               TextNode("this", TextType.LINK, "gif2.com"),
               TextNode("This is bold", TextType.BOLD),
               TextNode("Hello again ", TextType.TEXT),
               TextNode("click this!", TextType.LINK, "gif3.com"),
               TextNode(" but don't forget this", TextType.TEXT),
               TextNode("This is text but without links", TextType.TEXT)
            ],
            new_nodes,
        )
    
    def test_text_to_textnodes(self):
        node= text_to_textnodes(
            "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ],
        node
        )

    def test_markdown_to_blocks(self):
        md="""
          first  

   

                      second


                   third        
        """
        blocks=markdown_to_blocks(md)

        self.assertEqual(["first","second","third"],blocks)
        
    def test_markdown_to_blocks_2(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    def test_block_to_block_type_1(self):
        block= block_to_block_type("1. one\n2. two\n3. three")
        self.assertEqual(block, BlockType.ORDERED_LIST)

    def test_block_to_block_type_2(self):
        block= block_to_block_type("- one\n- two\n- three")
        self.assertEqual(block, BlockType.UNORDERED_LIST)
    
    def test_block_to_block_type_3(self):
        block= block_to_block_type(">one\n>two\n> three")
        self.assertEqual(block, BlockType.QUOTE)
    
    def test_block_to_block_type_4(self):
        block= block_to_block_type("```\n one```")
        self.assertEqual(block, BlockType.CODE)
    
    def test_block_to_block_type_5(self):
        block= block_to_block_type("##### something something")
        self.assertEqual(block, BlockType.HEADING)
    
    def test_block_to_block_type_6(self):
        block= block_to_block_type("unu doi")
        self.assertEqual(block, BlockType.NORMAL)
    
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_orderedlist(self):
        md = """
1. one
2. two
3. three
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>one</li><li>two</li><li>three</li></ol></div>",
        )

    def test_unorderedlist(self):
        md = """
- one
- two
- three
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>one</li><li>two</li><li>three</li></ul></div>",
        )

    def test_heading(self):
        md = """
##### title
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h5>title</h5></div>",
        )
    
    def test_quote(self):
        md = """
> big quote
> small quote
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>big quote small quote</blockquote></div>",
        )


