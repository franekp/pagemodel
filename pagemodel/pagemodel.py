#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pagemodel.html import BaseNode, BaseLeaf, Base


class PageModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name in ['PageModel', 'BasePageModel']:
            return super(PageModelMetaClass, cls).__new__(cls, name, bases, attrs)
        if 'model_class' not in attrs:
            raise TypeError("Subclasses of PageModel must declare "
                "'model_class' attribute.")
        if 'page_tree' not in attrs:
            raise TypeError("Subclasses of PageModel must declare "
                "'page_tree' attribute.")
        page_tree = attrs['page_tree']
        if not isinstance(page_tree, BaseNode):
            raise TypeError("Invalid type of 'page_tree' attribute.")
        page_tree.validate()
        res = super(PageModelMetaClass, cls).__new__(cls, name, bases, attrs)
        page_tree.fill_thisclass_attr(res)
        return res


class BaseBasePageModel(object):
    pass
