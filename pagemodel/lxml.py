#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import six


from pagemodel.html import BaseNode, BaseLeaf, Base
from pagemodel.pagemodel import PageModelMetaClass, BaseBasePageModel

from lxml import etree
from lxml.etree import XPath
from lxml.cssselect import CSSSelector
from lxml.html import html5parser


class BasePageModel(six.with_metaclass(PageModelMetaClass, BaseBasePageModel)):
    pass


class PageModel(BasePageModel, BaseLeaf):
    @classmethod
    def extract_unboxed(cls, selector):
        res = cls.page_tree.extract(selector)
        cls.postproc(res)
        return cls.model_class(**res)

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
    def __init__(self, arg, nsmap=None, css_translator='html', html_parser=None):
        if not nsmap:
            nsmap = {'html': "http://www.w3.org/1999/xhtml"}
        self.nsmap = nsmap
        self.css_translator = css_translator
        self.html_parser = html_parser
        if isinstance(arg, six.string_types):
            self.sel = html5parser.fromstring(arg, parser=self.html_parser)
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
        return self.sel.text

    def to_string(self):
        """Return XML code within content of current element."""
        return etree.tostring(self.sel)

    def textlist(self):
        raise NotImplementedError() # do not know what it does

    def get_attr(self, attr_name):
        return self.sel.get(attr_name)
