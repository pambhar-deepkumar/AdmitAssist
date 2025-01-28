import xml.etree.ElementTree as ET

import markdown


class MarkdownLLMHelper:
    """
    A helper class to parse a Markdown file and provide structured access to its content.

    The class reads a Markdown file, converts it to HTML, and parses the headings and content
    into a tree structure. It provides methods to access the structure, search for text, and
    retrieve content snippets.

    Attributes:
    - _markdown_text: str, the original Markdown text
    - _root: Element, the root of the HTML ElementTree
    - _structure: list, the tree structure of headings and content

    Methods:
    - get_structure: return the tree structure of headings
    - get_section_by_title: return the node matching the specified title
    - get_content_of_section: return the content of the specified section
    - get_snippet_from_section: return a snippet of content from the specified section
    - get_all_headings: return a list of all headings in the document
    - search_text: search for a keyword in the document and return matches
    - get_snippet_around_section: return a snippet of content starting at the specified section

    """

    def __init__(self, markdown_path):
        """
        Initialize the helper by reading the Markdown file, converting it to HTML,
        and parsing headings and corresponding content into a tree structure.
        """
        with open(markdown_path, "r", encoding="utf-8") as f:
            self._markdown_text = f.read()

        # Convert the markdown to HTML
        html = markdown.markdown(self._markdown_text)

        # Parse the resulting HTML
        self._root = ET.fromstring(f"<div>{html}</div>")

        # Build a tree-like structure of headings
        self._structure = self._build_structure(self._root)

    def _build_structure(self, root):
        """
        Build a list-like tree structure from the HTML ElementTree root,
        detecting heading tags (h1, h2, h3, etc.) and their corresponding content.
        """
        structure_stack = []
        top_level = []

        for elem in list(root):
            tag = elem.tag.lower()

            if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(tag[1:])
                heading_text = "".join(elem.itertext()).strip()

                new_node = {
                    "level": level,
                    "title": heading_text,
                    "content": "",
                    "children": [],
                }

                if not structure_stack:
                    top_level.append(new_node)
                    structure_stack = [new_node]
                else:
                    while structure_stack and structure_stack[-1]["level"] >= level:
                        structure_stack.pop()

                    if not structure_stack:
                        top_level.append(new_node)
                        structure_stack = [new_node]
                    else:
                        structure_stack[-1]["children"].append(new_node)
                        structure_stack.append(new_node)
            else:
                text_content = "".join(elem.itertext()).strip()
                if text_content and structure_stack:
                    structure_stack[-1]["content"] += text_content + "\n"

        return top_level

    def get_structure(self):
        """
        Return a list of heading items (recursively) that shows the tree structure of the document.
        Each element is a dict with "level", "title", "content", and "children".
        """
        return self._structure

    def get_section_by_title(self, title, structure=None):
        """
        Return the dict node (heading) that matches the requested section title (exact match).
        """
        if structure is None:
            structure = self._structure

        for node in structure:
            if node["title"] == title:
                return node
            found = self.get_section_by_title(title, node["children"])
            if found:
                return found
        return None

    def get_content_of_section(self, title):
        """
        Return the content string (and children's content) for the specified heading title.
        Combines child sections' content as well.
        """
        node = self.get_section_by_title(title)
        if not node:
            return None
        return self._collect_section_text(node)

    def _collect_section_text(self, node):
        """
        Recursively gather content from this node and all its children.
        """
        combined_text = node["content"]
        for child in node["children"]:
            combined_text += f"\n[{child['title']}]\n{child['content']}"
            if child["children"]:
                combined_text += self._collect_section_text(child)
        return combined_text

    def get_snippet_from_section(self, title, char_count):
        """
        Return up to 'char_count' characters from the specified section only.
        """
        full_content = self.get_content_of_section(title)
        if not full_content:
            return None
        return full_content[:char_count]

    def get_all_headings(self):
        """
        Return a list of (title, level) from all headings in the document, flattening the tree.
        """
        results = []

        def walk(nodes):
            for n in nodes:
                results.append((n["title"], n["level"]))
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)
        return results

    def search_text(self, keyword):
        """
        Return a list of matches (title, text snippet containing the keyword).
        This is a simple rough search. Could be refined for LLM usage.
        """
        matches = []
        all_nodes = []

        def walk(nodes):
            for n in nodes:
                all_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)

        for node in all_nodes:
            content = node["content"]
            if keyword.lower() in content.lower():
                snippet = self._extract_around_keyword(content, keyword)
                if snippet:
                    matches.append({"title": node["title"], "snippet": snippet})
        return matches

    def _extract_around_keyword(self, text, keyword, window=40):
        """
        Return a snippet of 'text' around the first occurrence of 'keyword'
        with 'window' characters of context on each side.
        """
        idx = text.lower().find(keyword.lower())
        if idx == -1:
            return None
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        return text[start:end]

    def get_snippet_around_section(self, title, char_count):
        """
        Retrieve characters starting at the specified heading and continue
        through subsequent headings until 'char_count' characters are accumulated.
        """
        flattened_nodes = []

        def walk(nodes):
            for n in nodes:
                flattened_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)

        start_index = None
        for i, node in enumerate(flattened_nodes):
            if node["title"] == title:
                start_index = i
                break
        if start_index is None:
            return None

        snippet = ""
        for node in flattened_nodes[start_index:]:
            remaining = char_count - len(snippet)
            if remaining <= 0:
                break

            content_piece = node["content"]
            if len(content_piece) < remaining:
                snippet += content_piece
            else:
                snippet += content_piece[:remaining]
                break

        return snippet
