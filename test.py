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
    "template": r"{{#job}}Occupation: {{job.title}}{{/job}}<br />{{#jobflat}}Occupation: {{.}}{{/jobflat}}<br />Bob is a {{#jobhide}}{{jobhide.title}}{{/jobhide}}", 
    "bindings": {
        'job': {'title': "Chef"}, 
        "jobflat": "Chef", 
        'jobhide': {'title': "Chef", "_display": False}, 
    }, 
    "expected": r"Occupation: Chef<br />Occupation: Chef<br />Bob is a "
}
test_sections_2 = {
    "template": r"Profit:<br />Monday - {{#monday}}{{monday::$.2f}}{{/monday}}{{^monday}}Closed{{/monday}}<br />Sunday - {{#sunday}}{{sunday::$.2f}}{{/sunday}}{{^sunday}}Closed{{/sunday}}<br />Saturday - {{#saturday}}{{saturday::$.2f}}{{/saturday}}{{^saturday}}Closed{{/saturday}}<br />", 
    "bindings": {
      'monday': None, 
      'sunday': 0, 
      'saturday': 122
    }, 
    "options": {"eval_zero_as_true": True}, 
    "expected": r"Profit:<br />Monday - Closed<br />Sunday - $0.00<br />Saturday - $122.00<br />"
}
test_sections_3 = {
    "template": r"{{#children}}Child: {{.firstName}}<br />{{/children}}", 
    "bindings": {
      'children': [
        {'firstName': "Tina"}, 
        {'firstName': "Gene"}, 
        {'firstName': "Louise"}, 
        {'firstName': "Kuchi-Kopi", '_display': False}
      ]
    }, 
    "expected": r"Child: Tina<br />Child: Gene<br />Child: Louise<br />"
}
test_sections_4 = {
    "template": r"{{name.first}}'s children are {{&#children}}{{.}} {{name.last}}{{/children}}.", 
    "bindings": {
      'name': {
        'first': "Bob", 
        'last': "Belcher"
      }, 
      'children': ["Tina", "Gene", "Louise"]
    }, 
    "expected": r"Bob's children are Tina Belcher, Gene Belcher, and Louise Belcher."
}
test_sections_5 = {
    "template": r"{{#children}}{{.name.first}} {{name.last}}'s hobbies include {{&.hobbies}}.<br />{{/children}}", 
    "bindings": {
      'name': {
        'first': "Bob", 
        'last': "Belcher"
      }, 
      'children': [
        {
          'name': {'first': "Tina"},
          'hobbies': ["butts", "Equestranauts", "Boyz 4 Now"]
        }, 
        {
          'name': {'first': "Gene"},
          'hobbies': ["music", "farts"]
        }, 
        {
          'name': {'first': "Louise"},
          'hobbies': ["mischief"]
        }
      ]
    }, 
    "expected": r"Tina Belcher's hobbies include butts, Equestranauts, and Boyz 4 Now.<br />Gene Belcher's hobbies include music and farts.<br />Louise Belcher's hobbies include mischief.<br />"
}
test_sections_6 = {
    "template": r"{{#n->increment}}{{#n->increment}}{{n}}{{/n}}{{/n}} -- {{n}}", 
    "bindings": {
      'n': 1,
      'increment': lambda self, root : self + 1
    }, 
    "expected": r"3 -- 1"
}
test_sections_7 = {
    "template": r"{{#repeat}}{{#repeat}}{{.}} {{/repeat}}{{/repeat}}", 
    "bindings": {'repeat': [1,2,3]} , 
    "expected": r"1 2 3 "
}
test_functions_1 = {
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
test_functions_2 = {
    "template": r"Menu: <br />{{menu.burger.name::capitalize}} - {{menu.burger.price::$.2f}}.<br />{{menu.fries.name::capitalize}} - {{menu.fries.price::$.2f}}.<br />{{menu.soda.name::capitalize}} - {{menu.soda.price::$.2f}}. ", 
    "bindings": { 
      'burger': {'name': "burger", 'price': 5}, 
      'fries': {'name': "fries", 'price': 2}, 
      'soda': {'name': "soda", 'price': 2}, 
      'menu': lambda self, root : {'burger': self['burger'], 'fries': self['fries'], 'soda': self['soda']}
    }, 
    "expected": r"Menu: <br />Burger - $5.00.<br />Fries - $2.00.<br />Soda - $2.00."
}
test_functions_3 = {
    "template": r"{{main->fullname}}'s kids are:<br />{{#children}}{{children->fullname}} ({{children->age}} years old)<br />{{/children}}", 
    "bindings": {
      'main': {
        'name': "Bob"
      }, 
      'familyName': "Belcher", 
      'children': [
        {'name': "Tina", 'born': 2008}, 
        {'name': "Gene", 'born': 2010}, 
        {'name': "Louise", 'born': 2012}
      ], 
      'fullname': lambda self, root : self['name'] + " " + root['familyName'], 
      'age': lambda self, root : 2021 - self['born']
    }, 
    "expected": r"Bob Belcher's kids are:<br />Tina Belcher (13 years old)<br />Gene Belcher (11 years old)<br />Louise Belcher (9 years old)<br />"
}
def test_functions_4_func(self, root):
  root["i"] += 1
  return root["i"]
test_functions_4 = {
    "template": r"{{count}}, {{.->count}}-{{i}}, {{count}}-{{i}}, {{.->count}}-{{i}}", 
    "bindings": {
      'i': 0, 
      'count': test_functions_4_func
    }, 
    "expected": r"1, 2-2, 1-2, 3-2"
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


for i,test in enumerate([
    # test_basic_1, 
    # test_basic_2, 
    # test_basic_list, 
    # test_basic_section_1, 
    # test_basic_section_2, 
    # test_basic_context, 
    # test_basic_formatting_1, 
    # test_basic_formatting_2, 
    # test_sections_1, 
    # test_sections_2, 
    # test_sections_3, 
    # test_sections_4, 
    # test_sections_5, 
    # test_sections_6, 
    # test_sections_7, 
    test_functions_1, 
    test_functions_2, 
    test_functions_3, 
    test_functions_4
]):
    print("------Test {0}------".format(i+1))
    rendered = Templatize.render(test["template"], test["bindings"], test["options"] if "options" in test else None)
    print(test["expected"])
    print(rendered)
    if rendered.strip() != test["expected"].strip():
        print("---TEST {0} FAILED--".format(i+1))
        exit()
