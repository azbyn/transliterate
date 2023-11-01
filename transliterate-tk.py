#!/usr/bin/env python3

# TODO profile to make start faster
import unicodedata
import tkinter as tk
import re

import sys

# from tkinter import ttk


# config
_font = ("DejaVu Sans Mono", 12)
_txt_color = "#E0E0E0"
_alpha = 1
_bg = "#1D1F21"
_selected_bg = "#B4B7B4"
_selected_fg = "#1D1F21"


# they're not teeechnically languages, but that's a straight-forward name
languages = [
    ("Russian",     "Latin-Russian/BGN"),
    ("RomCyr",         "Latin"),
    ("Ukrainian",   "Latin-Russian/BGN"),
    # old church slavonic
    # ("OCS",         "Latin-Russian/BGN"),
    ("Glagolitic",  "Latin-Russian/BGN"),

    
    ("Hiragana",    "Latin-Hiragana"),
    ("Katakana",    "Latin-Katakana"),
    ("Latin",       "Russian-Latin/BGN; Greek-Latin/UNGEGN; Latin"),
    ("Greek",       "Latin-Greek/UNGEGN"),
]

languages_dict = { language: code for language, code in languages }

# state
_transliterator = None
_current_language_idx = 0

def change_language(idx):
    from icu import Transliterator

    global _transliterator, _current_language_idx
    _current_language_idx = idx
    l = languages[idx][0]
    _transliterator = Transliterator.createInstance(languages_dict[l])


    # TODO fix update
def greek_pre(string):
    string = (string
              .replace("w", "ω")
              .replace("W", "Ω")
              .replace("ö", "ω")
              .replace("Ö", "Ω")
              .replace("b", "β")
              .replace("B", "Β")
              
              .replace("x", "ξ")
              .replace("X", "Ξ")

              .replace("ę", "η")
              .replace("Ę", "Η")
              
              .replace("q", "ϙ")
              .replace("Q", "Ϙ")

              # digamma
              .replace("Â", "Ϝ")
              .replace("â", "ϝ")

              .replace("Ł", "Ϝ")
              .replace("ł", "ϝ")
              
             )
    return string

def cyrilic_pre(string):
    return string

def ukrainian_pre(string):
    string = cyrilic_pre(string)
    string = (string
             .replace("yi", "ї")
             .replace("ji", "ї")
             .replace("YI", "Ї")
             .replace("JI", "Ї")

             .replace("Yi", "Ї")
             .replace("Ji", "Ї")

             .replace("i", "і")
             .replace("I", "І")

             .replace("î", "и")
             .replace("Î", "И")

             .replace("ye", "є")
             .replace("YE", "Є")
             .replace("Ye", "Є")

             .replace("je", "є")
             .replace("JE", "Є")
             .replace("Je", "Є")
             )
    return string

