#include <curses.h>
#include <csignal>
#include <string>

#include <boost/regex/icu.hpp>
#include <unicode/errorcode.h>
#include <unicode/translit.h>
#include <stdio.h>
#ifndef CTRL
#define CTRL(c) ((c) & 037)
#endif
enum Mode {
    Russian,
    Ukrainian,
    Greek,

    LEN
};

icu::Transliterator* converters[3] = {0};

icu::Transliterator* getTransliterator(const char* str) {
    icu::ErrorCode result;
    // using 'Latin; ASCII' instead of 'NFD; [:M:] Remove; NFC' properly
    // converts 'ł' to 'l'. As a bonus, it converts greek and other
    // scripts to latin
    auto r = icu::Transliterator::createInstance(str, UTRANS_FORWARD, result);
    if (result.isFailure())
        throw std::runtime_error(
            "instantiation of transliterator instance failed with "
            + std::string(result.errorName()));
    return r;
}

void updateScreen(int cursor, const std::string& str, std::string& out, Mode mode) {
    const char* modeStr;
    switch (mode) {
    case Mode::Russian:   modeStr = "Russian"; break;
    case Mode::Ukrainian: modeStr = "Ukrainian"; break;
    case Mode::Greek:     modeStr = "Greek"; break;
    default: throw std::runtime_error("invalid mode");
    }

    auto& converter = converters[mode];
    if (converter == nullptr) {
        switch (mode) {
        case Mode::Russian:   converter = getTransliterator("Latin-Russian/BGN"); break;
        case Mode::Ukrainian: converter = converters[Mode::Russian]; break;//getTransliterator("Latin-Ukrainian/BGN"); break;
        case Mode::Greek:     converter = getTransliterator("Latin-Greek"); break;
        case Mode::LEN: break;
        }
    }

    auto us = icu::UnicodeString::fromUTF8(str);
    converter->transliterate(us);
    
    switch (mode) {
    case Mode::Ukrainian:
        us.findAndReplace("г", "ґ");
        us.findAndReplace("Г", "Ґ");
        us.findAndReplace("h", "г");
        us.findAndReplace("H", "Г");
        us.findAndReplace("J", "Й");
        us.findAndReplace("j", "й");
        us.findAndReplace("йи", "ї");
        us.findAndReplace("Йи", "Ї");
        us.findAndReplace("ЙИ", "Ї");
        us.findAndReplace("ыи", "ї");
        us.findAndReplace("Ыи", "Ї");
        us.findAndReplace("ЫИ", "Ї");
        us.findAndReplace("и", "і");
        us.findAndReplace("И", "І");
        us.findAndReplace("ы", "и");
        us.findAndReplace("Ы", "И");
        us.findAndReplace("Й", "И");
        us.findAndReplace("й", "и");
        //us.findAndReplace("е", "є");
        //us.findAndReplace("Е", "Є");
        us.findAndReplace("э", "е");
        us.findAndReplace("Э", "Е");
        us.findAndReplace("ё", "ио");
        us.findAndReplace("Ё", "ИО");
    case Mode::Russian:
        us.findAndReplace("'", "ь");
        us.findAndReplace("\"", "ъ");
        break;
    default: break;
    }
    out = std::string();
    us.toUTF8String(out);

    mvprintw(0, 0, "%s:            ", modeStr);
    mvprintw(1, 0, "%s             ", str.c_str());
    mvprintw(2, 0, "%s             ", out.c_str());
    move(1, cursor);
}

void writeClip(const char* str) {
    FILE* fp = popen(" xsel -i -b", "w");
    if (!fp) {
        perror("popen");
        exit(1);
    }
    //printf("%s\n", str);
    fputs(str, fp);
    pclose(fp);
}


int main() {
    setlocale(LC_ALL, "");
    signal(SIGINT, [](int) { endwin(); exit(0); });

    initscr(); /* initialize the curses library */
    keypad(stdscr, true); /* enable keyboard mapping */
    nonl(); /* tell curses not to do NL->CR/NL on output */
    cbreak(); /* take input chars one at a time, no wait for \n */
    noecho();
    //nodelay(stdscr, true);
    meta(stdscr, true);
    //curs_set(0);
    if (has_colors()) {
        start_color();
    }
    int c = 0;
    int cursor = 0;
    Mode mode = Mode::Russian;
    std::string res;
    std::string out;

    updateScreen(cursor, res, out, mode);
    while ((c = getch())) {
        //endwin();
        //printf("'%c' %d\n", c, c);
        switch (c) {
        case KEY_ENTER:
        case 27: // esc
            endwin();
            return 0;
        case 13: // enter
            endwin();
            writeClip(out.c_str());
            return 0;
        case KEY_UP:
            mode = Mode(mode == 0 ? (Mode::LEN - 1) : (mode - 1));
            break;
        case KEY_DOWN:
            mode = Mode(mode + 1);
            if (mode == Mode::LEN) mode = Mode(0);
            break;
        case KEY_LEFT:
            --cursor;
            if (cursor < 0) cursor = 0;
            break;
        case KEY_RIGHT:
            ++cursor;
            if (cursor >= (int) res.length()) cursor = res.length();
            break;
        case CTRL(KEY_LEFT):
            cursor = 0;
            break;
        case CTRL(KEY_RIGHT):
            cursor = res.length();
            break;

        case KEY_BACKSPACE:
            if (--cursor >= 0)
                res.erase(res.begin() + cursor);
            else cursor = 0;
            break;
        default:
            if (ispunct(c) || isalnum(c) || c==' ') {
                res.insert(res.begin() + cursor++, c);
            }
            break;
        }
        updateScreen(cursor, res, out, mode);
    }
    return 0;
}
