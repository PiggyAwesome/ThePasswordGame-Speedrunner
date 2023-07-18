import json
import random
import re
import string
import time
from datetime import datetime
from threading import Thread

import pylunar
import requests
from geopy.geocoders import Nominatim
from playwright.sync_api import (BrowserContext, ElementHandle, Page,
                                 sync_playwright)
from stockfish import Stockfish

geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0")

engine = Stockfish(path="stockfish.exe", depth=15)




class File:
    def __init__(self, positions) -> None:
        self.positions = positions
    def __str__(self) -> str:
        return self.positions
    def __getitem__(self, index) -> list:
        return self.positions.split(" ")[index]

class Rank:
    def __init__(self, positions) -> None:
        self.positions = positions
    def __str__(self) -> str:
        return self.positions
    def __getitem__(self, index) -> list:
        return self.positions.split(" ")[index]


class ChessBoard:
    def __init__(self, board:str, player:str):
        self.player = "w" if "white" in player.lower() else "b"
        self.can_castle = "-"
        self.en_passant = "-"

        self.board = board.splitlines()
        
        self.rank_8 = Rank(self.board[0])
        self.rank_7 = Rank(self.board[1])
        self.rank_6 = Rank(self.board[2])
        self.rank_5 = Rank(self.board[3])
        self.rank_4 = Rank(self.board[4])
        self.rank_3 = Rank(self.board[5])
        self.rank_2 = Rank(self.board[6])
        self.rank_1 = Rank(self.board[7])


        self.a_file = self.Rank_to_File(0)
        self.b_file = self.Rank_to_File(1)
        self.c_file = self.Rank_to_File(2)
        self.d_file = self.Rank_to_File(3)
        self.e_file = self.Rank_to_File(4)
        self.f_file = self.Rank_to_File(5)
        self.g_file = self.Rank_to_File(6)
        self.h_file = self.Rank_to_File(7)


    def gen_fen(self):
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        old_ranks = [self.rank_1, self.rank_2, self.rank_3, self.rank_4, self.rank_5, self.rank_6, self.rank_7, self.rank_8]
        new_ranks = []

        for rank in old_ranks:
            rank = list(rank)
            result = "".join(rank)

            open_spaces = re.findall(r"\.+", "".join(rank))
    
            for match in open_spaces:
                result = result.replace(match, str(len(match)), 1)

            new_ranks.append(result)
            
            
        fen = f"{new_ranks[7]}/{new_ranks[6]}/{new_ranks[5]}/{new_ranks[4]}/{new_ranks[3]}/{new_ranks[2]}/{new_ranks[1]}/{new_ranks[0]} {self.player} {self.can_castle} {self.en_passant} 0 1" 
        return fen

    def Rank_to_File(self, index):
        return File(f"{self.rank_1[index]} {self.rank_2[index]} {self.rank_3[index]} {self.rank_4[index]} {self.rank_5[index]} {self.rank_6[index]} {self.rank_7[index]} {self.rank_8[index]}")




