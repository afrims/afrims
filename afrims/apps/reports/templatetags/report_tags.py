from django import template

register = template.Library()


@register.filter
def divide(numerator, denominator):
    "Divide two numbers from the template."
    denominator = denominator or 0.0
    result = 0.0
    if denominator:
        try:
            numerator = float(numerator)
        except ValueError:
            result = 0.0
        else:
            result = numerator / denominator
    return result


@register.filter
def percent(part, total):
    "Return % of part in the total."
    fraction = divide(part, total)
    return fraction * 100
