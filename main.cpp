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

using icu::Transliterator;
using icu::UnicodeString;

struct ModeData {
    std::string name;
private:
    const char* transliteratorID;
    Transliterator* converter;
public:
    ModeData(std::string name, const char* transliteratorID):
        name(name), transliteratorID(transliteratorID), converter(nullptr) {}

    Transliterator* getConverter() {
        if (converter == nullptr) {
            icu::ErrorCode result;
            converter = Transliterator::createInstance(transliteratorID, UTRANS_FORWARD, result);
            if (result.isFailure())
                throw std::runtime_error(
                    "instantiation of transliterator instance failed with "
                    + std::string(result.errorName()));
        }
        return converter;
    }
};

enum Mode {
    Russian,
    Ukrainian,
    Greek,
    GreekUNGEGN,
    Latin,

    LEN
};
ModeData modeDatas[Mode::LEN] = {
    { "Russian",     "Latin-Russian/BGN" },
    { "Ukrainian",   "Latin-Russian/BGN" },
    { "Greek",       "Latin-Greek" },
    { "Greek UNGEGN", "Latin-Greek/UNGEGN" },
    { "Latin",       "Russian-Latin/BGN; Greek-Latin/UNGEGN; Latin" },
};

constexpr int modeStrLength = 18;

void drawTopBar(Mode mode) {
    //attron(COLOR_PAIR(2));
    //vline(' ', modeStrLength* Mode::LEN);
    for (int i = 0; i < Mode::LEN; ++i) {
        auto& s = modeDatas[i].name;
        int left = (modeStrLength+ s.size())/2 - 2;//; + s.size();
        attron(COLOR_PAIR(1));
        mvprintw(0, i * modeStrLength, "|");
        attron(COLOR_PAIR(1 + (i == mode)));
        printw(" %d %*s", i+1, left, s.c_str());
        int right = modeStrLength - left-3;
        hline(' ', right);
    }
    attron(COLOR_PAIR(1));
    int x = Mode::LEN * modeStrLength;
    mvprintw(0, x, "|");
    mvprintw(1, 0, "|");
    mvprintw(1, x, "|");
    mvhline(1, 1, '-', x-1);
}

void updateScreen(int cursor, const UnicodeString& str, std::string& out, Mode mode) {
    drawTopBar(mode);

    UnicodeString us = str;//.copy();// icu::UnicodeString::fromUTF8(str);

    switch (mode) {
    case Mode::Greek:
    case Mode::GreekUNGEGN:
        us.findAndReplace("w", "ω");
        us.findAndReplace("W", "Ω");
        break;
    case Mode::Ukrainian:
    case Mode::Russian:
        //us.findAndReplace("c", "ц");
        //us.findAndReplace("C", "Ц");
        break;
    default: break;
    }
    modeDatas[mode].getConverter()->transliterate(us);

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
        goto fall;
    case Mode::Russian:
        fall:
        us.findAndReplace("'", "ь");
        us.findAndReplace("\"", "ъ");
        us.findAndReplace("ż", "ж");
        us.findAndReplace("ž", "ж");

        us.findAndReplace("Ż", "Ж");
        us.findAndReplace("Ž", "Ж");
        us.findAndReplace("ș", "ш"); us.findAndReplace("Ș", "Ш");
        us.findAndReplace("ś", "ш"); us.findAndReplace("Ś", "Ш");
        us.findAndReplace("š", "щ"); us.findAndReplace("Š", "щ");
        us.findAndReplace("ć", "ч"); us.findAndReplace("Ć", "ч");
        us.findAndReplace("č", "ч"); us.findAndReplace("Č", "ч");
        us.findAndReplace("c", "к");
        us.findAndReplace("C", "К");


        us.findAndReplace("ö", "ё");
        us.findAndReplace("Ö", "Ё");
        us.findAndReplace("yo", "ё");
        us.findAndReplace("Yo", "Ё");
        us.findAndReplace("YO", "Ё");
        if (mode == Mode::Russian) {
            // us.findAndReplace("H", "Х");
            // us.findAndReplace("Kh", "Х");
            // us.findAndReplace("KH", "Х");
            us.findAndReplace("h", "х");
            us.findAndReplace("kh", "х");
        }
        break;
    default: break;
    }
    out = std::string();
    auto tmp = std::string();
    str.toUTF8String(tmp);
    us.toUTF8String(out);

    //mvprintw(0, 0, "%s:            ", modeStr);
    mvprintw(2, 0, "%s             ", tmp.c_str());
    mvprintw(3, 0, "%s             ", out.c_str());
    move(2, cursor);
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
UnicodeString readClip() {
    FILE* fp = popen("xsel --clipboard", "r");
    if (!fp) {
        perror("popen");
        exit(1);
    }
    char s[1024];
    fgets(s, sizeof(s) / sizeof(char), fp);
    auto r = UnicodeString::fromUTF8(s);
    pclose(fp);
    return r;
}