def ocs_pre(string): #ocs is similar to ukrainian
    string = (string
              .replace("dz", "ꙃ")
              .replace("Dz", "Ꙃ")
              .replace("DZ", "Ꙃ")
              # special dz
              .replace("dż", "ѕ")
              .replace("Dż", "Ѕ")
              .replace("DŻ", "Ѕ")
              .replace("dź", "ѕ")
              .replace("Dź", "Ѕ")
              .replace("DŹ", "Ѕ")

              # ot
              .replace("öt", "ѿ")
              .replace("Öt", "Ѿ")
              .replace("ÖT", "Ѿ")

              .replace("ö", "ѡ")
              .replace("Ö", "Ѡ")

              # ks
              .replace("x", "ѯ")
              .replace("X", "Ѯ")

              # ps
              .replace("ps", "ѱ")
              .replace("Ps", "Ѱ")
              .replace("PS", "Ѱ")

              # th
              .replace("th", "ѳ")
              .replace("Th", "Ѳ")
              .replace("TH", "Ѳ")

              # weird stuff
              .replace("ü", "ѵ")
              .replace("Ü", "Ѵ")

              .replace("q", "ҁ")
              .replace("Q", "Ҁ")

              # romanian stuff
              .replace("Â", "Ꙟ")
              .replace("â", "ꙟ")

              .replace("đż", "џ")
              .replace("đż", "Џ")

              # misc
              .replace("ł", "ў")
              .replace("Ł", "Ў")

              # ae
              .replace("ae", "ѣ")
              .replace("Ae", "Ѣ")
              .replace("AE", "Ѣ")
              .replace("ě", "ѣ")
              .replace("Ě", "Ѣ")

              # ye
             .replace("ye", "ѥ")
             .replace("YE", "Ѥ")
             .replace("Ye", "Ѥ")

             .replace("je", "ѥ")
             .replace("JE", "Ѥ")
             .replace("Je", "Ѥ")

              # nasal stuff
              .replace("ją", "ѭ")
              .replace("Ją", "Ѭ")
              .replace("JĄ", "Ѭ")

              .replace("yą", "ѭ")
              .replace("Yą", "Ѭ")
              .replace("YĄ", "Ѭ")

              .replace("ą", "ѫ")
              .replace("Ą", "Ѫ")

              .replace("yę", "ѩ")
              .replace("Yę", "ѩ")
              .replace("YĘ", "ѩ")

              .replace("ję", "ѩ")
              .replace("Ję", "ѩ")
              .replace("JĘ", "ѩ")

              .replace("ę", "ѧ")
              .replace("Ę", "Ѧ")
              )
    string = ukrainian_pre(string)
    string = (string
              .replace("dz", "ꙃ")
              .replace("Dz", "Ꙃ")
              .replace("DZ", "Ꙃ")
              )
    return string

def russian_pre(string):
    string = cyrilic_pre(string)
    string = (string
              .replace("ö", "ё")
              .replace("ę", "э")
              .replace("Ę", "Э")
              .replace("Ö", "Ё")
              .replace("yo", "ё")
              .replace("Yo", "Ё")
              .replace("YO", "Ё")

              .replace("î", "ы")
              .replace("Î", "Ы")
              )
    return string

def cyrilic_post(string):
    string = (string
        .replace("c", "ц")
        .replace("C", "Ц")

        .replace("ü", "ю")
        .replace("Ü", "Ю")

        .replace("w", "в")
        .replace("W", "В")

        .replace("x", "кс")
        .replace("X", "КС")

        .replace("'", "ь")
        .replace("\"", "ъ")
        .replace("ă", "ъ")
        .replace("Ă", "Ъ")

        .replace("â", "ы")
        .replace("Â", "Ы")
              
        .replace("ż", "ж")
        .replace("ž", "ж")
        .replace("ź", "ж")

        .replace("Ż", "Ж")
        .replace("Ž", "Ж")
        .replace("Ź", "Ж")

        .replace("j", "й")
        .replace("J", "Й")

        .replace("ș", "ш").replace("Ș", "Ш")
        .replace("ś", "ш").replace("Ś", "Ш")
        .replace("š", "щ").replace("Š", "щ")
        .replace("ć", "ч").replace("Ć", "ч")
        .replace("č", "ч").replace("Č", "ч")
        .replace("ț", "ц")
        .replace("Ț", "Ц")
        )
    return string
def russian_post(string):
    string = cyrilic_post(string)
    string = (string
              .replace("h", "х")
              .replace("H", "х")

              .replace("h", "х")
              .replace("H", "х")
              )

    return string

def ukrainian_post(string):
    string = cyrilic_post(string)
    string = (string
              .replace("г", "ґ")
              .replace("Г", "Ґ")

              .replace("э", "е")
              .replace("Э", "Е")

              .replace("Ы", "И")
              .replace("ы", "и")

              .replace("h", "г")
              .replace("H", "Г")
              )

    return string