class Password:
    def __init__(self, page:Page) -> None:
        self.password = ""
        self.password_rich = ""
        self.page = page
        self.moon_phase = self.getMoonPhase() # Do these first to save time
        self.wordle = self.getWordle()        #
        self.moon_phase = self.getMoonPhase() #
    class Selectors:
        password_field = "#__layout > div > div > div.password-wrapper > div.password-box > div.password-box-inner > div:nth-child(2) > div"
        captcha_img = "#__layout > div > div > div.password-wrapper > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.captcha-wrapper > img.captcha-img"
        new_captcha_btn = "#__layout > div > div > div.password-wrapper > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.captcha-wrapper > img.captcha-refresh"
        maps_iframe = "#__layout > div > div > div.password-wrapper > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div > iframe"
        chess_img = "#__layout > div > div > div.password-wrapper > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.chess-wrapper > img"
        chess_turn_2_play = "#__layout > div > div > div.password-wrapper > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.chess-wrapper > div.move"
        rule24 = '//*[@id="__layout"]/div/div/div[2]/div[5]/div/div[1]/div/div/div/div[1]'
        sacrifice_letters = "#__layout > div > div > div.password-wrapper.has-toolbar > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.sacrafice-area > div > "
        confirm_sacrifice = "#__layout > div > div > div.password-wrapper.has-toolbar > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.sacrafice-area > button"
        colour = "#__layout > div > div > div.password-wrapper.has-toolbar > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.rand-color"
        new_colour_btn = "#__layout > div > div > div.password-wrapper.has-toolbar > div:nth-child(5) > div > div:nth-child(1) > div > div > div > div.rand-color > img"#'//*[@id="__layout"]/div/div/div[2]/div[5]/div/div[2]/div/div/div/div[2]/img'
        pass_len_counter = "#__layout > div > div > div.password-wrapper.has-toolbar > div.password-box > div.password-box-inner > div.password-length.show-password-length"
    def getCharacters(self, k=5):
        result = "".join(random.choices(string.ascii_lowercase.strip("aeiou"), k=k))
        return result

    def getNumber(self, k=1):
        "Your password must include a number."
        result = "0"*k
        return result

    def getUppercaseLetter(self, k=1):
        "Your password must include an uppercase letter."
        result = "L"*k
        return result

    def getPunctuation(self, k=1):
        "Your password must include a special character."
        result = "!"*k
        return result

    def getDigits(self, passw=None, Exit=True):
        "The digits in your password must add up to 25."
        passw = self.password if passw == None else passw

        add_up_to = 25
        for character in passw:
            if character.isdigit():
                add_up_to -= int(character)

        if add_up_to < 0:
            if Exit == True:
                input("Yikes! You got unlucky with the digits, retry needed")
                exit()
            else:
                return False
        


        quotient = add_up_to // 9
        remainder = add_up_to % 9

        result = ("9" * quotient) + str(remainder)
        return result

    def getMonth(self):
        "Your password must include a month of the year."
        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        result = random.choice(months)
        return result

    def getRomanNumeral(self, k=1):
        "Your password must include a roman numeral."
        result = "I"*k
        return result

    def getSponsor(self):
        "Your password must include one of our sponsors."
        result = random.choice(["shell", "starbucks", "pepsi"])
        return result


    def getRomanNumeral35(self):
        "The roman numerals in your password should multiply to 35."
        result = "XXXV"
        return result


    def solveCaptcha(self):
        "Your password must include this CAPTCHA"
        retry = True
        while retry:
            self.page.get_by_text('Rule 10')
            captcha = self.page.query_selector(self.Selectors.captcha_img)
            captcha_img = captcha.get_attribute("src")
            result = captcha_img.split("/")[-1].replace(".png", "")

            add_up_to = 0
            for character in result:
                if character.isdigit():
                    add_up_to += int(character)

            if add_up_to > 0:
                captcha_btn = self.page.query_selector(self.Selectors.new_captcha_btn)
                captcha_btn.click()
                continue
            else:
                retry = False

        return result


    def getWordle(self):
        "Your password must include today's Wordle answer."
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day

        resp = requests.get(f"https://neal.fun/api/password-game/wordle?date={year}-{month:02}-{day:02}")
        result = resp.json()["answer"]
        return result


    def get2LetterElement(self):
        "Your password must include a two letter symbol from the periodic table."
        result = "Ga"
        return result

    def getMoonPhase(self):
        "Your password must include the current phase of the moon as an emoji."
        # Had to disable this, because thepasswordgame is not accurate to user's country.
        # location = requests.get("http://ipinfo.io/loc").text
        location = "37.0902,95.7129"
        lat, lon = location.split(",")
        lat1, lat2_3 = f"{lat}0000".split(".")
        lat2, lat3 = lat2_3[:2], lat2_3[2:4]

        lon1, lon2_3 = f"{lon}0000".split(".")
        lon2, lon3 = lon2_3[:2], lon2_3[2:4]

        latitude = (lat1, lat2, lat3)
        longitude = (lon1, lon2, lon3)

        mi = pylunar.MoonInfo(latitude=latitude, longitude=longitude)

        match mi.phase_name():
            case "NEW_MOON":
                result = "🌑"
            case "WAXING_CRESCENT":
                result = "🌒"
            case "FIRST_QUARTER":
                result = "🌓"
            case "WAXING_GIBBOUS":
                result = "🌔"
            case "FULL_MOON":
                result = "🌕"
            case "WANING_GIBBOUS":
                result = "🌖"
            case "LAST_QUARTER":
                result = "🌗"
            case "WANING_CRESCENT":
                result = "🌘"

        return result


    def findCountryName(self):
        "Your password must include the name of this country."

        element = self.page.query_selector(self.Selectors.maps_iframe)
        link = element.get_attribute("src")
        cords = link.split("1d")[-1].split("!3f")[0]

        Latitude, Longitude = cords.split("!2d")
        
        location = geolocator.reverse(Latitude + "," + Longitude, language="en")
        result = location.raw['address'].get("country").lower() 
        
        return result


    def getLeapYear(self):
        "Your password must include a leap year."
        return "0"


    def solveChessPuzzle(self):
        "Your password must include the best move in algebraic chess notation."
        
        element = self.page.query_selector(self.Selectors.chess_img)
        link = element.get_attribute("src")

        player_element = self.page.query_selector(self.Selectors.chess_turn_2_play)
        player = player_element.text_content()

        svg = requests.get("https://neal.fun" + link)

        svg_data = svg.text

        chess_position = svg_data.split("<pre>")[1].split("</pre>")[0]         

        board = ChessBoard(chess_position, player)

        fen = board.gen_fen()
        engine.set_fen_position(fen)

        best_move = engine.get_best_move()
        piece = engine.get_what_is_on_square(best_move[:2])

        is_capture = "" if engine.will_move_be_a_capture(best_move).value == "no capture" else "x"

        is_check = "" if engine.is_move_correct(piece.value + is_capture + best_move[2:] + "") else "+"

        result = piece.value.upper() + is_capture + best_move[2:] + is_check

        return result


    def getPaul(self):
        "🥚 ← This is my chicken Paul. He hasn't hatched yet, please put him in your password and keep him safe."
        result = "🥚"
        return result

    def calculateElements(self, password:str, add_up_to=200):
        "The elements in your password must have atomic numbers that add up to 200."
        
        with open("assets/element_to_number.json", 'rb') as file:
            elmnt2nmbr = json.loads(file.read())
            
        periodic_table = sorted(elmnt2nmbr.keys(), key=len, reverse=True)

        # print(password)

        elementsAlreadyInPassword = {}
        og_pass = password

        for element in periodic_table:
            if element in password:                     # count
                elementsAlreadyInPassword[element] = {"occurences": password.count(element), "number_total": 0}
                password = password.replace(element, "")



        current_value = 0
        
        for found_element in elementsAlreadyInPassword:
            number = elmnt2nmbr.get(found_element)
            elementsAlreadyInPassword[found_element]["number_total"] = number*elementsAlreadyInPassword[found_element]["occurences"]
            try:
                current_value += number*elementsAlreadyInPassword[found_element]["occurences"]
            except TypeError:
                # print(number, found_element)
                raise TypeError("Idk why this happened, but I dont want to find out")
        
        print(f"Found these elements in your password: {elementsAlreadyInPassword} = {current_value}")
        needed_value = add_up_to - current_value
        print(f"Needed value: {needed_value}")


        with open("assets/number_to_element.json", 'rb') as file:
            nmbr2elmnt = json.loads(file.read())

    
        def get_element_by_nr(required_value):
            if nmbr2elmnt.get(str(required_value)) != None:
                return nmbr2elmnt.get(str(required_value))
            else:
                return ""
        

        if needed_value < 0:
            self.page.query_selector(self.Selectors.password_field).evaluate(f"node => node.innerHTML = '{og_pass}'"); 
            input("Yikes! You got unlucky with the elements, the atomic numbers in your password are too big. Retry is needed.\nTIP: If you want this error to occur less frequently for everyone, you can help by finding YouTube videos without periodic table elements in their links, and then making an issue, or pull request with the links updated in assets/youtube_links.json. This will help grow the database, and lower the chances of failing the challenge.")
            exit() 

        elementsToAddToPassword = {}
        if needed_value > 100:
            element_1 = get_element_by_nr(100)
            element_2 = get_element_by_nr(needed_value - 100)
            elementsToAddToPassword[element_1] = 100
            elementsToAddToPassword[element_2] = needed_value - 100
        else:
            element = get_element_by_nr(needed_value)
            elementsToAddToPassword[element] = needed_value

        result = "".join(elementsToAddToPassword)

        print(f"Needed elements: {elementsToAddToPassword}")

        return result


    def makeStrong(self):
        "Your password is not strong enough 🏋️‍♂️"

        def stronger_maker():
            return "🏋️‍♂️"
        
        result = stronger_maker() * 3
        return result


    def getAffirmation(self):
        "Your password must contain one of the following affirmations:"
