import logging
import re
import time
from typing import List, Dict, Any, Callable
from notion_client import Client, APIResponseError

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self, notion_secret: str, database_id: str, max_retries: int = 3, retry_delay: int = 5):
        self.client = Client(auth=notion_secret)
        self.database_id = database_id
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executes a Notion API call with a retry mechanism for rate limits (429).
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except APIResponseError as e:
                if e.status == 429:
                    retries += 1
                    if retries > self.max_retries:
                        logger.error(f"Max retries reached for Notion API (429).")
                        raise
                    wait_time = self.retry_delay * retries
                    logger.warning(f"Notion rate limit reached. Retrying in {wait_time}s... (Attempt {retries}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Notion API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error calling Notion API: {e}")
                raise

    def check_connection(self) -> bool:
        """
        Verifies the connection to Notion by retrieving the database metadata.
        """
        try:
            self._execute_with_retry(self.client.databases.retrieve, database_id=self.database_id)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion: {e}")
            return False

    def process_inline_formatting(self, text: str) -> List[Dict[str, Any]]:
        """
        Processes inline markdown formatting (bold, italic, code, links, math) into Notion rich text objects.
        """
        # Patterns for inline formatting
        bold_pattern = r'(\*\*|__)(.*?)\1'
        italic_pattern = r'(\*|_)(.*?)\1'
        code_pattern = r'`(.*?)`'
        link_pattern = r'\[(.*?)\]\((.*?)\)'
        math_pattern = r'\$(.*?)\$'

        # We'll use a list of parts that can be either strings (unprocessed) or dicts (processed)
        parts = [text]

        def replace_with_regex(parts_list, pattern, annotation_key=None, is_link=False, is_math=False):
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
                    elif is_math:
                        expression = match.group(1)
                        rt = {
                            "type": "equation",
                            "equation": {"expression": expression}
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
        parts = replace_with_regex(parts, math_pattern, is_math=True)
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

    def _convert_table_to_latex(self, table_lines: List[str]) -> str:
        """
        Converts a list of markdown table lines to a LaTeX array for Notion equations.
        Also handles basic markdown (bold/italic) within cells and preserves math.
        """
        if len(table_lines) < 2:
            return ""

        def clean_cell(text: str) -> str:
            # Handle bold: **text** or __text__ -> \textbf{text}
            text = re.sub(r'(\*\*|__)(.*?)\1', r'\\textbf{\2}', text)
            # Handle italic: *text* or _text_ -> \textit{text}
            text = re.sub(r'(\*|_)(.*?)\1', r'\\textit{\2}', text)
            # Escape LaTeX special characters that break the array, 
            # but PRESERVE $ for math mode and \ for our injected commands
            text = text.replace("&", "\\&").replace("%", "\\%")
            # Note: We don't escape $ here because we want to allow math inside cells
            return text

        # Extract headers and rows, skipping delimiter line
        headers = [clean_cell(c.strip()) for c in table_lines[0].split('|') if c.strip()]
        rows = []
        for line in table_lines[2:]:
            cols = [clean_cell(c.strip()) for c in line.split('|') if c.strip()]
            if cols:
                rows.append(cols)

        if not headers:
            return ""

        col_count = len(headers)
        col_format = "|c" * col_count + "|"
        
        latex = f"\\def\\arraystretch{{1.4}}\\begin{{array}}{{{col_format}}}\\hline\n"
        
        # Add Header
        header_row = " & ".join([f"\\textsf{{\\textbf{{{h}}}}}" for h in headers])
        latex += f"{header_row} \\\\\\hline\n"
        
        # Add Data Rows
        for row in rows:
            # Pad or truncate row to match col_count
            row = (row + [""] * col_count)[:col_count]
            row_text = " & ".join([f"\\textsf{{{c}}}" for c in row])
            latex += f"{row_text} \\\\\\hline\n"
            
        latex += "\\end{array}"
        return latex

    def markdown_to_blocks(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Converts Markdown text into Notion blocks. Handles math, tables, headings, lists, code blocks, and quotes.
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

        # Pre-process block math
        math_blocks = {}
        def replace_math_block(match):
            idx = len(math_blocks)
            expression = match.group(1).strip()
            math_blocks[f"MATH_BLOCK_{idx}"] = expression
            return f"\nMATH_BLOCK_{idx}\n"

        markdown_text = re.sub(r'\$\$(.*?)\$\$', replace_math_block, markdown_text, flags=re.DOTALL)

        lines = markdown_text.split("\n")
        blocks = []
        
        in_table = False
        table_lines = []

        for line in lines:
            stripped = line.strip()
            
            # Table detection
            is_table_row = bool(re.match(r'^\|.*\|$', stripped))
            if is_table_row:
                in_table = True
                table_lines.append(stripped)
                continue
            elif in_table:
                # Process the table
                latex_table = self._convert_table_to_latex(table_lines)
                if latex_table:
                    blocks.append({
                        "object": "block",
                        "type": "equation",
                        "equation": {"expression": latex_table}
                    })
                in_table = False
                table_lines = []

            if not stripped:
                continue

            # Code Blocks
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

            # Math Blocks
            if stripped in math_blocks:
                expression = math_blocks[stripped]
                blocks.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": expression}
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

        # Catch trailing table
        if in_table:
            latex_table = self._convert_table_to_latex(table_lines)
            if latex_table:
                blocks.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": latex_table}
                })

        return blocks

    def split_rich_text(self, rich_text_list: List[Dict[str, Any]], max_len: int = 2000) -> List[List[Dict[str, Any]]]:
        """
        Splits a list of rich text objects into multiple lists, each within the character limit.
        """
        chunks = []
        current_chunk = []
        current_len = 0

        for rt in rich_text_list:
            content = rt.get("text", {}).get("content", "")
            content_len = len(content)

            if current_len + content_len <= max_len:
                current_chunk.append(rt)
                current_len += content_len
            else:
                # If a single segment is too long, we need to split it (rare for our use case but good for robustness)
                if content_len > max_len:
                    # Flush current chunk if not empty
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = []
                        current_len = 0
                    
                    # Split the long content
                    for i in range(0, content_len, max_len):
                        segment = content[i:i + max_len]
                        new_rt = rt.copy()
                        new_rt["text"] = rt["text"].copy()
                        new_rt["text"]["content"] = segment
                        chunks.append([new_rt])
                else:
                    chunks.append(current_chunk)
                    current_chunk = [rt]
                    current_len = content_len
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def create_page(self, title: str, markdown_text: str) -> str:
        """
        Creates a new Notion page in the database and populates it with content.
        """
        blocks = self.markdown_to_blocks(markdown_text)
        
        # Handle 2000 character limit per rich text by potentially splitting blocks
        final_blocks = []
        for block in blocks:
            block_type = block.get("type")
            if block_type and block_type in block:
                rich_text = block[block_type].get("rich_text")
                if rich_text:
                    total_len = sum(len(rt.get("text", {}).get("content", "")) for rt in rich_text)
                    if total_len > 2000:
                        # Split into multiple blocks of the same type (only works for paragraphs really)
                        if block_type == "paragraph":
                            chunks = self.split_rich_text(rich_text)
                            for chunk in chunks:
                                final_blocks.append({
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {"rich_text": chunk}
                                })
                            continue
                        else:
                            # For headings/lists, we just truncate or keep as is (Notion will error if we don't)
                            # Truncation is safer for API stability
                            pass

            final_blocks.append(block)

        # 1. Create the page with initial properties (title)
        db_info = self._execute_with_retry(self.client.databases.retrieve, database_id=self.database_id)
        title_prop_name = "title" # default
        for prop_name, prop_info in db_info.get("properties", {}).items():
            if prop_info.get("type") == "title":
                title_prop_name = prop_name
                break

        # Initial 100 blocks can be sent in the create call
        initial_batch = final_blocks[:100]
        remaining_blocks = final_blocks[100:]

        new_page = self._execute_with_retry(
            self.client.pages.create,
            parent={"database_id": self.database_id},
            properties={
                title_prop_name: {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            },
            children=initial_batch
        )

        # 2. Append remaining blocks in batches of 100
        for i in range(0, len(remaining_blocks), 100):
            batch = remaining_blocks[i:i + 100]
            self._execute_with_retry(
                self.client.blocks.children.append,
                block_id=new_page["id"],
                children=batch
            )

        return new_page.get("url", "")
