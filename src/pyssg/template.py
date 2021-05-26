import os

from .page import Page


# all objects here require a header and footer as minimum
class HF:
    def __init__(self):
        self.header: str = None
        self.footer: str = None


# some objects require a "list-like" set of attributes
class Common(HF):
    def __init__(self):
        self.list_header: str = None
        self.list_footer: str = None
        self.list_entry: str = None
        self.list_separator: str = None


# main class
class Template(HF):
    def __init__(self, src: str):
        self.src: str = src
        self.article: HF = HF()
        self.articles: Common = Common()
        self.tags: Common = Common()
        self.rss: str = None
        self.sitemap: str = None

        self.is_read: bool = False


    # writes default templates
    def write(self) -> None:
        # get initial working directory
        iwd = os.getcwd()
        os.chdir(self.src)

        # create templates dir
        os.mkdir('templates')
        os.chdir('templates')

        # common
        os.mkdir('common')
        os.chdir('common')
        self.__write_template('header.html',
                              ['<!DOCTYPE html>\n',
                               '<html lang="$$LANG">\n',
                               '<head>\n',
                               '<meta charset="utf-8">\n',
                               '<title>$$TITLE</title>\n',
                               '</head>\n',
                               '<body>\n'])
        self.__write_template('footer.html',
                              ['</body>\n',
                               '</html>\n'])

        # go back to templates
        os.chdir('..')

        # article entry
        os.mkdir('article')
        os.chdir('article')
        self.__write_template('header.html',
                              ['<h1>$$TITLE</h1>\n',
                               '<p>$$AUTHOR</p>\n',
                               '<p>Created: $$CTIME, modified: $$MTIME</p>\n'])
        self.__write_template('footer.html',
                              [''])

        # go back to templates
        os.chdir('..')

        # article index (articles)
        os.mkdir('articles')
        os.chdir('articles')
        self.__write_template('header.html',
                              [''])
        self.__write_template('list_header.html',
                              ['<h2>Articles</h2>\n',
                               '<ul>\n'])
        self.__write_template('list_entry.html',
                              ['<li>$$DATE - <a href="$$URL">$$TITLE</a></li>\n'])
        self.__write_template('list_separator.html',
                              ['<h3>$$SEP</h3>\n'])
        self.__write_template('list_footer.html',
                              ['</ul>\n'])
        self.__write_template('footer.html',
                              [''])

        # go back to templates
        os.chdir('..')

        # tag
        os.mkdir('tag')
        os.chdir('tag')
        self.__write_template('header.html',
                              [''])
        self.__write_template('list_header.html',
                              ['<p>Tags: '])
        self.__write_template('list_entry.html',
                              ['<a href="$$URL">$$NAME</a>'])
        self.__write_template('list_separator.html',
                              [', '])
        self.__write_template('list_footer.html',
                              ['</p>\n'])
        self.__write_template('footer.html',
                              [''])

        # go back to templates
        os.chdir('..')

        os.mkdir('rss')
        os.chdir('rss')
        self.__write_template('rss.xml',
                              ['<?xml version="1.0" encoding="UTF-8" ?>\n',
                               '<rss version="2.0"\n',
                               '  xmlns:atom="http://www.w3.org/2005/Atom"\n',
                               '  xmlns:content="http://purl.org/rss/1.0/modules/content/">\n',
                               '  <channel>\n',
                               '    <title>$$TITLE</title>\n',
                               '    <link>$$LINK</link>\n',
                               '    <atom:link href="EXAMPLE.ORG/RSS.XML" rel="self" type="application/rss+xml"/>\n',
                               '    <description>SHORT DESCRIPTION.</description>\n',
                               '    <language>en-us</language>\n',
                               '    <copyright>COPYRIGHT NOTICE.</copyright>\n',
                               '    <managingEditor>EMAIL@EXAMPLE.ORG (NAME)</managingEditor>\n',
                               '    <webMaster>EMAIL@EXAMPLE.ORG (NAME)</webMaster>\n',
                               '    <pubDate>$$CURRENTDATE</pubDate>\n',
                               '    <lastBuildDate>$$CURRENTDATE</lastBuildDate>\n',
                               '    <generator>$$PYSSGVERSION</generator>\n',
                               '    <docs>https://validator.w3.org/feed/docs/rss2.html</docs>\n',
                               '    <ttl>30</ttl>\n',
                               '    <image>\n',
                               '      <url>EXAMPLE.ORG/IMAGE.PNG</url>\n',
                               '      <title>$$TITLE</title>\n',
                               '      <link>$$LINK</link>\n',
                               '    </image>\n',
                               '$$ITEMS\n',
                               '  </channel>\n',
                               '</rss>'])

        # go back to templates
        os.chdir('..')

        os.mkdir('sitemap')
        os.chdir('sitemap')
        self.__write_template('sitemap.xml',
                              ['<?xml version="1.0" encoding="utf-8"?>\n',
                               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n',
                               '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n',
                               '  xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n',
                               'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n',
                               '$$URLS\n',
                               '</urlset>'])
        # return to initial working directory
        os.chdir(iwd)


    # reads templates and stores them into class attributes
    def read(self) -> None:
        # only read templates if not read already
        # (might want to change this behaviour)
        if self.is_read:
            return
        self.is_read = True

        # get initial working directory
        iwd = os.getcwd()
        os.chdir(os.path.join(self.src, 'templates'))

        # common
        os.chdir('common')
        self.header = self.__read_template('header.html')
        self.footer = self.__read_template('footer.html')

        # go back to templates
        os.chdir('..')

        # article entry
        os.chdir('article')
        self.article.header = self.__read_template('header.html')
        self.article.footer = self.__read_template('footer.html')

        # go back to templates
        os.chdir('..')

        # article index
        os.chdir('articles')
        self.articles.header = self.__read_template('header.html')
        self.articles.list_header = \
                self.__read_template('list_header.html')
        self.articles.list_entry = \
                self.__read_template('list_entry.html')
        self.articles.list_separator = \
                self.__read_template('list_separator.html')
        self.articles.list_footer = \
                self.__read_template('list_footer.html')
        self.articles.footer = self.__read_template('footer.html')

        # go back to templates
        os.chdir('..')

        # tag
        os.chdir('tag')
        self.tags.header = self.__read_template('header.html')
        self.tags.list_header = self.__read_template('list_header.html')
        self.tags.list_entry = self.__read_template('list_entry.html')
        self.tags.list_separator = self.__read_template('list_separator.html')
        self.tags.list_footer = self.__read_template('list_footer.html')
        self.tags.footer = self.__read_template('footer.html')

        # go back to templates
        os.chdir('..')

        # rss
        os.chdir('rss')
        self.rss = self.__read_template('rss.xml')

        # go back to templates
        os.chdir('..')

        # sitemap
        os.chdir('sitemap')
        self.sitemap = self.__read_template('sitemap.xml')

        # return to initial working directory
        os.chdir(iwd)


    def __write_template(self, file_name: str, content: list[str]) -> None:
        with open(file_name, 'w+') as f:
            for c in content:
                f.write(c)

    def __read_template(self, file_name: str) -> str:
        out: str = None
        with open(file_name, 'r') as f:
            out = f.read()

        return out