# NGH
# DVL
        result = "iamloved"#random.choice(["iamloved", "iamenough"])
        return result


    def feedPaul(self):
        "Paul has hatched! Please don't forget to feed him, he eats three 🐛 every minute."
        result = "🐛"
        return result
    
    def evolvePaul(self):
        result = "🐔"
        return result


    def boldVowels(self, password:str):
        "All the vowels in your password must be bolded."
        vowels = ["a", "e", "i", "o", "u", "y", "A", "E", "I", "O", "U", "Y"]

        new_password = password
        for vowel in vowels:
            new_password = self.safeReplace(new_password, vowel, f"<strong>{vowel}</strong>")
        self.password_rich = new_password
        return new_password

    def getYouTubeVideo(self):
        "Your password must include the URL of a xx minute yy second long YouTube video."

        self.page.wait_for_selector("#__layout > div > div > div.password-wrapper.has-toolbar > div:nth-child(5) > div > div:nth-child(24)")
        vid_len_selector = self.page.query_selector(self.Selectors.rule24)
        vid_len_text = vid_len_selector.inner_text()

        for x in string.ascii_letters + string.punctuation: vid_len_text = vid_len_text.replace(x, "")

        vid_len = []
        for character in vid_len_text.split(" "): vid_len.append(character) if character != "" else None

        vid_mins, vid_secs = vid_len

        '''
        # I decided against finishing the real-time scraper 

        page2, page3, page4, page5 = context.new_page(), context.new_page(), context.new_page(), context.new_page()

        # Playwright is not threadsafe 😩
        search_vid_mins_rounded = (int(vid_secs) + 30) // 60 + int(vid_mins)
        page2.goto(f'https://www.youtube.com/results?search_query={vid_mins} minutes')
        page3.goto(f'https://www.youtube.com/results?search_query={search_vid_mins_rounded if search_vid_mins_rounded != vid_mins else "in " + vid_mins} minutes')
        page4.goto(f'https://www.youtube.com/results?search_query={vid_mins} minute timer')
        page5.goto(f'https://www.youtube.com/results?search_query=for {vid_mins} minutes straight!')


        links = []

        script = "const videoItems = document.querySelectorAll('ytd-video-renderer');const links = Array.from(videoItems).filter(videoItem => {const durationElement = videoItem.querySelector('span.style-scope.ytd-thumbnail-overlay-time-status-renderer'); const duration = durationElement ? durationElement.innerText : 'N/A'; const linkElement = videoItem.querySelector('a#thumbnail'); const link = linkElement ? linkElement.href : ''; return \"""" + f"{int(vid_mins)}:{int(vid_secs):02}" + """\" === duration;}).map(videoItem => {const linkElement = videoItem.querySelector('a#thumbnail'); return linkElement ? linkElement.href : '';}); links;" 
        print(script)

        def scroller(page: Page, loops=25):
            for i in range(loops):
                page.mouse.wheel(0, 10000)
                time.sleep(0.5)

        page_list = [page1, page2, page3, page4, page5]
        links = []

        for page in page_list:
            scroller(page, 25)
            this_page_link = page.evaluate(script)
            links += this_page_link
            password_span_selector.evaluate(f"node => node.innerHTML = '{password_span_selector.inner_html() + self.rule23() if password_span_selector.inner_html().count(self.rule23()) < 5 else password_span_selector.inner_html()}'")

            if links != []:
                break
        '''

        with open("assets/youtube_links.json", 'r') as file:
            videos = json.loads(file.read())

        link = "youtu.be/" + videos.get(f"{int(vid_mins)}:{int(vid_secs):02}")

        return link


    def sacrificeLetters(self):
        "A sacrifice must be made. Pick 2 letters that you will no longer be able to use."
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for character in self.password.upper():
            if character in letters:
                letters = letters.replace(character, "")

        letters_to_remove = list(letters)[:2]

        
        if len(letters_to_remove) < 2:
            if self.affirmation != "iamenough":
                self.password = self.password.replace(self.affirmation, "iamenough")
                self.affirmation = "iamenough"
                return self.sacrificeLetters()
            else:
                input("Yikes! You got unlucky with the letter sacrificing, all letters are used. Retry is needed")
                exit()


        for letter in letters_to_remove:
            letter_number = string.ascii_uppercase.find(letter) + 1
            letter_button = self.page.wait_for_selector(self.Selectors.sacrifice_letters + f"button:nth-child({letter_number})")
            letter_button.click()

        sacrifice_button = self.page.wait_for_selector(self.Selectors.confirm_sacrifice)
        sacrifice_button.click()
        print("Sacrificed:", letters_to_remove)

        return letters_to_remove


    def get_part_1(self):
        self.month = self.getMonth()
        self.sponsor = self.getSponsor()
        self.roman_numerals = self.getRomanNumeral35()
        self.leap_year = self.getLeapYear()
        self.two_letter_element = self.get2LetterElement()
        self.punctuation = self.getPunctuation()

        self.password = self.leap_year + self.two_letter_element + self.roman_numerals + self.sponsor + self.month + self.punctuation
        return self.password

    def get_part_2(self):
        self.digits = self.getDigits()
        self.password = self.leap_year + self.two_letter_element + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits 
        return self.password

    def get_part_3(self):
        self.captcha = self.solveCaptcha()
        self.digits = self.getDigits(passw=self.leap_year + self.two_letter_element + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.captcha + self.wordle + self.moon_phase)
        self.password = self.leap_year + self.two_letter_element + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase
        return self.password

    def get_part_4(self):
        self.country = self.findCountryName()
        self.password = self.leap_year + self.two_letter_element + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country
        return self.password

    def get_part_5(self):
        self.chess_notation = self.solveChessPuzzle()
        self.digits = self.getDigits(passw=self.leap_year + self.two_letter_element + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation)
        self.paul = self.getPaul()
        self.extra_elements = self.calculateElements(self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.paul)
        self.stronk = self.makeStrong()
        self.affirmation = self.getAffirmation()

        self.password = self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.extra_elements + self.stronk + self.affirmation + self.paul
        return self.password


    def get_part_6(self):
        self.paul = self.evolvePaul()
        self.food4paul = self.feedPaul()*5

        self.password = self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.extra_elements + self.stronk + self.affirmation + self.paul + self.food4paul
        return self.password

    def get_part_7(self):
        self.youtube_video = self.getYouTubeVideo()
        self.digits = self.getDigits(passw=self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.stronk + self.affirmation + self.youtube_video + self.paul + self.food4paul)
        self.extra_elements = self.calculateElements(self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.stronk + self.affirmation + self.youtube_video + self.paul + self.food4paul)

        
        self.password = self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.extra_elements + self.stronk + self.affirmation + self.youtube_video + self.paul + self.food4paul
        return self.password
    
    def get_part_8(self):
        self.nono_letters = self.sacrificeLetters()
        self.password = self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.extra_elements + self.stronk + self.affirmation + self.youtube_video + self.paul + self.food4paul
        return self.password

    def get_part_9(self):
        self.hex_colour = self.getHexColour()
        self.password_len = self.getPasswordLen(self.hex_colour)
        print(self.password_len)
        self.digits = self.getDigits(passw=self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.extra_elements + self.stronk + self.affirmation + self.youtube_video + self.hex_colour + self.paul + self.food4paul + self.password_len)
        self.password = self.leap_year + self.roman_numerals + self.sponsor + self.month + self.punctuation + self.digits + self.captcha + self.wordle + self.moon_phase + self.country + self.chess_notation + self.extra_elements + self.stronk + self.affirmation + self.youtube_video + self.hex_colour + self.paul + self.food4paul + self.password_len
        return self.password



    def makeItalic(self, password_with_bold:str):
        "Your password must contain twice as many italic characters as bold."
        bold_amount = password_with_bold.count("<strong>")
        # password_without_bold = password_with_bold.replace("<strong>", "<>").replace("</strong>", "</>")
        # password_with_italics = "<em>" + password_without_bold[:bold_amount*2+password_without_bold[:bold_amount*2].count("<>")] + "</em>" + password_without_bold[bold_amount*2:] # = f"<em>{password_without_bold[italic_num]}</em>"

        # password_with_bold_italics = password_with_italics.replace("<>", "<strong>").replace("</>", "</strong>")
        # return password_with_bold_italics

        return password_with_bold + "<em>" + "_"*bold_amount*2 + "</em>"
    
    def makeWingdings(self, password:str):
        bold_amount = password.count("<strong>")
        italics_loc = password.find("<em>" + "_"*bold_amount*2 + "</em>")
        wingdings =  password[:italics_loc] + '<span style="font-family: Wingdings">' + "<em>" + "_"*bold_amount*2 + "</em>" + '</span>'
        return wingdings
   
    def addWingdings(self, password:str):
        end_loc = password.find('</span>')
        wingdings = password.removesuffix('</span>') + int((len(password))/3)*"_" 
        return wingdings

    def getHexColour(self):
        retry = True
        while retry:
            colour_selector = self.page.wait_for_selector(self.Selectors.colour)
            style = colour_selector.get_attribute("style")
            rgb = style.replace("background: rgb(", "").replace(");", "")
            r,g,b = rgb.split(",")
            hex_colour = f'#{int(r.strip()):02x}{int(g.strip()):02x}{int(b.strip()):02x}'
            # print(hex_colour)
            for nono_letter in self.nono_letters:
                if nono_letter.lower() in hex_colour or self.getDigits(passw=self.password + hex_colour, Exit=False) == False:
                    colour_button = self.page.query_selector(self.Selectors.new_colour_btn)
                    colour_button.click()
                    retry = True
                    break
                else:
                    retry = False
            
        return hex_colour



    def makeTimesNewRoman(self, password:str):
        timesnewroman = password
        for numeral in "IVX":
            timesnewroman = timesnewroman.replace(numeral, f'<span style="font-family: Times New Roman">{numeral}</span>')
        return timesnewroman

    def changeFontSizeDigits(self, password:str):
        font_changed_password = password
        digits = []
        for character in password:
            if character.isdigit():
                digits.append(int(character))

        for digit in digits:
            font_changed_password = self.safeReplace(font_changed_password, str(digit), f'<span style="font-family: Monospace; font-size: {digit**2}px">{digit}</span>')
        # print(font_changed_password)
        return font_changed_password

    def changeFontSizeLetters_and_makeTimesNewRoman(self, password:str):
        letters = {}
        output = ""
        fontsizes = [0,1,4,9,12,16,25,28,32,36,42,49,64,81]
        for character in password:
            if character.isalpha():
                character_low = character.lower()
                letters[character_low] = letters.get(character_low) + 1 if letters.get(character_low) != None else 0
                occurence = letters[character_low]
                # print(occurence)
                output += f'<span style="font-family: {"Times New Roman" if character in "IVX" else "Monospace"}; font-size: {fontsizes[occurence]}px">{character}</span>'
            else:
                output += character
        # self.password_rich = output
        return output
            
    def getPasswordLen(self, extra:str):
        time.sleep(0.1)
        passw = self.page.query_selector(self.Selectors.pass_len_counter).inner_text() + extra
        passw_len = len(passw)
        passw_len_len = len(str(passw_len))

        print(passw_len, passw_len_len)

        return str(passw_len + int(passw_len_len)) # wont work occasionally but whatever


    def safeReplace(self, text, what_to_replace, replacement, count=0):
        pattern = r"(?![^<]*>)" + f"{what_to_replace}"

        replaced_text = re.sub(pattern, replacement, text, count)
        return replaced_text

