from django import template

register = template.Library()

def customsort(value, arg):
    if arg == 'subscribers':
        return sorted(value, key=lambda x: -len(x.subscribers.all()))


register.filter('customsort', customsort)
