# -*- coding: utf-8 -*-

"""
    sometest 
    ~~~~~~~~~

    what does this file do.

    :copyright: (c) 2018 by Hong DR.
    :license: BSD, see LICENSE for more details.
"""

class TestAction:
    short_description = 'testAction'

    def __call__(self, modeladmin, request, queryset):
        print('test')
        pass


if __name__ == '__main__':
    test = TestAction()
    test(1, 1, 1)