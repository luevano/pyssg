import os


def create_templates(src: str, dst: str):
    # get initial working directory
    iwd = os.getcwd()
    print('creating dir structure...')

    # create main dirs
    try:
        os.mkdir(src)
        os.mkdir(dst)
    except FileExistsError:
        pass

    os.chdir(src)

    # create templates dir
    os.mkdir('templates')
    os.chdir('templates')

    # create article (blog) barebones template
    os.mkdir('article')
    with open('article/header.html', 'w+') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang=$$LANG>\n')
        f.write('<head>\n')
        f.write('<meta charset="utf-8">\n')
        f.write('<title>$$TITLE</title>\n')
        f.write('$$EXTRAHEAD\n')
        f.write('</head>\n')
        f.write('<body>\n')

    with open('article/footer.html', 'w+') as f:
        f.write('</body>\n')
        f.write('</html>\n')

    with open('article/index_header.html', 'w+') as f:
        f.write('')

    with open('article/tag_list_header.html', 'w+') as f:
        f.write('<p>Tags:')

    with open('article/tag_entry.html', 'w+') as f:
        f.write('<a href="$$URL">$$NAME</a>')

    with open('article/tag_separator.html', 'w+') as f:
        f.write(', ')

    with open('article/tag_list_footer.html', 'w+') as f:
        f.write('</p>\n')

    with open('article/article_list_header.html', 'w+') as f:
        f.write('<h2>Articles</h2>\n')
        f.write('<ul>\n')

    with open('article/article_entry.html', 'w+') as f:
        f.write('<li><a href="$$URL">$$DATE $$TITLE</a></li>\n')

    with open('article/article_separator.html', 'w+') as f:
        f.write('')

    with open('article/article_list_footer.html', 'w+') as f:
        f.write('</ul>\n')

    with open('article/index_footer.html', 'w+') as f:
        f.write('')

    with open('article/tag_index_header.html', 'w+') as f:
        f.write('')

    with open('article/tag_index_footer.html', 'w+') as f:
        f.write('')

    with open('article/article_header.html', 'w+') as f:
        f.write('<h1>$$TITLE</h1>')

    with open('article/article_footer.html', 'w+') as f:
        f.write('')

    # return to initial working directory
    os.chdir(iwd)
    print('done creating dir structure...')
