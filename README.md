# pyssg

Static Site Generator inspired by Roman Zolotarev's [`ssg5`](https://rgz.ee/bin/ssg5) and [`rssg`](https://rgz.ee/bin/rssg), Luke Smith's [`lb` and `sup`](https://github.com/LukeSmithxyz/lb) and, pedantic.software's [`blogit`](https://pedantic.software/git/blogit/).

The reason of making this in python is because I was tired of wanting (some) features from all of these minimal programs, but being a pain in the ass to maintain or add features on my own, specially to `blogit`...; making minimalist software it's great and all, but there is a limit on how pretentious and elitist a software can be for me to accept it.

## Current features

This is still a WIP. Still doesn't build `sitemap.xml` or `rss.xml` files.

- [x] Build static site parsing `markdown` files ( `*.md` -> `*.html`)
	- [x] Preserves hand-made `*.html` files.
	- [x] Tag functionality.
	- [ ] Open Graph (and similar) support.
- [ ] Build `sitemap.xml` file.
- [ ] Build `rss.xml` file.

## Markdown features

This program uses [`python-markdown`](https://python-markdown.github.io/) package with the following [extensions](https://python-markdown.github.io/extensions/):

- Extra (collection of QoL extensions).
- Meta-Data.
- Sane Lists.
- SmartyPants.
- Table of Contents.
- WikiLinks.

## Usage

First initialize the directories you're going to use for the source files and destination files:

```sh
pyssg -s src_dir -d dst_dir -i
```

That creates the desired directories with the basic templates that can be edited as desired. Place your `*.md` files somewhere inside the source directory (`src_dir` in the command above), but outside of the `templates` directory. It accepts sub-directories.

Build the site with:

```sh
pyssg -s src_dir -d dst_dir -b
```

That creates all `*.html` for the site and can be easily moved to the server. Where an optional `-u` flag can be provided for the base URL (don't include the trailing slash `/`)
