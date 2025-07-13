from django import template
register = template.Library()
@register.filter
def space_thousands(value):
    try:
        value = float(str(value).replace(",", "."))
        int_part = int(value)
        frac_part = abs(value - int_part)
        if frac_part > 0:
            parts = f"{value:,.2f}".replace(",", " ").split(".")
            return parts[0] + "." + parts[1]
        else:
            return f"{int_part:,}".replace(",", " ")
    except (ValueError, TypeError):
        return value