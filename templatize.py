from lib.interface import Interface


class Templatize:

    @staticmethod
    def render(self, template, bindings, options):
        return self.from(template, options).render(bindings, options);

    @staticmethod
    def from(self, template, options):
        return Interface(Template(template, options), options);
