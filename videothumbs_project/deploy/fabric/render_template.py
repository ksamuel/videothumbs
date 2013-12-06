#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Simple templating tools for Python.
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

u"""
    Onliner to render templates with a choosen template engine using the
    command line, Python code or fabric tasks.

    Compatible rendering engines :

        - templite (default and provided);
        - django (to be installed);
        - jinja2 (to be installed).
"""


from __future__ import unicode_literals, absolute_import, print_function

import sys
import re
import argparse
import os
import json
import imp
import ast
import tempfile

from codecs import open
from ConfigParser import ConfigParser


try:
    from jinja2 import Environment

    env = Environment()

    def jinja2_render_string(string, context={}):
        """
            Render a jinja template passed as unicode string.
        """
        return env.from_string(open(string).read()).render(**context)


    def jinja2_render_file(path, context={}, encoding=sys.getfilesystemencoding()):
        """
            Render a template file.
        """
        return jinja2_render_string(open(path).read().decode(encoding), context)

except ImportError:
    pass


try:
    from django.template import Context, Template
    from django.conf import settings as django_settings

    DEFAULT_DJANGO_SETTINGS = {'TEMPLATE_DEBUG': False}

    def django_render_string(string, context={}, settings=DEFAULT_DJANGO_SETTINGS):
        """
            Render a django template passed as unicode string.

            If it's a dictionary,
            it will be passed as settings (all var names must be uppercase). If
            it's a string, DJANGO_SETTINGS_MODULE will be set
            using it.

            By default, if will use `{'TEMPLATE_DEBUG': False}` for settings.

            In the unlikely case that you ALREADY have DJANGO_SETTINGS_MODULE
            set before this call but settings are not configured yet,
            you can force to use it by passing a False value to settings.

            Returns a unicode string.
        """
        if not django_settings.configured:
            if isinstance(settings, basestring):
                os.environ['DJANGO_SETTINGS_MODULE'] = settings
            elif settings:
                django_settings.configure(**settings)

        return Template(string).render(Context(context))


    def django_render_file(path, context={}, encoding=sys.getfilesystemencoding(),
                           settings=DEFAULT_DJANGO_SETTINGS):
        """
            Render a django template file.

            If settings is False, os.environ['DJANGO_SETTINGS_MODULE'] is
            ignored and TEMPLATE_DEBUG is set to False. If it's a dictionary,
            it will be passed as settings (all var names must be uppercase). If
            it's astring, os.environ['DJANGO_SETTINGS_MODULE'] will be set
            using it.

            Returns a unicode string.
        """
        text = open(path).read().decode(encoding)
        return django_render_string(text, context, settings=settings)

except ImportError:
    pass


class Templite(object):
    """
        Templite template engine, from Thimo Kraemer and Tomer Filiba.

        See: http://www.joonis.de/en/code/templite

        GPL2 licensed.

        Usage :

            >>> t = Templite(template)
            >>> print t.render(variable1=value, variable2=value)

        Template syntax example :

            ${
            # embed pure Python code ...
            def say_hello(arg):
                emit("hello ", arg, "<br>")
            }$

            <table>
                ${
                    for i in range(10):
                        emit("<tr><td> ")
                        say_hello(i)
                        emit(" </tr></td>\n")
                    # ... or use or more descriptive language :
                }$
            </table>

            ${if x > 6:}$
                Rendered text...
                Abitrary code : ${print x}$
            ${:elif x > 3:}$
                This is great
            ${:endif}$

            ${for i in range(x-1):}$
                Of course you can use any type of block statement :
                ${i}$ ${"fmt: %s" % (i*2)}$
            ${:else:}$
                Single variables and expressions starting with quotes are substituted automatically.
                Instead $\{emit(x)}\$ you can write $\{x}\$ or $\{'%s' % x}\$ or $\{"", x}\$
                Therefore standalone statements like break, continue or pass
                must be enlosed by a semicolon: $\{continue;}\$
                The end
            ${:end-for}$


    """
    auto_emit = re.compile('(^[\'\"])|(^[a-zA-Z0-9_\[\]\'\"]+$)')

    def __init__(self, template, start='${', end='}$'):
        if len(start) != 2 or len(end) != 2:
            raise ValueError('each delimiter must be two characters long')
        delimiter = re.compile('%s(.*?)%s' % (re.escape(start), re.escape(end)), re.DOTALL)
        offset = 0
        tokens = []
        for i, part in enumerate(delimiter.split(template)):
            part = part.replace('\\'.join(list(start)), start)
            part = part.replace('\\'.join(list(end)), end)
            if i % 2 == 0:
                if not part: continue
                part = part.replace('\\', '\\\\').replace('"', '\\"')
                part = '\t' * offset + 'emit("""%s""")' % part
            else:
                part = part.rstrip()
                if not part: continue
                if part.lstrip().startswith(':'):
                    if not offset:
                        raise SyntaxError('no block statement to terminate: ${%s}$' % part)
                    offset -= 1
                    part = part.lstrip()[1:]
                    if not part.endswith(':'): continue
                elif self.auto_emit.match(part.lstrip()):
                    part = 'emit(%s)' % part.lstrip()
                lines = part.splitlines()
                margin = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
                part = '\n'.join('\t' * offset + l[margin:] for l in lines)
                if part.endswith(':'):
                    offset += 1
            tokens.append(part)
        if offset:
            raise SyntaxError('%i block statement(s) not terminated' % offset)
        self.__code = compile('\n'.join(tokens), '<templite %r>' % template[:20], 'exec')

    def render(self, __namespace=None, **kw):
        """
        renders the template according to the given namespace.
        __namespace - a dictionary serving as a namespace for evaluation
        **kw - keyword arguments which are added to the namespace
        """
        namespace = {}
        if __namespace: namespace.update(__namespace)
        if kw: namespace.update(kw)
        namespace['emit'] = self.write

        __stdout = sys.stdout
        sys.stdout = self
        self.__output = []
        eval(self.__code, namespace)
        sys.stdout = __stdout
        return ''.join(self.__output)

    def write(self, *args):
        for a in args:
            self.__output.append(str(a))


