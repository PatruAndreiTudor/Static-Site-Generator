import unittest
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):

    def test_1(self):
        node=HTMLNode(props={"a": "b"})
        assert node.props_to_html() == ' a="b"'
    
    def test_2(self):
        node=HTMLNode(props={"a": "b", "c": "d"})
        assert node.props_to_html() == ' a="b" c="d"'

    def test_3(self):
        node=HTMLNode(props={})
        assert node.props_to_html() == ""

    def test_4(self):
        node=LeafNode("p","Hello, world!")
        self.assertEqual(node.to_html(),"<p>Hello, world!</p>")

    def test_5(self):
        node=LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(),'<a href="https://www.google.com">Click me!</a>')

    def test_6(self):
        node=LeafNode("a", "Click me!", {"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.to_html(),'<a href="https://www.google.com" target="_blank">Click me!</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    def test_7(self):
        grandchild_12=LeafNode("c", "hello")
        child_2=LeafNode("d","world", {"key" : "value"})
        child_1=ParentNode("b", [grandchild_12])
        parent_node=ParentNode("a", [child_1 , child_2])
        self.assertEqual(
            parent_node.to_html(),
            '<a><b><c>hello</c></b><d key="value">world</d></a>'
        )