def ocs_post(string):
    string = (string
              .replace("з", "ꙁ")
              .replace("З", "Ꙁ")
              
              .replace("â", "ꙑ")
              .replace("Â", "Ꙑ")

              .replace("е", "є")
              .replace("е", "Є")
              
              
              # .replace("ż", "з")
              # .replace("Ż", "З")

              .replace("ź", "з")
              .replace("Ź", "З"))
    string = cyrilic_post(string)
    string = (string
              # .replace("є", "ѥ")
              # .replace("Є", "Ѥ")
              
              .replace("э", "є")
              .replace("Э", "Є")
              
              .replace("е", "є")
              .replace("Е", "Є")


              .replace("Ы", "Ꙑ")
              .replace("ы", "ꙑ")

              .replace("đ", "ꙉ")
              .replace("Đ", "Ꙉ")


              # ou
              
              .replace("ō", "ꙋ")
              .replace("Ō", "Ꙋ")

              # ya
              .replace("я", "ꙗ")
              .replace("Я", "Ꙗ")

              # sht
              .replace("шт", "щ")
              .replace("ШТ", "Щ")
              .replace("Шт", "Щ")


              # palatisation
              .replace("ń", "\u0484")
              .replace("Ń", "\u0484")

              # numbers
              .replace("ñ", "\u0483")
              .replace("Ñ", "\u0483")

              # punctiation
              .replace(".", "·")
              .replace(";", "⁙")
              .replace(":", "჻")

              .replace("?", ";")

              )
    return string

def glagoltic_pre(string):
    string = ocs_pre(string)
    return string

def glagoltic_post(string):
    string = ocs_post(string)
    
    string = (string
              .replace("а", "ⰰ")
              .replace("А", "Ⰰ")

              .replace("б", "ⰱ")
              .replace("Б", "Ⰱ")

              .replace("В", "Ⰲ")
              .replace("в", "ⰲ")

              .replace("Г", "Ⰳ")
              .replace("г", "ⰳ")

              .replace("Д", "Ⰴ")
              .replace("д", "ⰴ")
              
              .replace("є", "ⰵ")
              .replace("Є", "Ⰵ")
              
              .replace("Ж", "Ⰶ")
              .replace("ж", "ⰶ")
              
              .replace("Ꙃ", "Ⰷ")
              .replace("ꙃ", "ⰷ")
              
              .replace("Ꙁ", "Ⰸ")
              .replace("ꙁ", "ⰸ")
              
              .replace("І", "Ⰹ")
              .replace("і", "ⰹ")

              .replace("й", "ⰺ")
              .replace("Й", "Ⰺ")
              
              .replace("И", "Ⰻ")
              .replace("и", "ⰻ")
              
              .replace("Ꙉ", "Ⰼ")
              .replace("ꙉ", "ⰼ")
              
              .replace("К", "Ⰽ")
              .replace("к", "ⰽ")

              .replace("Л", "Ⰾ")
              .replace("л", "ⰾ")

              .replace("М", "Ⰿ")
              .replace("м", "ⰿ")
              
              .replace("Н", "Ⱀ")
              .replace("н", "ⱀ")
              
              .replace("О", "Ⱁ")
              .replace("о", "ⱁ")

              .replace("П", "Ⱂ")
              .replace("п", "ⱂ")
              
              .replace("Р", "Ⱃ")
              .replace("р", "ⱃ")
              
              .replace("С", "Ⱄ")
              .replace("с", "ⱄ")
              
              .replace("Т", "Ⱅ")
              .replace("т", "ⱅ")
              
              .replace("У", "Ⱆ")
              .replace("у", "ⱆ")
              
              .replace("Ф", "Ⱇ")
              .replace("ф", "ⱇ")
              
              .replace("х", "ⱈ")
              .replace("Х", "Ⱈ")
              
              .replace("ѡ", "ⱉ")
              .replace("Ѡ", "Ⱉ")
              
              .replace("Щ", "Ⱋ")
              .replace("щ", "ⱋ")
              
              .replace("ц", "ⱌ")
              .replace("Ц", "Ⱌ")
              
              .replace("Ч", "Ⱍ")
              .replace("ч", "ⱍ")
              
              .replace("Ш", "Ⱎ")
              .replace("ш", "ⱎ")
              
              .replace("Ъ", "Ⱏ")
              .replace("ъ", "ⱏ")
              
              .replace("Ꙑ", "ⰟⰊ")
              .replace("ꙑ", "ⱏⰺ")
              
              .replace("Ь", "Ⱐ")
              .replace("ь", "ⱐ")
              
              .replace("Ѣ", "Ⱑ")
              .replace("ѣ", "ⱑ")

              .replace("ꙗ", "ⱑ")
              .replace("Ꙗ", "Ⱑ")
              
              .replace("йо", "ⱖ")
              .replace("Йо", "Ⱖ")
              .replace("ЙО", "Ⱖ")
              
              .replace("ю", "ⱓ")
              .replace("Ю", "Ⱓ")
              
              .replace("ѧ", "ⱔ")
              .replace("Ѧ", "Ⱔ")
              
              .replace("ѩ", "ⱗ")
              .replace("Ѩ", "Ⱗ")
              
              .replace("Ѭ", "Ⱙ")
              .replace("ѭ", "Ⱙ")
              
              .replace("Ⱘ", "Ѫ")
              .replace("ⱘ", "ѫ")
              
              .replace("ѳ", "ⱚ")
              .replace("Ѳ", "Ⱚ")
              
              .replace("ѵ", "ⱛ")
              .replace("Ѵ", "Ⱛ"))
    return string


