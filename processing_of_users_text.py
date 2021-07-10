import pymorphy2


numbers = {'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8,
           'девять': 9, 'десять': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
           'шестнадцать': 16, 'семнадцать': 17, 'восемьнадцать': 18, 'девятнадцать': 19, 'двадцать': 20, 'тридцать': 30, 'сорок': 40,
           'пятьдесят': 50, 'полдень': 12, 'полночь': 0, 'час': 1, '': 1, '': 1, '': 1}



def processing_of_users_text(text):
    morph = pymorphy2.MorphAnalyzer()
    if 'напомни' in text or 'таймер' in text:
        if 'напомни' in text:
            type = 'n'
        else:
            type = 't'
        seconds = 0
        for i in range(len(text) - 1, -1, -1):
            if 'секунд' in text[i] or 'минут' in text[i] or 'час' in text[i]:
                hms = text[i]
        for i in range(1, text.index(hms) + 1):
            if text[i] == 'через' or text[i] == 'о' or text[i] == 'об' or text[i] == 'мне' or text[i] == 'на'\
                    or text[i] == 'таймер':
                continue
            if 'час' in text[i]:
                dop = morph.parse(text[i - 1])[0].normal_form
                if text[i] == 'час':
                    seconds += 3600
                elif dop in numbers:
                    seconds += numbers[dop] * 3600
                else:
                    seconds += int(dop) * 3600
            elif 'минут' in text[i]:
                dop = morph.parse(text[i - 1])[0].normal_form
                if text[i] == 'минуту':
                    seconds += 60
                elif dop in numbers:
                    seconds += numbers[dop] * 60
                else:
                    seconds += int(dop) * 60
            elif 'секунд' in text[i]:
                dop = morph.parse(text[i - 1])[0].normal_form
                if text[i] == 'секунду':
                    seconds += 1
                elif dop in numbers:
                    seconds += numbers[dop]
                else:
                    seconds += int(dop)
        request = ' '.join(text[i+1:])
        return type, [seconds, request]
    elif 'покажи' in text and 'напоминания' in text:
        return 's', []