void initColor() {
    if (!has_colors()) return;
    start_color();
    int bg_col = (use_default_colors() == OK) ? -1: COLOR_BLACK;
    init_pair(2, COLOR_BLACK, COLOR_WHITE);
    init_pair(1, COLOR_WHITE, bg_col);
}
int main(int argc, char* /*argv*/[]) {
    Mode mode = Mode::Russian;
    icu::UnicodeString res;// = icu::UnicodeString::fromUTF8(s);
    std::string out;
    int cursor = res.length();
    atexit([] { endwin(); });

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
    initColor();
    bool debugMode = argc >= 2;

    updateScreen(cursor, res, out, mode);
    int c = 0;
    bool escape = false;
    int i = 4;

    //TODO proper unicode <- and -> and delete

    //not fully implemented with all safety guards, but it works
    // auto getch_utf8 = [] () -> char32_t {
    //     //for the other bytes
    //     auto readExtra = [] { return getch() & 0b0011'1111; };
    //     unsigned c = getch();
    //     if (c & 0x80) {
    //         if ((c & 0b1110'0000) == 0b1100'0000) { //110x'xxxx - 2 bytes
    //             auto b1 = c & 0b0001'1111;
    //             auto b2 = readExtra();
    //             return (b1 << 6) | b2;
    //         } else if ((c & 0b1111'0000) == 0b1110'0000) { //1110'xxxx - 3 bytes
    //             auto b1 = c & 0b0000'1111;
    //             auto b2 = readExtra();
    //             auto b3 = readExtra();
    //             return (b1 << 6*2) | (b2 << 6) | b3;
    //         } else if ((c & 0b1111'1000) == 0b1111'0000) { //1111'0xxx - 4 bytes
    //             auto b1 = c & 0b0000'0111;
    //             auto b2 = readExtra();
    //             auto b3 = readExtra();
    //             auto b4 = readExtra();
    //             return (b1 << 6*3) | (b2 << 6*2) | (b3 <<6) | b4;
    //         }
    //     }
    //     return c;
    // };
    while ((c = getch())) {
        if (escape) {
            if (c >= '1' && c <= '1' + Mode::LEN) {
                mode = Mode(c- '1');
            }
            escape = false;
            updateScreen(cursor, res, out, mode);
            continue;
        }
        //endwin();
        if (debugMode) {
            printf("inserting '%c' %d\n", c, c);
            mvprintw(i++, 0, "'%c' %d\n", c, c);
        }
        switch (c) {
        case 27: // esc
            escape = true;
            continue;
        case KEY_ENTER:
        case 13: // enter
            endwin();
            if (out.size()) writeClip(out.c_str());
            return 0;
        case KEY_DOWN:
            mode = Mode(mode == 0 ? (Mode::LEN - 1) : (mode - 1));
            break;
        case KEY_UP:
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
        case CTRL('v'): {
            auto tmp = readClip();
            res.insert(cursor, tmp);
            cursor += tmp.length();
        } break;
        case CTRL(KEY_RIGHT):
            cursor = res.length();
            break;

        case KEY_BACKSPACE:
            if (--cursor >= 0)
                res.remove(cursor, 1);
                //res.erase(res.begin() + cursor);
            else cursor = 0;
            break;
        case 410: break;
        default: {
            char32_t chr = c;
            auto readExtra = [] { return getch() & 0b0011'1111; };
            // c = getch();
            if (c & 0x80) {
                if ((c & 0b1110'0000) == 0b1100'0000) { //110x'xxxx - 2 bytes
                    auto b1 = c & 0b0001'1111;
                    auto b2 = readExtra();
                    chr = (b1 << 6) | b2;
                } else if ((c & 0b1111'0000) == 0b1110'0000) { //1110'xxxx - 3 bytes
                    auto b1 = c & 0b0000'1111;
                    auto b2 = readExtra();
                    auto b3 = readExtra();
                    chr = (b1 << 6*2) | (b2 << 6) | b3;
                } else if ((c & 0b1111'1000) == 0b1111'0000) { //1111'0xxx - 4 bytes
                    auto b1 = c & 0b0000'0111;
                    auto b2 = readExtra();
                    auto b3 = readExtra();
                    auto b4 = readExtra();
                    chr = (b1 << 6*3) | (b2 << 6*2) | (b3 <<6) | b4;
                }
            }
            //printf("--'%x'--\n", chr);
            c = chr;
            if (c >= 0x20){ //ispunct(c) || isalnum(c) || c==' ') {
            // if (ispunct(c) || isalnum(c) || c==' ') {
                //res.insert(res.begin() + cursor++, c);
                // printf("+\n");
                res.insert(cursor++, c);
            } else continue;
        } break;
        }
        updateScreen(cursor, res, out, mode);
    }
    return 0;
}