def to_romanian_cyrillic(string):
    # default_z = "з" #"ꙁ"
    default_z = "ꙁ"
    default_dz = "з"
    # default_dz = "ѕ #"з"
    # default_ps = "пс"
    
    string = (string
              .replace("_", "҇")
              .replace("~+", "҇")

              .replace("o+", "ѻ")
              .replace("O+", "Ѻ")
              
              .replace("%șt", "ⷳ")
              .replace("%th", "ⷴ")
              .replace("%ea", "ⷺ")
              .replace("%iu", "ⷻ")
              .replace("%ia", "ⷼ")
              .replace("%ya", "ⷽ")
              .replace("%â", "ⷾ")
              
              .replace("%b", "ⷠ")
              .replace("%v", "ⷡ")
              .replace("%g", "ⷢ")
              .replace("%d", "ⷣ")
              .replace("%ż", "ⷤ")
              .replace("%z", "ⷥ")
              .replace("%k", "ⷦ")
              .replace("%l", "ⷧ")
              .replace("%m", "ⷨ")
              .replace("%n", "ⷩ")
              .replace("%o", "ⷪ")
              .replace("%p", "ⷫ")
              .replace("%r", "ⷬ")
              .replace("%s", "ⷭ")
              .replace("%t", "ⷮ")
              .replace("%h", "ⷯ")
              .replace("%ț", "ⷰ")
              .replace("%ć", "ⷱ")

              .replace("%ș", "ⷲ")
              .replace("%a", "ⷶ")
              .replace("%e", "ⷷ")
              .replace("%u", "ⷹ")
              .replace("%ü", "ꙷ")
              .replace("%i", "ꙵ")
              .replace("%w", "ꙻ")
              .replace("%ă", "ꙸ")
              .replace("%\\", "ꙺ")
              

              .replace("t+", "ᲄ")
              
              
              
              .replace("ciia\"", "чїѧ")
              .replace("Ciia\"", "Чїѧ")

              .replace("iia\"", "їѧ")
              .replace("Iia\"", "Їѧ")
              
              .replace("cea", "чѣ")
              .replace("Cea", "Чѣ")
              .replace("ce", "че")
              .replace("Ce", "Че")
              .replace("ci", "чи")
              .replace("Ci", "Чи")

              .replace("cj", "чй")
              .replace("Cj", "Чй")

              .replace("chi", "ки")
              .replace("Chi", "Ки")
              
              .replace("chj", "кй")
              .replace("Chj", "Кй")

              .replace("chea", "кѣ")
              .replace("Chea", "Кѣ")

              .replace("che", "ке")
              .replace("Che", "Ке")

              .replace("gea", "џѣ")
              .replace("Gea", "Џѣ")
              .replace("ge", "џе")
              .replace("Ge", "Џе")
              .replace("gi", "џи")
              .replace("Gi", "Џи")

              .replace("ghi", "ги")
              .replace("Ghi", "Ги")

              .replace("ghea", "гѣ")
              .replace("Ghea", "Гѣ")

              .replace("ghe", "ге")
              .replace("Ghe", "Ге")

              .replace("đ", "џ")
              .replace("Đ", "Џ")

              .replace("iu", "ю")
              .replace("Iu", "Ю")

      

              .replace("ie\"", "їе")
              .replace("Ie\"", "Їе")
              
              .replace("ie'", "і́е")
              .replace("Ie'", "І́е")

              .replace("io\"", "їо")
              .replace("Io\"", "Їо")
              
              .replace("ia\"", "їа")
              .replace("Ia\"", "Їа")

              .replace("ii*'", "їи́")
              .replace("Ii*'", "Їи́")

              .replace("ii\"'", "їи́")
              .replace("Ii\"'", "Їи́")
              
              .replace("ii*", "ій")
              .replace("Ii*", "Ій")

              .replace("ij\"", "їй")
              .replace("Ij\"", "Їй")

              .replace("ii\"", "їи")
              .replace("Ii\"", "Їи")

              .replace("ō", "ї")
              .replace("Ō", "Ї")
              )
    string = (string
              # .replace("u<", "оу<")
              # .replace("U<", "Оу<")


              # .replace("ie<", "є<")
              # .replace("Ie<", "Є<")
              
              # .replace("ia<", "ꙗ<")
              # .replace("Ia<", "Ꙗ<")

              .replace("ż", "ж")
              .replace("Ż", "Ж")

              .replace("ź", "ж")
              .replace("Ź", "Ж")
              
              .replace("ia", "ѧ")
              .replace("Ia", "Ѧ")

              .replace("ea", "ѣ")
              .replace("Ea", "Ѣ")

              .replace("ă", "ъ")
              .replace("Ă", "Ъ")

              .replace("ć", "ч")
              .replace("Ć", "Ч")

              .replace("č", "ч")
              .replace("Č", "Ч")
              
              .replace("c", "к")
              .replace("C", "К")
              .replace("k", "к")
              .replace("K", "К")

              .replace("șt", "щ")
              .replace("Șt", "Щ")

              .replace("șț", "щ")
              .replace("Șț", "Щ")

              .replace("în", "ꙟ")
              .replace("În", "Ꙟ")
              .replace("îm", "ꙟ")
              .replace("Îm", "Ꙟ")
              .replace("î", "ꙟ")
              .replace("Î", "Ꙟ")

              .replace("â", "ѫ")
              .replace("Â", "Ѫ")

              .replace("\\", "ь")
              .replace("]", "ь")
              # .replace("Â", "Ь")



              .replace("ș", "ш")
              .replace("Ș", "Ш")

              .replace("ț", "ц")
              .replace("Ț", "Ц")

              .replace("w", "ѡ")
              .replace("W", "Ѡ")

              .replace("th", "ѳ")
              .replace("Th", "Ѳ")

              # .replace("ps", "ѱ")
              # .replace("Ps", "Ѱ")

              .replace("pß", "ѱ")
              .replace("Pß", "Ѱ")

              .replace("dz", default_dz)
              .replace("Dz", default_dz.upper())

              .replace("dz+", "ѕ")
              .replace("Dz+", "Ѕ")

              .replace("ę", "є")
              .replace("Ę", "Є")

              .replace("--", "—")

              

              .replace("x", "ѯ")
              .replace("X", "Ѯ")

              .replace("h", "х")
              .replace("H", "Х")

              .replace("f", "ф")
              .replace("F", "Ф")
              
              .replace("u", "ꙋ")
              .replace("U", "Ꙋ")

              .replace("t", "т")
              .replace("T", "Т")

              .replace("a", "а")
              .replace("A", "А")

              .replace("b", "б")
              .replace("B", "Б")

              .replace("v", "в")
              .replace("V", "В")

              .replace("g", "г")
              .replace("G", "Г")

              .replace("d", "д")
              .replace("D", "Д")

              .replace("e", "е")
              .replace("E", "Е")

              .replace("j", "й")
              .replace("J", "Й")

              .replace("z", default_z)
              .replace("Z", default_z.upper())

              .replace("i", "и")
              .replace("I", "И")

              .replace("y", "і")
              .replace("Y", "І")

              .replace("l", "л")
              .replace("L", "Л")

              .replace("m", "м")
              .replace("M", "М")
              
              .replace("n", "н")
              .replace("N", "Н")

              .replace("o", "о")
              .replace("O", "О")

              .replace("ü", "ѵ")
              .replace("Ü", "Ѵ")

              .replace("p", "п")
              .replace("P", "П")

              .replace("s", "с")
              .replace("S", "С")

              .replace("r", "р")
              .replace("R", "Р")


              .replace("ß", "§")
              )


    string = re.sub(r"(?!\\)'<", "\u0486\u0301", string)
    string = re.sub(r"(?!\\)<'", "\u0486\u0301", string)
    string = re.sub(r"(?!\\)'", "\u0301", string)
    string = re.sub(r"(?!\\)`", "\u0300", string)
    string = re.sub(r"(?!\\)<", "\u0486", string)
    string = re.sub(r'(?!\\)"', "\u0308", string)

    string = re.sub(r'(?!\\)\*', "\u0306", string)
    string = re.sub(r'(?!\\)~', "\u0483", string)
    # string = re.sub(r'(\w)(?!\\)\^', "\\1\u0484", string)
    string = re.sub(r'(?!\\)\^\+', "\uA67D", string) # combining payerok - 7 thing - https://ru.wiktionary.org/wiki/%D0%BF%D0%B0%D0%B5%D1%80%D0%BE%D0%BA - for some replacement of yers
    string = re.sub(r'(?!\\)\^', "\u033e", string)# yerik -z thing  - https://ru.wiktionary.org/wiki/%D0%B5%D1%80%D0%B8%D0%BA

    # kavyka - https://ru.wiktionary.org/wiki/%D0%BA%D0%B0%D0%B2%D1%8B%D0%BA%D0%B0

    # https://unicode-table.com/en/blocks/cyrillic-extended/
    # convert initial variants

    pre = "(?<![\u0306\u0301\u0300\u0483\u0486\u180e])"
    for a, b in [("ие", "є"), ("Ие", "Є"),
                 ("ѧ", "ꙗ"), ("Ѧ", "Ꙗ"),
                 ("ꙋ", "\u180eоу҆"), ("Ꙋ", "\u180eОу҆"),
                 ]:
        string = re.sub(fr'\b{pre}({a})(?!\u180e)', b+"\u0486", string)
        
    # string = re.sub(r'\b(ие)(?!\u180e)', "є", string)
    # string = re.sub(r'\b(И[еЕ])(?!\u0486)', "Є", string)

    # add psili automatically
    # string = re.sub(rf'\b{pre}([аеиіоѡюѣѻАЕИІОѠЮѢѺ])(?!\u0486|\u180e)', "\\1\u0486", string)

    # string = (string
    #           .replace("ꙟ", "ꙟ҆")
    #           .replace("Ꙟ", "Ꙟ҆")
    #           .replace("є҆ꙋ", "є҆́ꙋ")
    #           .replace("Є҆й", "Є҆́й")
    #           )
    
    string = (string
              .replace(r"\'", "'")
              .replace(r'\"', '"')
              .replace(r"\`", "`")
              .replace(r"\<", "<")
              .replace(r"\*", "*")
              .replace(r"\~", "~")
              .replace(r"\^", "^")

              .replace(r"҆҆", "҆")
              )
    # to_romanian_cyrillic end


    string = unicodedata.normalize('NFC', string)
    return string

