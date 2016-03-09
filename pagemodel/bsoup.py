#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from pagemodel.html import BaseNode, BaseLeaf, Base
from pagemodel.pagemodel import PageModelMetaClass, BaseBasePageModel

import bs4


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
    def __init__(self, arg):
        if isinstance(arg, six.string_types):
            self.sel = bs4.BeautifulSoup(arg, "html.parser")
        else:
            self.sel = arg

    def css(self, *paths):
        """Return a list of nodes that satisfy any of provided
        css paths.
        """
        # musi być zrobione, że po kolei wywołuje, ponieważ
        # według BS4 przecinek wiąże silniej niż spacja w
        # selektorach css.
        sel_list = [self.sel.select(path.strip()) for path in paths]
        sel_list = [el for chunk in sel_list for el in chunk]
        return [Selector(sel) for sel in sel_list]

    def text(self):
        """
        Return all the text contained in a node as a string.
        :return: String containing all the taxt inside the node, w/o tags.
        """
        return self.sel.get_text()

    def textlist(self):
        return list(self.sel.strings)

    def get_attr(self, attr_name):
        """
        Returns value of specified attribute of this tag.
        :param attr_name: Name of the attribute.
        :return: Value of the attribute.
        """
        attr_value = self.sel[attr_name]
        if isinstance(attr_value, list):
            attr_value = ' '.join(attr_value)
        return attr_value
