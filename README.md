# Templatize (Python)

Basic templating code. It originally started as needing a very simplistic template library, hence creating my own version, before snowballing requirements (and also just personal curiosity on where I could take it) turned it into a powerful templating library of its own.

This is the Python port of the javascript library (https://github.com/lawrencesim/templatize).

Lawrence Sim © 2023

## Contents

* [Usage](#usage)
* [The Basics](#the-basics)
    * [Variables](#variables)
    * [Lists](#lists)
    * [Sections](#sections)
    * [Scoping and context](#scoping-and-the-context-directive)
    * [Functions](#functions)
    * [Formatting](#formatting)
* [More Topics (including comparison with Mustache)](#more-topics)
* [Acknowledgments](#acknowledgments)

----------


&nbsp; 


## Usage

Import Templatize from wherever your library is installed. E.g.:

```python
from templatize import Templatize
```

The most basic use-case is to simply call the `Templatize.render()` function.

```python
import Templatize from templatize

rendered = Templatize.render(my_template, bindings)
```

However this will not take advantage of caching the processed template. If reusing the template, one can first create a rendering instance from said template using `Templatize.make()`, then call the render function on that instance.

```python
import Templatize from templatize

template_one = Templatize.make(my_template, {'eval_zero_as_true': True})
rendered = template_one.render(bindings)
```

<a href="templatize-render" name="templatize-render">#</a> *Templatize*.**render**(*template*, *bindings*[, *options*])

| Name | Type | Description |
| --- | --- | :--- |
| `template` | str | The template. |
| `bindings` | dict | The dictionary of data-bindings. |
| `options` | dict | See [options](#options). |

&nbsp; &nbsp; &nbsp; &nbsp;**Returns:** (str) The rendered template.

<a href="templatize-make" name="templatize-make">#</a> *Templatize*.**make**(*template*[, *options*])

&nbsp; &nbsp; &nbsp; &nbsp;**Returns:** (Interface) An instance of the Templatize rendering interface based off this template.

<a href="templatize-instance-render" name="templatize-instance-render">#</a> *Interface*.**render**(*bindings*[, *options*])

&nbsp; &nbsp; &nbsp; &nbsp;**Returns:** (str) The rendered template.

### Options

* **`delimiters`** - (*default:* `["{{", "}}"]`) Set custom delimiters here as list of strings. Only available in *Templatize*.**make()** when creating a new instance off a preprocessed template.
* **`error_on_func_failure`** - (*default:* `False`) If true, throw exceptions resulting from function calls in the data-bindings. Otherwise, simply warns in the console and returns empty for the binding being evaluated.
* **`eval_zero_as_true`** - (*default:* `False`) If true, zero-values are treated as a real value for section evaluation. See [section value evaluation](#section-value-evaluation).
* **`escape_all`** - (*default:* `False`) If true, all tags are by default HTML special-character escaped. Any tag printing unescaped code needs the specific formatting directive. See [formatting](#formatting).
* **`error_on_missing_tags`** - (*default:* `False`) If true, throw exceptions when a data-binding called by the template is missing. Otherwise, simply warns in the console and returns empty.

----------


&nbsp;


## The Basics

Templates are strings in which tags define where the text will be dynamically replaced and updated. By default, tags use the double-curly-braces delimiters (e.g. `{{likeThis}}`). The value inside the tag is the key or key name, which may be supplemented by special characters called directives that instruct special-case use or handling of the tag.

Whitespace between the delimiters and the inner key (and directives) are generally trimmed and ignored by the renderer, but as a general rule, either use no whitespaces or only between the delimiters and key, not within the key value itself -- e.g. `{{likeThis}}` or `{{ likeThis }}` but `{{ not like this }}`.

The data-binding for a tag is the data, identified by the tag key, that will be supplanted in the tag's place.

&nbsp;

### Variables

Variables are the most basic use-case, where the tag will render the data-binding value associated with the tag's key. Dot-notation may be used to traverse the data-structure.

&nbsp; *Template:*

```
{{name.first}} is {{age}} years old.
```

&nbsp; *Bindings:*

```python
{
  'name': { 'first': "Bob" }, 
  'age': 46
}
```

&nbsp; *Outputs:*

```
Bob is 46 years old.
```

The default behavior is to treat missing bindings as empty. You may also throw an exception when encounter a missing binding by setting the `error_on_missing_tags` parameter in [the render options](#options).

&nbsp; 

### Comments and escaping

Both commenting and escaping are done with a bang directive (`!`). For comments, place the bang within the opening delimiter. For escaping, place the bang just outside the opening delimiter.

&nbsp; *Template:*

```
{{name.first}} is !{{age}} years old. {{! note to self: is this the right age? }}
```

&nbsp; *Bindings:*

```python
{
  'name': { 'first': "Bob" }, 
  'age': 46
}
```

&nbsp; *Outputs:*

```
Bob is {{age}} years old.
```

&nbsp; 

### Naming restrictions

**Restrictions for tag key names**

* `_display` is a special keyword. While it can be set (see the [_display parameter](./more/sections/#the-_display-parameter)), it should only be done when specifically calling said functionality.
* Any key name with a leading bang (`!`) will be treated as an [comment](#comments-and-escaping) in the template code.
* Any key name with a leading directive used for [lists](#lists) and [sections](#sections) -- which include ampersand (`&`), hash (`#`), and caret (`^`) -- will be interpreted as such and not considered part of the key name.
* Ending a key name with a semi-colon (`;`) will be interpreted as the escape [formatting](#formatting) directive and not part of the key name.
* Using in any place a double-colon (`::`), which is a [formatting](#formatting) directive, or an arrow operator (`->`), which is used for [passing context to functions](./more/functions/#passing-context-to-functions), will be interpreted as their respective directives.

**Things to avoid in tag key names**

* While whitespaces can be part of the key name, it is generally not good practice. At the very least avoid using it as leading or trailing characters. Templatize will generally handle trimming and adjust in cases where it does exist, but proper behavior cannot be fully guaranteed.
* While dots (`.`) can mostly be used in the key name without failing (though a few edge-cases may still result in odd behavior), it is generally to be avoided to reduce naming confusion.


&nbsp;


## Lists

Lists are marked with an ampersand (`&`) and can take in an list (or a function that returns an list). The output is grammatically formatted with appropriate use of commas and/or the 'and'-conjunction, as dictated by the length of the list. No other dynamic text or subsections should be nested within a list, and values within the list should be strings or numbers only for best results.

One special case exists with the list functionality, the combination of the list and section directive (`&#`) which can be used to [grammatically list repeating sections](./more/sections#repeating-list-sections).

&nbsp; *Template:*

```
{{&name}} sells {{&sells}} with his {{&with}}. 
```

&nbsp; *Bindings:*

```python
{
  'name': ["Bob"], 
  'sells': ["burgers", "sodas", "fries"], 
  'with': ["wife", "kids"]
}
```

&nbsp; *Outputs:*

```
Bob sells burgers, sodas, and fries with his wife and kids.
```

*Note, the Oxford-comma is the default -- and only -- behavior, as the universe intended.*


&nbsp; 


## Sections

Section start at tags with the `#`-directive and end at the corresponding tags with the `/`-directive. If the data bound to the tag evaluates as true, the content between the section tags will be shown. Conversely, it will be hidden if it evaluates to false. 

You may also inverse the rules for showing and hiding a section by replacing the hash (`#`) with a caret (`^`) in the section start tag.

&nbsp; *Template:*

```
Bob is {{#married}}married{{/married}}{{#single}}single{{/single}}.
<br />
{{#spouse}}Bob is married to {{spouse}}.{{/spouse}}
<br />
Bob has {{^haspets}}no pets{{/haspets}}{{#haspets}}pets{{/haspets}}.
```

&nbsp; *Bindings:*

```python
{
  'married': True, 
  'single': False, 
  'spouse': "Linda", 
  'haspets': False
}
```

&nbsp; *Outputs:*

```
Bob is married.
Bob is married to Linda.
Bob has no pets.
```

### Section value evaluation

The data bound to a section tag is evaluated for 'truthiness'. `None` values, an empty string or composed only of whitespace, an empty list, and `0` evaluate as false (though in certain cases you may want to [treat 0-values as true](./more/sections/#treating-zero-values-as-true)). Otherwise, as long as data-binding for section evaluates to true, it will be treated as such. You may use this as a shortcut for both displaying the section and formatting its value. 

&nbsp;

### More on sections

See additional documentation for more on [sections](./more/sections/), including [section value evaluation](./more/sections/#section-value-evaluation), the [`_display` parameter](./more/sections/#the-_display-parameter), and more.

&nbsp; 

### Repeating Sections

If the value bound to a section tag is a list (or function that evaluates to an list), the section will be repeated for as many items as exists in the list. 

Within the context of the repeating section (that is, between the opening and closing section tags), the same tag key is temporarily bound to the value of each item during each iteration. Thus, the tag key can be used within the section context to access the inner values as it iterates through the list.

&nbsp; *Template:*

```
{{#children}}Child: {{children}}<br />{{/children}}
```

&nbsp; *Bindings:*

```python
{'children': ["Tina", "Gene", "Louise", "", None, False, 0]}
```

&nbsp; *Outputs:*

```
Child: Tina
Child: Gene
Child: Louise
```

Note that each item is also treated to the same [section value evaluation](./more/sections/#section-value-evaluation) to determine whether it is rendered.

&nbsp;

### More on repeating sections

See additional documentation for more on [repeating sections](./more/sections/#repeating-sections).


&nbsp; 


## Scoping and the context directive

All keys in template tags must provide the full path to the data-binding, even if within a section. However, one way to shortcut to the inner-most context is by prefacing the tag key with the context directive (`.`). A naked context tag (`{{.}}`) is particularly useful for repeating sections with flat values.

&nbsp; *Template:*

```
{{#name}}1. {{name.first}}{{/name}}<br />
{{#name}}2. {{first}}{{/name}}<br />
{{#name}}3. {{.first}}{{/name}}
<br /><br />
Friends: {{#friends}}{{.}} {{/friends}}
```

&nbsp; *Bindings:*

```python
{
  'name': {'first': "Bob"}, 
  'friends': ["Teddy", "Mort"]
}
```

&nbsp; *Outputs:*

```
1. Bob
2.
3. Bob

Friends: Teddy Mort
```

In the above, we try to access `name.first` in three ways. Using the full binding path (1) works in almost any case. However, using `first` without giving a context (2), fails as it tries to find a binding for `first` from the root, which does not exist. We can fix this by providing the context directive (3), which begins the search from the given context, with is within the section (and corresponding data-binding for) `name`.

The naked context tag (`{{.}}`) in the final line is equivalent to the tag `{{friends}}`, which in-context of a repeating section, accesses each iterated value in the list.


&nbsp;


## Functions

Functions are evaluated and uses the returned value as the data-binding to the tag. As the behavior of the function depends on what is returned, it may be used in a variety of contexts, such as using the function output as a section or list.

The function is given the context of the data-binding object where it resides (accessed via `self`) and the full/root data-binding object (`root`) as arguments.

&nbsp; *Template:*

```
{{fullname}}'s friends include {{&friends}}.
```

&nbsp; *Bindings:*

```python
# lambda functions are used here for simplicity but in actual use could be references to functions to keep the code cleaner
{
  'name': {
    'first': "Bob", 
    'last': "Belcher"
  },
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
}
```

&nbsp; *Outputs:*

```
Bob Belcher's friends include Teddy and Mort.
```

Note, since none of the tags were called in context, for the functions called, `self` and `root` will refer to the same (the root data-binding).

&nbsp;

### Error handling

By default, functions fail silently. If an error occurs during function call, exception is not raised further and value is assumed to be an empty string. To change this, simply set the `error_on_func_failure` flag to `true` in the [options](../README.md#options).

&nbsp;

### More on functions

Functions are arguably the most powerful (and sometimes frustrating) aspect of Templatize, especially paired with the [pass-context-to-function directive](./more/functions/#passing-context-to-functions). This section only covers the most superficial use of functions.

See additional documentation for more on [functions](./more/functions/).


&nbsp;


## Formatting

Formatting options are also available by suffixing the key name in the template code with a double-colon (`::`) and following with a format key. For strings, a few of the commonly recognized values are detailed in the below table. If not recognized, Templatize passes the format key to python's `str.format()`.


* **html** - If the [option](#options) `escape_all` is set true, this key sets the output not to escape HTML special characters.
    * **raw** - Same as above.
* **encode** - Encodes HTML special characters in rendered output.
* **upper** - Transforms all alphabetical characters to uppercase.
    * **caps** - Same as above.
    * **allcaps** - Same as above.
* **lower** - Transforms all alphabetical characters to lowercase.
* **capitalize** - Capitalizes the first letter in each word.

Additionally, you can shorthand the **encode** format directive and key by suffixing a semi-colon (`;`) to the end of the tag name. It may even be combined with another format directive.

&nbsp; *Template:*

```
{{name::capitalize}} lives in {{locale::capitalize}} 
    and sells burgers for {{price.burger::$.2f}}.
{{break}}
{{break::encode}}{{break;}}{{break::upper;}}
```

&nbsp; *Bindings:*

```python
{
  'name': "bob", 
  'locale': "new england", 
  'price': { 'burger': 5 }, 
  'break': "<br />"
}
```

&nbsp; *Outputs:*

```
Bob lives in New England and sells burgers for $5.00.
<br /><br /><BR />
```

Formatting also works for [lists](#lists) and [functions](#functions).

&nbsp; *Template:*

```
Order: {{&order::lower}}<br />
Prices: {{&ticket::$.2f}}<br />
Sale tax: {{salesTax::.0%}}<br />
Total: {{total::$.2f}}<br />
Total (w/ tax): {{addTax::$.2f}}
```

&nbsp; *Bindings:*

```python
{
  'order': ["BURGER", "FRIES"], 
  'prices': {
    'BURGER': 5, 
    'FRIES': 2
  }, 
  'ticket': lambda self, root : list(map(lambda item : self["prices"][item], self["order"]), )
  'salesTax': 0.05, 
  'total': lambda self, root : sum(self["prices"][item] for item in self["order"]), 
  'addTax': lambda self, root : self["total"](self, root) * (1+self["salesTax"])
}
```

&nbsp; *Outputs:*

```
Order: burger and fries
Prices: $5.00 and $2.00
Sale tax: 5%
Total: $7.00
Total (w/ tax): $7.35
```

&nbsp; 


## More Topics

The above only takes a cursory glance at some of the directives. Be sure to look into the additional documentation below.

* [More about sections and repeating sections](./more/sections/)
* [More about functions](./more/functions/)

&nbsp;

#### Advanced usage, edge cases, and general weirdness

That's all great, you may be thinking, but what about if I [pass a function to itself](./more/advanced/#passing-a-function-to-itself)? Or [use a context-pass-to-function directive in the section tag](./more/advanced/#mixing-directives-in-a-section-tag)? What about [multi-dimensional lists](./more/advanced/#mutli-dimensional-lists)? Did you think of all that?

Well luckily for you, you sadist, we have such a section on [advanced usage, edge cases, and general weirdness](./more/advanced/).

&nbsp;

#### Templatize vs Mustache

Time to address the elephant in the room. Why recreate what Mustache (basically) already does? How does Templatize differ? Which is better? Which is faster? The quick answers are: just because, much more powerful function directives (among a few other syntactic differences), depends what you want, and probably Mustache.js. But if you want a little more substance to those answers, see [Templatize vs. Mustache](./more/compared/).


-----


&nbsp;