date = r"^(0?[1-9]|1[0-2])([/|\-|\s|月|]?)((0?[1-9])|((1|2)[0-9])|30|31)([日|號]?)\s[\+|\-][1-9]$"
week = r"^[這|本|下](下?)[週|周]\s[\+|\-][1-9]$"
quick = r"^[\+|\-][1-9]$"

convert_date = r"^(0?[1-9]|1[0-2])([/|\-|\s|月|]?)((0?[1-9])|((1|2)[0-9])|30|31)([日|號]?)$"
convert_week = r"^[這|本|下](下?)[週|周]$"

month_zero = r"^([1-9])(.?)((0?[1-9])|((1|2)[0-9])|30|31)(.?)$"
day_zero = r"^(0?[1-9]|1[0-2])(.?)([1-9])(.?)$"