def templite_render_string(string, context={}):
    """
        Render a templite template passed as unicode string.
    """
    return Templite(string).render(**context)


def templite_render_file(path, context={}, encoding=sys.getfilesystemencoding()):
    """
        Render a templite template file.
    """
    return templite_render_string(open(path).read().decode(encoding), context)


def extract_context(path, encoding=sys.getfilesystemencoding()):
    """
        Extract variables from a INI, JSON or Python file, and
        returns a template context dictionary.
    """

    context = open(path, encoding=encoding)

    f, ext = os.path.split(path)

    if ext == '.json':
        return json.loads(context)

    if ext in ('.ini', '.cfg'):
        ConfigParser().read(context)

    return imp.load_source('', path).__dict__


try:
    from fabric.api import task
    from fabric.contrib.files import put

    @task
    def render(template, output, var_file=None, engine='templite',
               encoding=sys.getfilesystemencoding(), use_sudo=False, **kwargs):
        """
            Fabric task to render a template on a remote serveur.

            Template variables are extracted from var_file if any, and
            all addition arguments from `kwargs`.

            The template files must be on the LOCAL machine.
        """

        context = {}
        if var_file:
            context.update(extract_context(var_file, encoding))

        for name, value in kwargs.items():
            try:
                context[name] = ast.literal_eval(value)
            except:
                context[name] = value

        try:
            r = globals()['%s_render_file' % engine]
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(r(template, context, encoding=encoding))
            f.close()
            put(f.name, unicode(output))
        except KeyError:
            sys.exit('Could not import "%s" lib for rendering. Is it installed ?' % engine)
        finally:
            try:
                f.close()
                path(f.name).remove()
            except:
                pass

except ImportError:
    pass


if __name__ == '__main__':

    desc = u"""
        Render templates files from the command lines.

        Compatible rendering engines :

            - templite (default and provided);
            - django (to be installed);
            - jinja2 (to be installed).

        Any non listed arguments or options will be passed to the template engine
        as variable. You can also pass variables using a JSON, INI or Python file.
    """

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--template', type=str,
                         nargs='?', default="",
                         help="Path of the template file to render.")

    parser.add_argument('--var-file', nargs="?", type=str, default="",
                        help="Path of the file containing template variables.")

    parser.add_argument('--engine', type=str,
                         nargs='?', default="templite",
                         help="Template rendering engine to use.")

    parser.add_argument('--encoding', type=str,
                         nargs='?', default=sys.getfilesystemencoding(),
                         help="Encoding to use for both template and variables files.")

    namespace, remaining_args = parser.parse_known_args()

    if namespace.engine not in ('django, jinja2', 'templite'):
        sys.exit("This template engine is not supported.")

    context = {}
    if namespace.var_file:
        context.update(extract_context(namespace.var_file, namespace.encoding))

    if remaining_args:
        if len(remaining_args) % 2 != 0:
            sys.exit("Positiponal arguments are not supported")


        for name, value in zip(remaining_args[::2], remaining_args[1::2]):
            name = name.lstrip('-')
            try:
                context[name] = ast.literal_eval(value)
            except:
                context[name] = value

    try:
        local_vars = locals()
        if namespace.template:
            r = local_vars['%s_render_file' % namespace.engine]
            print(r(namespace.template, context, encoding=namespace.encoding))
        else:
            content = sys.stdin.read()
            r = local_vars['%s_render_string' % namespace.engine]
            encoding = sys.stdin.encoding or namespace.encoding
            print(r(content.decode(encoding), context))
    except NameError:
        sys.exit('Could not import "%s" lib for rendering. Is it installed ?' % namespace.engine)

