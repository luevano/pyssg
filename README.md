# pyssg - Static Site Generator written in Python

Generates HTML files from MD files for a static site, personally using it for a blog-like site.

Initially inspired by Roman Zolotarev's [`ssg5`](https://rgz.ee/bin/ssg5) and [`rssg`](https://rgz.ee/bin/rssg), Luke Smith's [`lb` and `sup`](https://github.com/LukeSmithxyz/lb) and, pedantic.software's [`blogit`](https://pedantic.software/git/blogit/).

## Features and to-do

**NOTE:** WIP, there will be changes that will break the setup.

- [x] Build static site parsing `markdown` files ( `*.md` -> `*.html`)
	- [x] Uses [`jinja`](https://jinja.palletsprojects.com/en/3.0.x/) for templating.
	- [x] Preserves hand-made `*.html` files.
	- [x] Tag functionality, useful for blog-style sites.
	- [ ] Open Graph (and similar) support.
		- Technically, this works if you add the correct metadata to the `*.md` files and use the variables available for Jinja.
- [x] Build `sitemap.xml` file.
	- [ ] Include manually added `*.html` files.
- [x] Build `rss.xml` file.
	- [ ] Join the `static_url` to all relative URLs found to comply with the [RSS 2.0 spec](https://validator.w3.org/feed/docs/rss2.html).
		- This would be added to the parsed HTML text extracted from the MD files, so it would be available to the created `*.html` and `*.xml` files. Note that depending on the reader, it will append the URL specified in the RSS file or use the [`xml:base`](https://www.rssboard.org/news/151/relative-links) specified (for example, [newsboat](https://newsboat.org/) parses `xml:base`).
	- [ ] Include manually added `*.html` files.
- [x] YAML for configuration file, uses [`PyYAML`](https://pyyaml.org/).
	- [ ] Handle multiple "documents".
	- [ ] More complex directory structure to support multiple subdomains and different types of pages.
- [ ] Option/change to using an SQL database instead of the custom solution.
- [x] Checksum checking because the timestamp of the file is not enough.
- [ ] Use external markdown extensions.

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

Install with `pip`:

```sh
pip install pyssg
```

Probably will add a PKBUILD (and possibly submit it to the AUR) in the future.

## Usage

1. Get the default configuration file:

```sh
pyssg --copy-default-config -c <path/to/config>
```

- Where `-c` is optional as by default `$XDG_CONFIG_HOME/pyssg/config.yaml` is used.

2. Edit the config file created as needed.

- `config.yaml` is parsed using [`PyYAML`](https://pyyaml.org/), [more about the config file](#config-file).

3. Initialize the directory structures (source, destination, template) and move template files:

```sh
pyssg -i
```

- You can modify the basic templates as needed (see [variables available for Jinja](#available-jinja-variables)).

- Strongly recommended to edit the `rss.xml` template.

4. Place your `*.md` files somewhere inside the source directory. It accepts sub-directories.

- Recommended (no longer mandatory) metadata keys that can be added to the top of `.md` files:

```
title: the title of your blog entry or whatever
author: your name or online handle
	another name maybe for multiple authors?
lang: the language the entry is written on
summary: a summary of the entry
tags: english
	short
	tutorial
	etc
```

- You can add more meta-data keys as long as it is [Python-Markdown compliant](https://python-markdown.github.io/extensions/meta_data/), and these will ve [available as Jinja variables](#available-jinja-variables).

5. Build the `*.html` with:

```sh
pyssg -b
```

- After this, you have ready to deploy `*.html` files.

## Config file

All sections/options need to be compliant with [`PyYAML`](https://pyyaml.org/) which should be compliant with [`YAML 1.2`](https://yaml.org/spec/1.2.2/). Additionaly, I've added the custom tag `!join` which concatenates strings from an array, which an be used as follows:

```yaml
variable: &variable_reference_name "value"
other_variable: !join [*variable_reference_name, "other_value", 1]
```

Which would produce `other_variable: "valueother_value1"`. Also environment variables will be expanded internally.

The following is a list of config items that need to be present in the config unless stated otherwise:

```yaml
%YAML 1.2
---
# not needed, shown here as an example of the !join tag
define: &root "$HOME/path/to/" # $HOME expands to /home/user, for example

title: "Example site"
path:
  src: !join [*root, "src"] # $HOME/path/to/src
  dst: "$HOME/some/other/path/to/dst"
  plt: "plt"
  db: !join [*root, "src/", "db.psv"]
url:
  main: "https://example.com"
fmt:
  date: "%a, %b %d, %Y @ %H:%M %Z"
  list_date: "%b %d"
  list_sep_date: "%B %Y"
dirs:
  /: # root "dir_path", whatever is sitting directly under "src"
	cfg:
	  plt: "page.html"
	  # the template can be specified instead of just True/False, a default template will used
	  tags: False
	  index: True
	  rss: True
	  sitemap: True
	  exclude_dirs: ["articles", "blog"] # optional; list of subdirectories to exclude when parsing the / dir_path
# below are other example "dir_paths", can be named anything, only the / (above) is mandatory
  articles:
    cfg:
	  plt: "page.html"
	  tags: True
	  index: True
	  rss: True
	  sitemap: True
  blog:
    cfg:
	  # ...
...
```

The config under `dirs` are just per-subdirectory configuration of directories under `src`. Only the `/` "dir_path" is required as it is the config for the root `src` path files.

The following will be added on runtime:

```yaml
%YAML 1.2
---
fmt:
  rss_date: "%a, %d %b %Y %H:%M:%S GMT" # fixed
  sitemap_date: "%Y-%m-%d" # fixed
info:
  version: "x.y.z" # current 'pyssg' version (0.5.1.dev16, for example)
  debug: True/False # depending if --debug was used when executing
  force: True/False # depending if --force was used when executing
rss_run_date: # date the program was run, formatted with 'fmt.rss_date'
sitemap_run_date: # date the program was run, formatted with 'fmt.sitemap_date'
...
```

You can add any other option/section that you can later use in the Jinja templates via the exposed config object. URL's shouldn't have the trailing slash `/`

## Available Jinja variables

These variables are exposed to use within the templates. The below list is displayed in the form of *variable (type) (available from): description*. `field1/field2/field3/...` describe config file section from the YAML file and option and `object.attribute` corresponding object and it's attribute.

- `config` (`dict`) (all): parsed config file plus the added options internally (as described in [config file](#config-file)).
- `dir_config` (`dict`) (all*): parsed dir_config file plus the added options internally (as described in [config file](#config-file)). *This is for all of the specific "dir_path" files, as per configured in the YAML file `dirs.dir_path.cfg` (for exmaple `dirs./.cfg` for the required dir_path).
- `all_pages` (`list(Page)`) (all): list of all the pages, sorted by creation time, reversed.
- `page` (`Page`) (`page.html`): contains the following attributes (genarally these are parsed from the metadata in the `*.md` files):
	- `title` (`str`): title of the page.
	- `author` (`list[str]`): list of authors of the page.
	- `lang` (`str`): page language, used for the general `html` tag `lang` attribute.
	- `summary` (`str`): summary of the page, as specified in the `*.md` file.
	- `content` (`str`): actual content of the page, this is the `html`.
	- `cdatetime` (`str`): creation datetime object of the page.
	- `cdate_rss` (`str`): formatted `cdatetime` as required by rss.
	- `cdate_sitemap` (`str`): formatted `cdatetime` as required by sitemap.
	- `mdatetime` (`str`): modification datetime object of the page. Defaults to `None`.
	- `mdate_rss` (`str`): formatted `mdatetime` as required by rss.
	- `mdate_sitemap` (`str`): formatted `mdatetime` as required by sitemap.
	- `tags` (`list(tuple(str))`): list of tuple of tags of the page, containing the name and the url of the tag, in that order. Defaults to empty list.
	- `url` (`str`): url of the page, this already includes the `url/main` from config file.
	- `image_url` (`str`): image url of the page, this already includes the `url/static`. Defaults to the `url/default_image` config option.
	- `next/previous` (`Page`): reference to the next or previous page object (containing all these attributes). Defaults to `None`.
	- `og` (`dict(str, str)`): dict for object graph metadata.
	- `meta` (`dict(str, list(str))`): meta dict as obtained from python-markdown, in case you use a meta tag not yet supported, it will be available there.
- `tag` (`tuple(str)`) (`tag.html`): tuple of name and url of the current tag.
- `tag_pages` (`list(Page)`) (`tag.html`): similar to `all_pages` but contains all the pages for the current tag.
- `all_tags` (`list(tuple(str))`) (all): similar to `page.tags` but contains all the tags.
