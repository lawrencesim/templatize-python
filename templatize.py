from lib.interface import Interface
from lib.template import Template


class Templatize:

    @staticmethod
    def render(template, bindings, options=None):
        return Templatize.make(template, options).render(bindings, options)

    @staticmethod
    def make(template, options=None):
        return Interface(Template(template, options), options)
