from datetime import date, datetime

def getDayDelta(button, referenceDate):
    text = button.get_attribute("innerText")
    """
    DAY OF THE WEEK
    DAY
    MONTH
    """
    _, day, month = text.split()
    day = int(day)
    month = datetime.strptime(month, "%b").month

    return abs(date(referenceDate.year, month, day) - referenceDate)