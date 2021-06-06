# pyssg - Static Site Generator written in Python

Inspired (initially) by Roman Zolotarev's [`ssg5`](https://rgz.ee/bin/ssg5) and [`rssg`](https://rgz.ee/bin/rssg), Luke Smith's [`lb` and `sup`](https://github.com/LukeSmithxyz/lb) and, pedantic.software's great (but *"mamador"*, as I would say in spanish) [`blogit`](https://pedantic.software/git/blogit/).

I'm writing this in *pYtHoN* (thought about doing it in Go, but I'm most comfortable with Python at the moment) because I want features from all of these minimal programs (and more), but I don't really want to be stitching each one of the features on any of these programs, because they're written in a way to only work as how they were first imagined to work like; I already tried adding features to `ssg` and ended up rewriting it in POSIX shell, but it was a pain in the ass when I tried to add even more, and don't get me started on trying to extend `blogit`... And also because I want to.

## Current features

**This is still a WIP. Still doesn't build `sitemap.xml` or `rss.xml` files.**

- [x] Build static site parsing `markdown` files ( `*.md` -> `*.html`)
	- [x] ~~Using plain `*.html` files for templates.~~ Changed to Jinja templates.
		- [x] Would like to change to something more flexible and easier to manage ([`jinja`](https://jinja.palletsprojects.com/en/3.0.x/), for example).
	- [x] Preserves hand-made `*.html` files.
	- [x] Tag functionality.
	- [ ] Open Graph (and similar) support. (Technically, this works if you add the correct metadata to the `*.md` files and use the variables available for Jinja)
- [x] Build `sitemap.xml` file.
- [x] Build `rss.xml` file.
	- [ ] Join the `static_url` to all relative URLs found to comply with the [RSS 2.0 spec](https://validator.w3.org/feed/docs/rss2.html) (this would be added to the parsed HTML text extracted from the MD files, so it would be available to the created `*.html` and `*.xml` files). Note that depending on the reader, it will append the URL specified in the RSS file or use the [`xml:base`](https://www.rssboard.org/news/151/relative-links) specified ([newsboat](https://newsboat.org/) parses `xml:base`).
- [x] Only build page if `*.md` is new or updated.
	- [ ] Extend this to tag pages and index (right now all tags and index is built no matter if no new/updated file is present).
- [x] Configuration file as an alternative to using command line flags (configuration file options are prioritized).

### Markdown features

This program uses the base [`markdown` syntax](https://daringfireball.net/projects/markdown/syntax) plus additional syntax, all thanks to [`python-markdown`](https://python-markdown.github.io/) that provides [extensions](https://python-markdown.github.io/extensions/). The following extensions are used:

- Extra (collection of QoL extensions).
- Meta-Data.
- Sane Lists.
- SmartyPants.
- Table of Contents.
- WikiLinks.

## Installation

Just install it with `pip`:

```sh
pip install pyssg
```

*EW!*, I know..., I will try to make a PKBUILD and release it in AUR or something; hit me up if you do it to add it here.

## Usage

It is intended to be used as a standalone terminal program running on the "root" directory where you have the `src` and `dst` directories in (defaults for both flags).

First initialize the directories you're going to use for the source files and destination files:

```sh
pyssg -s src_dir -d dst_dir -i
```

That creates the desired directories with the basic templates that can be edited as desired (see variables available for Jinja below). Place your `*.md` files somewhere inside the source directory (`src_dir` in the command above), but outside of the `templates` directory. It accepts sub-directories.

Strongly recommended to edit the `rss.xml` template.

Build the site with:

```sh
pyssg -s src_dir -d dst_dir -t plt_dir -u https://base.url -b
```

That creates all `*.html` for the site and can be easily moved to the server. Here, the `-u` flag is technically optional in the sense that you'll not receive a warning/error, but it's used to prepend links with this URL (not strictly required everywhere), so don't ignore it; also don't include the trailing `/`.

For now, the `-b`uild tag also creates the `rss.xml` and `sitemap.xml` files based on templates including only all converted `*.md` files (and processed tags in case of the sitemap), meaning that separate `*.html` files should be included manually in the template.

For more options/flags just checkout `pyssg -h`.

## Available Jinja variables

Here is the list of variables that you can use specific Jinja templates with a short description. Note that all urls are without the trailing slash `/`.

- `config` (`Configuration`) (all): configuration object containing general/global attributes, the useful ones being:
	- `title` (`str`): title of the website.
	- `url` (`str`): base url of the website.
	- `static_url` (`str`): base static url where all static files are located, mostly needed for correct rss feed generator when using a `base` tag and using relative links to files. For more, see [<base>](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base).
	- `default_image_url` (`str`): as defined in `DEFAULT_IMAGE_URL` configuration option.
	- `version` (`str`): version in numeric form, i.e. `0.5.0`.
	- `run_date` (`str`): date when the program was run, with format required for rss.
- Pages:
	- `all_pages` (`list(Page)`) (all): list of all the pages, sorted by creation time, reversed.
	- `page` (`Page`) (`page.html`): page object that contains the following attributes:
		- `title` (`str`): title of the page.
		- `author` (`str`): author of the page.
		- `content` (`str`): actual content of the page.
		- `cdatetime` (`str`): creation datetime object of the page.
		- `cdate` (`str`): formatted `cdatetime` as the configuration option `DATE_FORMAT`.
		- `cdate_list` (`str`): formatted `cdatetime` as the configuration option `LIST_DATE_FORMAT`.
		- `cdate_list_sep` (`str`): formatted `cdatetime` as the configuration option `LIST_SEP_DATE_FORMAT`.
		- `cdate_rss` (`str`): formatted `cdatetime` as required by rss.
		- `cdate_sitemap` (`str`): formatted `cdatetime` as required by sitemap.
		- `mdatetime` (`str`): modification datetime object of the page. Defaults to None.
		- `mdate` (`str`): formatted `mdatetime` as the configuration option `DATE_FORMAT`. Defaults to None.
		- `mdate_list` (`str`): formatted `mdatetime` as the configuration option `LIST_DATE_FORMAT`.
		- `mdate_list_sep` (`str`): formatted `mdatetime` as the configuration option `LIST_SEP_DATE_FORMAT`.
		- `mdate_rss` (`str`): formatted `mdatetime` as required by rss.
		- `mdate_sitemap` (`str`): formatted `mdatetime` as required by sitemap.
		- `summary` (`str`): summary of the page, as specified in the `*.md` file.
		- `lang` (`str`): page language, used for the general `html` tag `lang` attribute.
		- `tags` (`list(tuple(str))`): list of tuple of tags of the page, containing the name and the url of the tag, in that order. Defaults to empty list.
		- `url` (`str`): url of the page, this already includes the `config.url`.
		- `image_url` (`str`): image url of the page, this already includes the `config.static_url`. Defaults to the `DEFAULT_IMAGE_URL` configuration option.
		- `next/previous` (`Page`): reference to the next or previous page object (containing all these attributes). Defaults to None
		- `og` (`dict(str, str)`): dict for object graph metadata.
		- `meta` (`dict(str, list(str))`): meta dict as obtained from python-markdown, in case you use a meta tag not yet supported, it will be available there.
- Tags:
	- `tag` (`tuple(str)`) (`tag.html`): tuple of name and url of the current tag.
	- `tag_pages` (`list(Page)`) (`tag.html`): similar to `all_pages` but contains all the pages for the current tag.
	- `all_tags` (`list(tuple(str))`) (all): similar to `page.tags` but contains all the tags.
