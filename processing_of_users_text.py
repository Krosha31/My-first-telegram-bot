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
        time = {'Y':0, 'M':0, 'D':0, 'h':0, 'm':0, 's':0, }
        for i in range(len(text) - 1, -1, -1):
            if 'секунд' in text[i] or 'минут' in text[i] or 'час' in text[i]:
                hms = text[i]
                break
        for i in range(1, text.index(hms) + 1):
            if text[i] == 'через' or text[i] == 'о' or text[i] == 'об' or text[i] == 'мне' or text[i] == 'на'\
                    or text[i] == 'таймер':
                continue
            if 'час' in text[i]:
                dop = morph.parse(text[i - 1])[0].normal_form
                if text[i] == 'час' and dop not in numbers and not (set(dop) & set('0123456789')):
                    time['h'] += 1
                elif dop in numbers:
                    time['h'] += numbers[dop]
                else:
                    time['h'] += int(dop)
            elif 'минут' in text[i]:
                dop = morph.parse(text[i - 1])[0].normal_form
                if text[i] == 'минуту' and dop not in numbers and not (set(dop) & set('0123456789')):
                    time['m'] += 1
                elif dop in numbers:
                    time['m'] += numbers[dop]
                else:
                    time['m'] += int(dop)
            elif 'секунд' in text[i]:
                print(text[i-1])
                dop = morph.parse(text[i - 1])[0].normal_form
                if text[i] == 'секунду' and dop not in numbers and not (set(dop) & set('0123456789')):
                    time['s'] += 1
                elif dop in numbers:
                    time['s'] += numbers[dop]
                else:
                    time['s'] += int(dop)
        request = ' '.join(text[i+1:])
        return type, [time, request]
    elif 'покажи' in text and 'напоминания' in text or 'показать' in text and 'напоминания' in text:
        return 's', []
    elif 'удали' in text and ('напоминания' in text or 'напоминание' in text) or 'удалить' in text and ('напоминания' in text or 'напоминание' in text):
        return 'd', []



