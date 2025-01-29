import re
import xml.etree.ElementTree as ET

import markdown

try:
    from difflib import SequenceMatcher

    HAS_DIFFLIB = True
except ImportError:
    HAS_DIFFLIB = False


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
    - boolean_search: return matches of headings/content using simple Boolean logic (AND/OR)
    - fuzzy_search: return approximate matches using a ratio check (requires difflib)
    - get_highlighted_snippet: return a snippet highlighting matches for a given keyword
    """

    def __init__(self, markdown_path):
        """
        Initialize the helper by reading the Markdown file, converting it to HTML,
        and parsing headings and corresponding content into a tree structure.
        """
        with open(markdown_path, "r", encoding="utf-8") as f:
            self._markdown_text = f.read()

        html = markdown.markdown(self._markdown_text)
        self._root = ET.fromstring(f"<div>{html}</div>")
        self._structure = self._build_structure(self._root)

    def _build_structure(self, root):
        """
        Build a list-like tree structure from the HTML ElementTree root,
        detecting heading tags (h1, h2, h3, h4, h5, h6) and their corresponding content.
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

    def get_markDown(self):
        return self._markdown_text

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

    def _flatten_structure(self):
        """
        Flatten the hierarchical structure into a list of nodes for easier traversal.
        """
        flattened_nodes = []

        def walk(nodes):
            for n in nodes:
                flattened_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)
        return flattened_nodes

    def fuzzy_match_heading_and_retrieve_lines(
        self, keyword, num_lines=5, ratio_threshold=0.6
    ):
        """
        Fuzzily match a heading based on the provided keyword and retrieve `num_lines` lines
        of content starting from the matched heading. The content can span across subsequent sections.

        Args:
            keyword (str): The keyword to fuzzily match with headings.
            num_lines (int): The number of lines to retrieve from the matched heading onward.
            ratio_threshold (float): The minimum similarity ratio for fuzzy matching.

        Returns:
            dict: A dictionary containing the matched heading title and retrieved content.
                  Returns None if no match is found.
        """
        flattened_nodes = self._flatten_structure()

        # Find the best fuzzy match for the heading
        best_match = None
        best_ratio = 0.0

        for node in flattened_nodes:
            similarity = SequenceMatcher(
                None, node["title"].lower(), keyword.lower()
            ).ratio()
            if similarity > best_ratio and similarity >= ratio_threshold:
                best_match = node
                best_ratio = similarity

        if not best_match:
            return None  # No suitable match found

        # Retrieve content starting from the matched heading
        start_index = flattened_nodes.index(best_match)

        retrieved_content = []

        for node in flattened_nodes[start_index:]:
            lines = node["content"].splitlines()
            retrieved_content.extend(lines)

            # Stop once we have enough lines
            if len(retrieved_content) >= num_lines:
                break

        # Trim to the required number of lines
        retrieved_content = retrieved_content[:num_lines]

        return {
            "matched_heading": best_match["title"],
            "content": "\n".join(retrieved_content),
        }

    def get_snippet_around_section(self, title, num_lines):
        """
        Retrieve up to `num_lines` lines starting at the specified heading and continuing through
        subsequent headings until enough lines are accumulated.

        Args:
            title (str): The title of the section to start from.
            num_lines (int): The number of lines to retrieve.

        Returns:
            str: The retrieved snippet of content.
                Returns None if no matching section is found.
        """
        flattened_nodes = self._flatten_structure()

        start_index = None
        for i, node in enumerate(flattened_nodes):
            if node["title"] == title:
                start_index = i
                break

        if start_index is None:
            return None  # No matching section found

        snippet_lines = []

        for node in flattened_nodes[start_index:]:
            lines = node["content"].splitlines()
            snippet_lines.extend(lines)

            # Stop once we have enough lines
            if len(snippet_lines) >= num_lines:
                break

        # Trim to the required number of lines
        snippet_lines = snippet_lines[:num_lines]

        return "\n".join(snippet_lines)

    def boolean_search(self, query, operator="AND"):
        """
        Perform a simple Boolean search for the query terms in the node content.
        operator='AND' matches only if all terms are present.
        operator='OR' matches if any term is present.
        Returns a list of matched nodes with a snippet for each.
        """
        terms = [t.strip().lower() for t in query.split() if t.strip()]
        if not terms:
            return []

        matches = []
        all_nodes = []

        def walk(nodes):
            for n in nodes:
                all_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)

        for node in all_nodes:
            content_lower = node["content"].lower()
            if operator.upper() == "AND":
                if all(term in content_lower for term in terms):
                    snippet = self._extract_around_keyword(content_lower, terms[0])
                    matches.append({"title": node["title"], "snippet": snippet})
            elif operator.upper() == "OR":
                if any(term in content_lower for term in terms):
                    snippet = self._extract_around_keyword(content_lower, terms[0])
                    matches.append({"title": node["title"], "snippet": snippet})
        return matches

    def fuzzy_search(self, keyword, ratio_threshold=0.6):
        """
        Return a list of approximate matches using a similarity ratio check.
        Requires the standard library 'difflib' or a similar library.
        'ratio_threshold' is a float between 0 and 1.
        """
        if not HAS_DIFFLIB:
            return []

        matches = []
        all_nodes = []

        def walk(nodes):
            for n in nodes:
                all_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)

        for node in all_nodes:
            content_words = node["content"].split()
            for word in content_words:
                similarity = SequenceMatcher(
                    None, word.lower(), keyword.lower()
                ).ratio()
                if similarity >= ratio_threshold:
                    snippet = self._extract_around_keyword(node["content"], word)
                    matches.append(
                        {
                            "title": node["title"],
                            "matched_word": word,
                            "snippet": snippet,
                        }
                    )
                    break
        return matches

    def get_highlighted_snippet(self, keyword, window=40):
        """
        Return a dictionary of headings and highlighted snippets around the first
        occurrence of 'keyword' in each heading's content.
        """
        results = []
        all_nodes = []

        def walk(nodes):
            for n in nodes:
                all_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)

        for node in all_nodes:
            idx = node["content"].lower().find(keyword.lower())
            if idx != -1:
                start = max(0, idx - window)
                end = min(len(node["content"]), idx + len(keyword) + window)
                snippet = node["content"][start:end]
                highlighted = re.sub(
                    re.escape(keyword),
                    f"[{keyword.upper()}]",
                    snippet,
                    flags=re.IGNORECASE,
                )
                results.append(
                    {"title": node["title"], "highlighted_snippet": highlighted}
                )
        return results

    def fuzzy_search_with_lines(self, keyword, num_lines=5, ratio_threshold=0.6):
        """
        Perform a fuzzy search for a keyword in the document and extract a specified
        number of lines (num_lines) around the fuzzy match.

        Args:
            keyword (str): The keyword to search for using fuzzy matching.
            num_lines (int): The number of lines to extract starting from the match.
            ratio_threshold (float): The minimum similarity ratio for fuzzy matches.

        Returns:
            list: A list of dictionaries containing the matched heading title,
                matched word, and the extracted lines of content. Returns an
                empty list if no matches are found.
        """
        if not HAS_DIFFLIB:
            return []

        matches = []
        all_nodes = []

        # Flatten the structure for easy traversal
        def walk(nodes):
            for n in nodes:
                all_nodes.append(n)
                if n["children"]:
                    walk(n["children"])

        walk(self._structure)

        # Iterate through each node and perform a fuzzy search
        for node in all_nodes:
            content_lines = node["content"].splitlines()

            # Search for a fuzzy match for the keyword in the content lines
            for line in content_lines:
                similarity = SequenceMatcher(
                    None, line.lower(), keyword.lower()
                ).ratio()

                if similarity >= ratio_threshold:
                    # Extract the specified number of lines from this point
                    line_index = content_lines.index(line)
                    extracted_lines = content_lines[line_index : line_index + num_lines]

                    matches.append(
                        {
                            "title": node["title"],
                            "matched_line": line,
                            "content": "\n".join(extracted_lines),
                        }
                    )
                    break  # Stop after the first match in this node (optional)

        return matches
