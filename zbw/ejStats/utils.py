import locale

def format_number(number):
    """method for getting thousands separator on results
    """
    locale.setlocale(locale.LC_NUMERIC, 'de_DE.UTF-8')
    if type(number) == str:
        result = int(number.replace('.', ''))
    if type(number) == int:
        result = locale.format("%d", number, True)
    
    return result


