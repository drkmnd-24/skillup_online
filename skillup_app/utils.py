import markdown as md

def render_markdown(text: str) -> str:
    return md.markdown(
        text or '',
        extensions=[
            'extra',
            'codehilite',
            'sane_lists',
            'toc',
        ],
        output_format='html5',
    )
