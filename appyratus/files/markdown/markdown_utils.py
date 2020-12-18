import mistune


class HtmlRenderer(object):
    pass


class Markdown2Html(object):
    encoder = mistune.Markdown(renderer=mistune.HTMLRenderer(escape=False))

    def perform(self, value):
        if value is None:
            return
        return self.encoder(value)