def latin_pre(string):
    string = (string
              .replace("th", "þ")
              .replace("Th", "Þ")
              .replace("TH", "Þ")
              
              .replace("ae", "æ")
              .replace("Ae", "Æ")
              .replace("AE", "Æ")
              
              .replace("î",  "ï")
              .replace("Î",  "Ï")

              .replace("ă",  "ə")
              .replace("Ă",  "Ə")

              .replace("ę",  "ě")
              .replace("Ę",  "Ě")
              
              .replace("dh", "ð")
              .replace("Dh", "Ð")
              .replace("DH", "Ð")

              .replace("rz", "ř")
              .replace("Rz", "Ř")
              .replace("RZ", "Ř")

              
              )
    return string

def transliterate_string(input):
    lang = languages[_current_language_idx][0]

    if lang == "RomCyr":
        return to_romanian_cyrillic(input).replace("\u180e", "")

    if lang == "Greek":
        input = greek_pre(input)
    elif lang == "Ukrainian":
        input = ukrainian_pre(input)
    elif lang == "OCS":
        input = ocs_pre(input)
    elif lang == "Glagolitic":
        input = glagoltic_pre(input)
    elif lang == "Russian":
        input = russian_pre(input)
    elif lang == "Latin":
        input = latin_pre(input)

    res = _transliterator.transliterate(input)

    if lang == "Russian":
        res = russian_post(res)
    elif lang == "Ukrainian":
        res = ukrainian_post(res)
    elif lang == "OCS":
        # old church slavonic
        res = ocs_post(res)
    elif lang == "Glagolitic":
        res = glagoltic_post(res)

    #no more mongolian vowel separator (for тс) and stuff
    res = res.replace("\u180e", "")
    res = res.replace("_", "")
    return res# s + "-oi"


