import logging
import re
from typing import List, Dict, Any
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self, notion_secret: str, database_id: str):
        self.client = Client(auth=notion_secret)
        self.database_id = database_id

    def check_connection(self) -> bool:
        """
        Verifies the connection to Notion by retrieving the database metadata.
        """
        try:
            self.client.databases.retrieve(database_id=self.database_id)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion: {e}")
            return False

    def process_inline_formatting(self, text: str) -> List[Dict[str, Any]]:
        """
        Processes inline markdown formatting (bold, italic, code, links) into Notion rich text objects.
        """
        # Patterns for inline formatting
        bold_pattern = r'(\*\*|__)(.*?)\1'
        italic_pattern = r'(\*|_)(.*?)\1'
        code_pattern = r'`(.*?)`'
        link_pattern = r'\[(.*?)\]\((.*?)\)'

        # We'll use a list of parts that can be either strings (unprocessed) or dicts (processed)
        parts = [text]

        def replace_with_regex(parts_list, pattern, annotation_key=None, is_link=False):
            new_parts = []
            for part in parts_list:
                if not isinstance(part, str):
                    new_parts.append(part)
                    continue
                
                last_idx = 0
                for match in re.finditer(pattern, part):
                    # Add preceding plain text
                    if match.start() > last_idx:
                        new_parts.append(part[last_idx:match.start()])
                    
                    # Create Notion rich text object
                    if is_link:
                        content, url = match.group(1), match.group(2)
                        rt = {
                            "type": "text",
                            "text": {"content": content, "link": {"url": url}},
                            "annotations": {}
                        }
                    else:
                        content = match.group(2) if annotation_key != 'code' else match.group(1)
                        rt = {
                            "type": "text",
                            "text": {"content": content},
                            "annotations": {annotation_key: True} if annotation_key else {}
                        }
                    new_parts.append(rt)
                    last_idx = match.end()
                
                if last_idx < len(part):
                    new_parts.append(part[last_idx:])
            return new_parts

        # Apply replacements in order of priority
        parts = replace_with_regex(parts, code_pattern, 'code')
        parts = replace_with_regex(parts, link_pattern, is_link=True)
        parts = replace_with_regex(parts, bold_pattern, 'bold')
        parts = replace_with_regex(parts, italic_pattern, 'italic')

        # Final conversion to Notion format
        rich_text = []
        for part in parts:
            if isinstance(part, str):
                if part:
                    rich_text.append({"type": "text", "text": {"content": part}, "annotations": {}})
            else:
                rich_text.append(part)
        
        return rich_text

    def markdown_to_blocks(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Converts Markdown text into Notion blocks. Handles headings, lists, code blocks, and quotes.
        """
        # Pre-process triple-backtick code blocks
        code_blocks = {}
        def replace_code_block(match):
            idx = len(code_blocks)
            lang = match.group(1) or "plain text"
            content = match.group(2).strip()
            code_blocks[f"CODE_BLOCK_{idx}"] = (lang, content)
            return f"\nCODE_BLOCK_{idx}\n"

        markdown_text = re.sub(r'```(\w*)\n?(.*?)```', replace_code_block, markdown_text, flags=re.DOTALL)

        lines = markdown_text.split("\n")
        blocks = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Code Blocks (Placeholder replacement)
            if stripped in code_blocks:
                lang, content = code_blocks[stripped]
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": lang,
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                continue

            # Headings
            heading_match = re.match(r'^(#+) (.*)$', stripped)
            if heading_match:
                level = min(len(heading_match.group(1)), 3)
                content = heading_match.group(2)
                block_type = f"heading_{level}"
                blocks.append({
                    "object": "block",
                    "type": block_type,
                    block_type: {"rich_text": self.process_inline_formatting(content)}
                })
                continue

            # Blockquotes
            if stripped.startswith("> "):
                content = stripped[2:]
                blocks.append({
                    "object": "block",
                    "type": "quote",
                    "quote": {"rich_text": self.process_inline_formatting(content)}
                })
                continue

            # List Items
            bullet_match = re.match(r'^[\-\*] (.*)$', stripped)
            if bullet_match:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": self.process_inline_formatting(bullet_match.group(1))}
                })
                continue

            num_match = re.match(r'^\d+\. (.*)$', stripped)
            if num_match:
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": self.process_inline_formatting(num_match.group(1))}
                })
                continue

            # Horizontal Rule
            if re.match(r'^-{3,}$', stripped):
                blocks.append({"object": "block", "type": "divider", "divider": {}})
                continue

            # Paragraph (default)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": self.process_inline_formatting(stripped)}
            })

        return blocks
