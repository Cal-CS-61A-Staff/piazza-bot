import re

NUMBERED_LIST_RE = '^\d+\.'

def reformat(text):
    """Convert hard-wrapped text to long lines."""
    while '  ' in text:
        text = text.replace('  ', ' ')
    paragraphs = text.split('\n\n')
    new_paragraphs = []

    for paragraph in paragraphs:
        lines = [l.strip() for l in paragraph.split('\n')]
        lines = [l for l in lines if l]
        new_lines = []

        current_line = []
        for line in lines:
            if re.match(NUMBERED_LIST_RE, line):
                new_lines.append(' '.join(current_line))
                current_line = [line]
            else:
                current_line.append(line)
        new_lines.append(' '.join(current_line))
        new_lines = [l for l in new_lines if l]

        new_paragraphs.append('\n'.join(new_lines))
    return '\n\n'.join(new_paragraphs)
