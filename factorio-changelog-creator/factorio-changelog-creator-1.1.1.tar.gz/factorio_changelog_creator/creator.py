from string import Template

import logging

logger = logging.getLogger(__name__)

format_templates = {
    "md": {
        "message": "Generating Markdown Changelog",
        "heading": "# Changelog\n",
        "separator": "\n---\n",
        "version": Template("\n## $version\n"),
        "category": Template("\n### $category\n"),
        "change": Template("- $change$more$by\n"),
        "url": Template("[$text]($target)"),
    },
    "ingame": {
        "message": "Generating In-game Changelog",
        "separator": "---------------------------------------------------------------------------------------------------\n",
        "version": Template("Version: $version\n"),
        "date": Template("Date: $date\n"),
        "category": Template("\n  $category"),
        "change": Template("    - $change$more$by\n"),
        "more_url": Template("$target"),
        "by_url": Template("$text"),
    },
    "forum": {
        "message": "Generating Factorio Forum Changelog",
        "version": Template("[size=150][b]$version[/b][/size]\n"),
        "category": Template("\n[b]$category[/b]\n"),
        "list_start": "[list]\n",
        "list_end": "[/list]\n",
        "change": Template("[*] $change$more$by\n"),
        "url": Template("[url=$target]$text[/url]"),
    },
}

format_filenames = {
    "md": "CHANGELOG.md",
    "ingame": "changelog.txt",
    "forum": "changelog_forum.txt",
}

change_defaults = {"more": "", "by": ""}


def _entries_formatter(template, entries, entries_type):
    entries_output = " more: " if entries_type == "more" else " by "
    if not isinstance(entries, list):
        entries = [entries]
    for i, entry in enumerate(entries):
        if i:
            entries_output += ", "
        if isinstance(entry, dict):
            text = next(iter(entry))
            if "url" in template:
                entries_output += template["url"].substitute(
                    text=text, target=entry[text]
                )
            else:
                entries_output += template[f"{entries_type}_url"].substitute(
                    text=text, target=entry[text]
                )
        else:
            entries_output += entry
    return entries_output


def _change_formater(template, changes):
    changes_output = template["list_start"] if "list_start" in template else "\n"
    for change in changes:
        if isinstance(change, dict):
            more_text = (
                _entries_formatter(template, change["more"], "more")
                if "more" in change
                else ""
            )
            by_text = (
                _entries_formatter(template, change["by"], "by")
                if "by" in change
                else ""
            )
            changes_output += template["change"].substitute(
                change=change["change"], more=more_text, by=by_text
            )
        else:
            changes_output += template["change"].substitute(
                change_defaults, change=change
            )
    changes_output += template["list_end"] if "list_end" in template else ""
    return changes_output


def _version_formatter(template, version, data, first):
    version_output = ""
    if "separator" in template:
        if first and "heading" in template:
            version_output += template["heading"]
        else:
            version_output += template["separator"]
    version_output += template["version"].substitute(version=version)
    if "date" in template and "date" in data:
        version_output += template["date"].substitute(date=data["date"])
    if "Categories" in data:
        for category, category_data in data["Categories"].items():
            version_output += template["category"].substitute(category=category)
            version_output += _change_formater(template, category_data)
    if "Changes" in data:
        if "Categories" in data:
            version_output += template["category"].substitute(category="Other")
            version_output += _change_formater(template, data["Changes"])
        else:
            version_output += _change_formater(template, data["Changes"])
    return version_output


def create_changelog(input_data, format_template):
    output = ""

    first = True
    for version, data in input_data.items():
        output += _version_formatter(format_template, version, data, first)
        first = False

    return output


def get_format_template(format_name):
    return format_templates[format_name]


def get_format_filename(format_name):
    return format_filenames[format_name]


if __name__ == "__main__":
    pass
