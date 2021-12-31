from templatize import Templatize


test_basic_1 = {
    "template": r"{{name.first}} is {{age}} years old.", 
    "bindings": {
      'age': 46, 
      'name': { 'first': "Bob" }
    }, 
    "expected": r"Bob is 46 years old."
}
test_basic_2 = {
    "template": r"{{name.first}} is !{{age}} years old. {{! note to self: is this the right age? }}", 
    "bindings": {
      'age': 46, 
      'name': { 'first': "Bob" }
    }, 
    "expected": r"Bob is {{age}} years old."
}
test_basic_list = {
    "template": r"{{&name::capitalize}} sells {{&sells}} with {{&with}}. ", 
    "bindings": {
      'name': ["bob"], 
      'sells': ["burgers", "sodas", "fries"], 
      'with': ["his wife", "kids"]
    }, 
    "expected": r"Bob sells burgers, sodas, and fries with his wife and kids."
}
test_basic_section_1 = {
    "template": r"Bob is {{#married}}married{{/married}}{{#single}}single{{/single}}.<br />{{#spouse}}Bob is married to {{spouse}}.{{/spouse}}<br />Bob has {{^haspets}}no pets{{/haspets}}{{#haspets}}pets{{/haspets}}.", 
    "bindings": {
      'married': True, 
      'single': False, 
      'spouse': "Linda", 
      'haspets': False
    }, 
    "expected": r"Bob is married.<br />Bob is married to Linda.<br />Bob has no pets."
}
test_basic_section_2 = {
    "template": r"{{#children}}Child: {{children}}<br />{{/children}}", 
    "bindings": {'children': ["Tina", "Gene", "Louise", "", None, False, 0]}, 
    "expected": r"Child: Tina<br />Child: Gene<br />Child: Louise<br />"}
test_basic_context = {
    "template": r"{{#name}}1. {{name.first}}{{/name}}<br />{{#name}}2. {{first}}{{/name}}<br />{{#name}}3. {{.first}}{{/name}}<br /><br />Friends: {{#friends}}{{.}} {{/friends}}", 
    "bindings": {
      'name': {'first': "Bob"}, 
      'friends': ["Teddy", "Mort"]
    }, 
    "expected": r"1. Bob<br />2. <br />3. Bob<br /><br />Friends: Teddy Mort"
}
test_basic_functions = {
    "template": r"{{fullname}}'s friends include {{&friends}}.", 
    "bindings": {
  'name': {
        'first': "Bob", 
        'last': "Belcher"
      },
      # in this case, this/root will refer to the same 
      'fullname': lambda self, root : "{0} {1}".format(self['name']['first'], root['name']['last']), 
      'relations': [
        {'name': "Teddy", 'friendly': True}, 
        {'name': "Mort", 'friendly': True}, 
        {'name': "Jimmy Pesto", 'friendly': False}
      ], 
      'friends': lambda self, root : list(map(
        lambda person : person['name'], 
        filter(lambda person : person['friendly'], self['relations'])
      ))
    }, 
    "expected": r"Bob Belcher's friends include Teddy and Mort."
}
test_basic_formatting_1 = {
    "template": r"{{name::capitalize}} lives in {{locale::capitalize}} and sells burgers for {{price.burger::$.2f}}.{{break}}{{break::encode}}{{break::upper;}}{{break;}}", 
    "bindings": {
      'name': "bob", 
      'locale': "new england", 
      'price': { 'burger': 5 }, 
      'break': "<br />"
    }, 
    "expected": r"Bob lives in New England and sells burgers for $5.00.<br />&lt;br /&gt;&lt;BR /&gt;&lt;br /&gt;"
}
test_basic_formatting_2 = {
    "template": r"Order: {{&order}}<br />Prices: {{&ticket::$.2f}}<br />Sale tax: {{salesTax::.0%}}<br />Total: {{total::$.2f}}<br />Total (w/ tax): {{addTax::$.2f}}", 
    "bindings": {
      'order': ["BURGER", "FRIES"], 
      'prices': {
        'BURGER': 5, 
        'FRIES': 2
      }, 
      'ticket': lambda self, root : list(map(lambda item : self["prices"][item], self["order"])), 
      'salesTax': 0.05, 
      'total': lambda self, root : sum(self["prices"][item] for item in self["order"]), 
      'addTax': lambda self, root : self["total"](self, root)*(1+self["salesTax"])
    }, 
    "expected": r"Order: BURGER and FRIES<br />Prices: $5.00 and $2.00<br />Sale tax: 5%<br />Total: $7.00<br />Total (w/ tax): $7.35"
}
test_sections_1 = {
    "template": r"{{#job}}Occupation: {{job.title}}{{/job}}<br />{{#job}}Occupation: {{.}}{{/job}}", 
    "bindings": {'job': {'title': "Chef"}}, 
    "expected": r"Occupation: Chef<br />Occupation: Chef"
}
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }
# test_ = {
#     "template": r"", 
#     "bindings": , 
#     "expected": r""
# }


for i,test in enumerate([
    test_basic_1, 
    test_basic_2, 
    test_basic_list, 
    test_basic_section_1, 
    test_basic_section_2, 
    test_basic_context, 
    test_basic_functions, 
    test_basic_formatting_1, 
    test_basic_formatting_2, 
    test_sections_1
]):
    print("------Test {0}------".format(i+1))
    rendered = Templatize.render(test["template"], test["bindings"])
    print(test["expected"])
    print(rendered)
    if rendered.strip() != test["expected"].strip():
        print("---TEST {0} FAILED--".format(i+1))
        exit()
