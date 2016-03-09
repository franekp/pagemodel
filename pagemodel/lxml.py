#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import six

from pagemodel.html import BaseLeaf
from pagemodel.pagemodel import PageModelMetaClass, BaseBasePageModel

from lxml import etree
from lxml.etree import XPath
from lxml.cssselect import CSSSelector

import html5lib


class BasePageModel(six.with_metaclass(PageModelMetaClass, BaseBasePageModel)):
    pass


class PageModel(BasePageModel, BaseLeaf):
    @classmethod
    def extract_unboxed(cls, selector):
        try:
            res = cls.page_tree.extract(selector)
            cls.postproc(res)
            return cls.model_class(**res)
        except ValueError as a:
            raise ValueError(cls.__name__ + ": " + str(a))

    def extract(self, selector):
        res = self.extract_unboxed(selector)
        return {self.fieldlabel: res}

    def __new__(cls, page_text=None):
        if page_text is None:
            res = super(PageModel, cls).__new__(cls)
            return res
        else:
            return cls.extract_unboxed(Selector(page_text))

    @classmethod
    def postproc(cls, dic):
        return dic


class Selector(object):
    @classmethod
    def _simple_html5_parser(cls, s):
        """
        Parses HTML code into tree (html namespace is converted to void namespace)
        :param s: HTML code to parse
        :return: Lxml tree representing the code
        """
        parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
        return parser.parse(s)

    def __init__(self, arg, nsmap=None, css_translator='html', html_parser=None):
        if not nsmap:
            nsmap = {}
        if not html_parser:
            html_parser = Selector._simple_html5_parser
        self.nsmap = nsmap
        self.css_translator = css_translator
        self.html_parser = html_parser
        if isinstance(arg, six.string_types):
            self.sel = self.html_parser(arg)
        else:
            self.sel = arg

    def css(self, *paths):
        """Return a list of nodes that satisfy any of provided
        css paths.
        """
        sel_list = [CSSSelector(path, translator=self.css_translator, namespaces=self.nsmap)(self.sel) for path in paths]
        sel_list = [el for chunk in sel_list for el in chunk]
        sel_list = set(sel_list)
        return [Selector(sel, nsmap=self.nsmap, css_translator=self.css_translator, html_parser=self.html_parser) for sel in sel_list]

    def xpath(self, *paths):
        """Return a list of nodes that satisfy any of provided
        xpath paths.
        """
        sel_list = [XPath(path, namespaces=self.nsmap)(self.sel) for path in paths]
        sel_list = [el for chunk in sel_list for el in chunk]
        sel_list = set(sel_list)
        return [Selector(sel, nsmap=self.nsmap, css_translator=self.css_translator, html_parser=self.html_parser) for sel in sel_list]

    def name(self):
        """Returns tag name or attribute name."""
        return self.sel.tag

    def text(self):
        """Return all the text contained in a node as a string."""
        res = ''.join([s for s in self.sel.itertext()])
        return res

    def fragment(self):
        """Return XML code within content of current element."""
        return etree.tostring(self.sel)

    def textlist(self):
        raise NotImplementedError() # do not know what it does

    def get_attr(self, attr_name):
        """
        Returns value of specified attribute of this tag.
        :param attr_name: Name of the attribute.
        :return: Value of the attribute.
        """
        return self.sel.get(attr_name)
