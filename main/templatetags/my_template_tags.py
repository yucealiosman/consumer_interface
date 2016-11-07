# -*- coding: utf-8 -*-
from django import template

register = template.Library()


def division(price):
    return round(float(price) / 4, 2)

register.filter('division', division)


# @register.simple_tag()
# def multiply(price):
#     temp =  float(price) / 4
#     return round(temp,2)
