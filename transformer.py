import requests
import re
import html2text
import os

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'

class Config:
	def __init__(self, user_agent=DEFAULT_USER_AGENT, download_image=False, asset_path='.'):
		self.user_agent = user_agent
		self.download_image = download_image
		self.asset_path = os.path.expanduser(asset_path)

class Article:
	def __init__(self, article_id, config):
		article_json = request_json(article_id, config.user_agent)

		self.id = article_json['id']
		self.title = article_json['title']
		self.created = article_json['created']
		self.updated = article_json['updated']
		content = article_json['content']
		self.content = preprocess_content(content, config.download_image, config.asset_path)
		self.markdown = html2text.html2text(self.content)

def request_json(article_id, user_agent):
	article_api_url = f'https://api.zhihu.com/articles/{article_id}'
	headers = { 'user-agent': user_agent }
	return requests.get(article_api_url, headers=headers).json()

def preprocess_content(content, download_image, asset_path):
	def latex_repl(matchobj):
		return f'${matchobj.group(1)}$'

	latex_pattern = r'<img src="https://www.zhihu.com/equation\?tex=.+?" alt="(.+?)".+?/>'
	left_para_latex = r'<p>\$'
	right_para_latex = r'\$ </p>'

	content = re.sub(latex_pattern, latex_repl, content) 
	content = re.sub(left_para_latex, '<p>$$<br>', content)
	content = re.sub(right_para_latex, '<br>$$', content)

	if download_image:
		image_pattern = r'<img src="(https?.+?)".+?/>'
		def image_repl(matchobj):
			image_url = matchobj.group(1)
			image_title = image_url.split('/')[-1]
			image_download_path = os.path.join(asset_path, image_title)
			image = requests.get(image_url).content
			with open(image_download_path, 'wb') as image_file:
				image_file.write(image)
			return f'<img src="{image_download_path}">'
		content = re.sub(image_pattern, image_repl, content)
	return content

def markdown_api(url):
	config = Config()
	article_pattern = r'https://zhuanlan.zhihu.com/p/(\d.+)/?'
	objmatch = re.search(article_pattern, url)
	if not objmatch.group(1):
		raise "Article URL not match. Must like: https://zhuanlan.zhihu.com/p/1234567"

	article = Article(objmatch.group(1), config)
	return article.markdown