############# <<-- Here

    def __str__(self) -> str:
        password = ""
        for rule in self.password:
            password += self.password[rule]
        return password



def run_playwright(artificialDelay = 1):
    # Create a Playwright instance
    with sync_playwright() as playwright:
        # Create a browser instance
        browser = playwright.chromium.launch(headless=False)

        # Create a context
        context = browser.new_context()

        # Create a page
        page = context.new_page()

        password = Password(page)

        # Navigate to a URL
        page.goto('https://neal.fun/password-game/')
        password_field = page.query_selector(password.Selectors.password_field)
        password_field.click()
        

        password_field.fill(password.get_part_1())
        time.sleep(1)

        password_field.fill(password.get_part_2())
        time.sleep(1)

        password_field.fill(password.get_part_3())
        time.sleep(2)

        password_field.fill(password.get_part_4())
        time.sleep(1)

        def fill_rich(rich_text):
            password_field.evaluate(f"node => node.innerHTML = '{rich_text}'")

        fill_rich(password.boldVowels(password.get_part_5()))
        fill_rich(password.boldVowels(password.password))
        time.sleep(1)

        fill_rich(password.boldVowels(password.get_part_6()))
        time.sleep(1)

        fill_rich(password.boldVowels(password.get_part_7()))
        time.sleep(1)

        fill_rich(password.makeWingdings(password.makeItalic(password.boldVowels(password.get_part_8()))))
        time.sleep(1)

        # print(password.changeFontSizeLetters(password.get_part_9()))
        fill_rich(password.changeFontSizeDigits(password.makeWingdings(password.makeItalic(password.boldVowels(password.changeFontSizeLetters_and_makeTimesNewRoman(password.get_part_9()))))))
        time.sleep(1)

        # fill_rich(password.changeFontSizeDigits(password.makeWingdings(password.makeItalic(password.boldVowels(password.changeFontSizeLetters_and_makeTimesNewRoman(password.get_part_10()))))))
        time.sleep(1)

        input()

        return

#   #   # Close the browser
#   #   # context.close()
#   #   # browser.close()

run_playwright(0.1)
