import mistune


class HtmlRenderer(object):
    pass


class MarkdownUtils(object):
    encoder = mistune.Markdown(renderer=mistune.HTMLRenderer(escape=False))

    @classmethod
    def to_html(cls, value):
        if value is None:
            return
        return cls.encoder(value)
