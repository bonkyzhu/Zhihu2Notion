from os import replace
from notion.client import NotionClient
from notion.block import PageBlock, EquationBlock
from md2notion.upload import upload,convert, uploadBlock
from md2notion.NotionPyRenderer import NotionPyRenderer, addLatexExtension
import itertools
import re
from transformer import *


# 基本信息
token = ""
client = NotionClient(token_v2=token)
zhihu_page = input("输入专栏链接：")
notion_page = "" 
page = client.get_block(notion_page)

print("The title is:", page.title)

txt = markdown_api(zhihu_page)

newPage = page.children.add_new(PageBlock, title="TestMarkdown Upload")

rendered = convert(txt,addLatexExtension(NotionPyRenderer))
for blockDescriptor in rendered:
	if blockDescriptor["type"] is EquationBlock:
		blockDescriptor['title_plaintext'] = blockDescriptor['title_plaintext'].replace("\\\\", "\\")
		blockDescriptor['title_plaintext'] = blockDescriptor['title_plaintext'].replace("\\\\", "\\")
		tag_pattern = r"\\tag\{\d+\}"
		blockDescriptor['title_plaintext'] = re.sub(tag_pattern, "", blockDescriptor['title_plaintext'])
		if not blockDescriptor['title_plaintext'].startswith(r"\begin"):
			blockDescriptor['title_plaintext'] = r"\begin{equation}" + blockDescriptor['title_plaintext'] + r"\end{equation}"
	uploadBlock(blockDescriptor, newPage, "./")