def on_quit(out_str):
    import clipboard
    if len(out_str) == 0:
        return
    clipboard.copy(out_str)

def main():
    # please don't start the class_name with a capital letter
    class_name = "transliterate"
    # the minimum amount of code to make this work from awesomewm
    if len(sys.argv) >= 3 and sys.argv[1] == "-name":
        class_name = sys.argv[2]

    # with open("/home/azbyn/dbg.txt", 'w')as f:
        # print(sys.argv, file=f)



    root = tk.Tk(className=class_name)
    root.wm_protocol("WM_CLASS", class_name)
    root.title("Transliterate")
    root.geometry("700x120")


    if _alpha < 1:

        root.wait_visibility(root)
        root.wm_attributes("-alpha", _alpha)


    in_var = tk.StringVar()
    out_var = tk.StringVar()


    def callback(*args):
        value = in_var.get()
        out_var.set(transliterate_string(value))

    def enter(*args):
        out_str = transliterate_string(in_var.get())
        # lang = languages[_current_language_idx][0]
        # if lang == "RomCyr" and "@" in out_str:
        #     out_str = ("%"+in_var.get() +"\n" +out_str+"\linebreak").replace("@", "")
        on_quit(out_str)
        root.quit()

    def on_change_language(idx):
        if idx < 0:
            idx = len(languages) - 1
        elif idx >= len(languages):
            idx = 0

        for _, b in buttons.items():
            b.state = tk.NORMAL
            b["bg"] = _bg
            b["fg"] = _txt_color

        b = buttons[idx]
        b.state = tk.DISABLED
        b["bg"] = _selected_bg
        b["fg"] = _selected_fg

        change_language(idx)
        callback()

    in_var.trace_add("write", callback)


    frame = tk.Frame(root)
    frame.pack(fill=tk.X, expand=True)

    buttons = {}
    i = 0
    for l,_ in languages:
        def m(n):
            return lambda: on_change_language(n)
        btn = tk.Button(frame, text=l,
                        command=m(l))

        btn.grid(row=0, column=i, sticky="nesw")
        frame.grid_columnconfigure(i, weight=1, uniform="column")
        buttons[i] = btn
        i += 1

    txt = tk.Entry(root, textvariable=in_var, font=_font, #bg=_bg,
                   insertbackground=_txt_color, fg=_txt_color)


    txt.pack(fill=tk.X, expand=True)
    txt.focus()

    output = tk.Label(root, textvariable=out_var, font=_font,
                      fg=_txt_color, anchor="w")

    output.pack(fill=tk.X, expand=True)


    txt.bind('<Return>',enter)
    txt.bind('<Up>',   lambda *_: on_change_language(_current_language_idx+1))
    txt.bind('<Down>', lambda *_: on_change_language(_current_language_idx-1))

    on_change_language(_current_language_idx)

    root.mainloop()


if __name__ == "__main__":
    main()

# import cProfile
