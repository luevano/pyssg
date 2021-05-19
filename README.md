# pyssg - Static Site Generator written in Python

Inspired (initially) by Roman Zolotarev's [`ssg5`](https://rgz.ee/bin/ssg5) and [`rssg`](https://rgz.ee/bin/rssg), Luke Smith's [`lb` and `sup`](https://github.com/LukeSmithxyz/lb) and, pedantic.software's great (but *"mamador"*, as I would say in spanish) [`blogit`](https://pedantic.software/git/blogit/).

I'm writing this in *pYtHoN* (thought about doing it in Go, but I'm most comfortable with Python at the moment) because I want features from all of these minimal programs (and more), but I don't really want to be stitching each one of the features on any of these programs, because they're written in a way to only work as how they were first imagined to work like; I already tried adding features to `ssg` and ended up rewriting it in POSIX shell, but it was a pain in the ass when I tried to add even more, and don't get me started on trying to extend `blogit`... And also because I want to.

## Current features

**This is still a WIP. Still doesn't build `sitemap.xml` or `rss.xml` files.**

- [x] Build static site parsing `markdown` files ( `*.md` -> `*.html`)
	- [x] Using plain `*.html` files for templates.
		- [ ] Would like to change to something more flexible and easier to manage ([`jinja`](), for example).
	- [x] Preserves hand-made `*.html` files.
	- [x] Tag functionality.
	- [ ] Open Graph (and similar) support.
- [ ] Build `sitemap.xml` file.
- [ ] Build `rss.xml` file.
- [x] Only build page if `*.md` is new or updated.
	- [ ] Extend this to tag pages and index (right now all tags and index is built no matter if no new/updated file is present).
- [x] Configuration file as an alternative to using command line flags (configuration file options are prioritized).

### Markdown features

This program uses the base [`markdown` syntax]() plus additional syntax, all thanks to [`python-markdown`](https://python-markdown.github.io/) that provides [extensions](https://python-markdown.github.io/extensions/). The following extensions are used:

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

That creates the desired directories with the basic templates that can be edited as desired. Place your `*.md` files somewhere inside the source directory (`src_dir` in the command above), but outside of the `templates` directory. It accepts sub-directories.

Build the site with:

```sh
pyssg -s src_dir -d dst_dir -u https://base.url -b
```

That creates all `*.html` for the site and can be easily moved to the server. Here, the `-u` flag is technically optional in the sense that you'll not receive a warning/error, but it's used to prepend links with this URL (not strictly required everywhere), so don't ignore it; also don't include the trailing `/`.
