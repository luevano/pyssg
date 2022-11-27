# pyssg - Static Site Generator written in Python

Inspired (initially) by Roman Zolotarev's [`ssg5`](https://rgz.ee/bin/ssg5) and [`rssg`](https://rgz.ee/bin/rssg), Luke Smith's [`lb` and `sup`](https://github.com/LukeSmithxyz/lb) and, pedantic.software's great (but *"mamador"*, as I would say in spanish) [`blogit`](https://pedantic.software/git/blogit/).

## Features and to-do

**Please note that since this is a WIP, there will be changes that will break your site setup (the database management, for example). Read the tag notes for any possible break between the version you're using and the one you're updating to.**

- [x] Build static site parsing `markdown` files ( `*.md` -> `*.html`)
	- [x] ~~Using plain `*.html` files for templates.~~ Changed to Jinja templates.
		- [x] Would like to change to something more flexible and easier to manage ([`jinja`](https://jinja.palletsprojects.com/en/3.0.x/), for example).
	- [x] Preserves hand-made `*.html` files.
	- [x] Tag functionality.
	- [ ] Open Graph (and similar) support. (Technically, this works if you add the correct metadata to the `*.md` files and use the variables available for Jinja)
- [x] Build `sitemap.xml` file.
	- [ ] Include manually added `*.html` files.
- [x] Build `rss.xml` file.
	- [ ] Join the `static_url` to all relative URLs found to comply with the [RSS 2.0 spec](https://validator.w3.org/feed/docs/rss2.html) (this would be added to the parsed HTML text extracted from the MD files, so it would be available to the created `*.html` and `*.xml` files). Note that depending on the reader, it will append the URL specified in the RSS file or use the [`xml:base`](https://www.rssboard.org/news/151/relative-links) specified ([newsboat](https://newsboat.org/) parses `xml:base`).
	- [ ] Include manually added `*.html` files.
- [x] Only build page if `*.md` is new or updated.
	- [ ] Extend this to tag pages and index (right now all tags and index is built no matter if no new/updated file is present).
- [x] Configuration file. ~~as an alternative to using command line flags (configuration file options are prioritized).~~ 
	- [x] Use [`configparser`](https://docs.python.org/3/library/configparser.html) instead of custom config handler.
	- [ ] Migrate to YAML instead of INI, as it is way more flexible.
- [x] Avoid the program to freak out when there are directories created in advance.
- [x] Provide more meaningful error messages when you are missing mandatory metadata in your `*.md` files.
- [ ] More complex directory structure to support multiple subdomains and different types of pages.
- [ ] Option/change to using an SQL database instead of the custom solution.
- [x] Checksum checking because the timestamp of the file is not enough.
- [ ] Better management of the extensions.

### Markdown features

This program uses the base [`markdown` syntax](https://daringfireball.net/projects/markdown/syntax) plus additional syntax, all thanks to [`python-markdown`](https://python-markdown.github.io/) that provides [extensions](https://python-markdown.github.io/extensions/). The following extensions are used:

- Extra (collection of QoL extensions).
- Meta-Data.
- Sane Lists.
- SmartyPants.
- Table of Contents.
- WikiLinks.
- [yafg - Yet Another Figure Generator](https://git.sr.ht/~ferruck/yafg)
- [Markdown Checklist](https://github.com/FND/markdown-checklist)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
	- [Caret](https://facelessuser.github.io/pymdown-extensions/extensions/caret/)
	- [Tilde](https://facelessuser.github.io/pymdown-extensions/extensions/tilde/)
	- [Mark](https://facelessuser.github.io/pymdown-extensions/extensions/mark/)

## Installation

Just install it with `pip`:

```sh
pip install pyssg
```

Will add a PKBUILD (and possibly submit it to the AUR) sometime later.

## Usage

1. Get the default configuration file:

```sh
pyssg --copy-default-config -c <path/to/config>
```

- Where `-c` is optional as by default `$XDG_CONFIG_HOME/pyssg/config.ini` is used.

2. Edit the config file created as needed.

- `config.ini` is parsed using Python's [`configparser`](https://docs.python.org/3/library/configparser.html), [more about the config file](#config-file).

3. Initialize the directory structures (source, destination, template) and move template files:

```sh
pyssg -i
```

- You can modify the basic templates as needed (see [variables available for Jinja](#available-jinja-variables)).

- Strongly recommended to edit the `rss.xml` template.

4. Place your `*.md` files somewhere inside the source directory. It accepts sub-directories.

- Remember to add the mandatory meta-data keys to your `.md` files, these are:

```
title: the title of your blog entry or whatever
author: your name or online handle
lang: the language the entry is written on
summary: a summary of the entry
```

- You can add more meta-data keys as long as it is [Python-Markdown compliant](https://python-markdown.github.io/extensions/meta_data/), and these will ve [available as Jinja variables](#available-jinja-variables).

- Also strongly recomended to add the `tags` metadata so that `pyssg` generates some nice filtering tags.

5. Build the `*.html` with:

```sh
pyssg -b
```

- After this, you have ready to deploy `*.html` files.

- For now, the building option also creates the `rss.xml` and `sitemap.xml` files based on templates, including only all converted `*.md` files (and processed tags in case of the sitemap), meaning that separate `*.html` files should be included manually in the template.

## Config file

All sections/options need to be compliant with the [`configparser`](https://docs.python.org/3/library/configparser.html).

At least the sections and options given in the default config should be present:

```ini
[path]
src=src # source
dst=dst # destination
plt=plt # template
[url]
main=https://example.com
static=https://static.example.com # used for static resources (images, js, css, etc)
default_image=/images/default.png # this will be appended to 'static' at the end
[fmt] # % needs to be escaped with another %
date=%%a, %%b %%d, %%Y @ %%H:%%M %%Z
list_date=%%b %%d
list_sep_date=%%B %%Y
[info]
title=Example site
[other]
force=False
```

Along with these, these extra ones will be added on runtime:

```ini
[fmt]
rss_date=%%a, %%d %%b %%Y %%H:%%M:%%S GMT # fixed
sitemap_date=%%Y-%%m-%%d # fixed
[info]
version= # current 'pyssg' version (0.5.1.dev16, for example)
debug=True/False # depending if --debug was used when executing
rss_run_date= # date the program was run, formatted with 'rss_date'
sitemap_run_date= # date the program was run, formatted with 'sitemap_date'
```

You can add any other option/section that you can later use in the Jinja templates via the exposed config object. 

Other requisites are:

- Urls shouldn't have the trailing slash `/`.
- The only character that needs to be escaped is `%` with another `%`.

## Available Jinja variables

These variables are exposed to use within the templates. The below list is in the form of *variable (type) (available from): description*. `section/option` describe config file section and option and `object.attribute` corresponding object and it's attribute.

- `config` (`ConfigParser`) (all): parsed config file plus the added options internally (as described in [config file](#config-file)).
- `all_pages` (`list(Page)`) (all): list of all the pages, sorted by creation time, reversed.
- `page` (`Page`) (`page.html`): contains the following attributes (genarally these are parsed from the metadata in the `*.md` files):
	- `title` (`str`): title of the page.
	- `author` (`str`): author of the page.
	- `content` (`str`): actual content of the page, this is the `html`.
	- `cdatetime` (`str`): creation datetime object of the page.
	- `cdate` (`str`): formatted `cdatetime` as the config option `fmt/date`.
	- `cdate_list` (`str`): formatted `cdatetime` as the config option `fmt/list_date`.
	- `cdate_list_sep` (`str`): formatted `cdatetime` as the config option `fmt/list_sep_date`.
	- `cdate_rss` (`str`): formatted `cdatetime` as required by rss.
	- `cdate_sitemap` (`str`): formatted `cdatetime` as required by sitemap.
	- `mdatetime` (`str`): modification datetime object of the page. Defaults to `None`.
	- `mdate` (`str`): formatted `mdatetime` as the config option `fmt/date`. Defaults to `None`.
	- `mdate_list` (`str`): formatted `mdatetime` as the config option `fmt/list_date`.
	- `mdate_list_sep` (`str`): formatted `mdatetime` as the config option `fmt/list_sep_date`.
	- `mdate_rss` (`str`): formatted `mdatetime` as required by rss.
	- `mdate_sitemap` (`str`): formatted `mdatetime` as required by sitemap.
	- `summary` (`str`): summary of the page, as specified in the `*.md` file.
	- `lang` (`str`): page language, used for the general `html` tag `lang` attribute.
	- `tags` (`list(tuple(str))`): list of tuple of tags of the page, containing the name and the url of the tag, in that order. Defaults to empty list.
	- `url` (`str`): url of the page, this already includes the `url/main` from config file.
	- `image_url` (`str`): image url of the page, this already includes the `url/static`. Defaults to the `url/default_image` config option.
	- `next/previous` (`Page`): reference to the next or previous page object (containing all these attributes). Defaults to `None`.
	- `og` (`dict(str, str)`): dict for object graph metadata.
	- `meta` (`dict(str, list(str))`): meta dict as obtained from python-markdown, in case you use a meta tag not yet supported, it will be available there.
- `tag` (`tuple(str)`) (`tag.html`): tuple of name and url of the current tag.
- `tag_pages` (`list(Page)`) (`tag.html`): similar to `all_pages` but contains all the pages for the current tag.
- `all_tags` (`list(tuple(str))`) (all): similar to `page.tags` but contains all the tags.
