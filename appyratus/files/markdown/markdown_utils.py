import mistune


class Markdown2Html(object):
    encoder = mistune.Markdown(renderer=mistune.HTMLRenderer())

    def perform(self, value):
        if value is None:
            return
        return self.encoder(value)
