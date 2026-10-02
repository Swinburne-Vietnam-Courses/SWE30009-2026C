def grade(score):
    if score >= 80:
        return "HD"
    elif score >= 70:
        return "D"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "P"
    else:
        return "N"
