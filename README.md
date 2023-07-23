# ThePasswordGame-Auto
Complex python script that plays https://neal.fun/password-game/ completely automatically

- [x] Rule 1 `Your password must be at least 5 characters.`
- [x] Rule 2 `Your password must include a number.`
- [x] Rule 3 `Your password must include an uppercase letter.`
- [x] Rule 4 `Your password must include a special character.`
- [x] Rule 5 `The digits in your password must add up to 25.`
- [x] Rule 6 `Your password must include a month of the year.`
- [x] Rule 7 `Your password must include a roman numeral.`
- [x] Rule 8 `Your password must include one of our sponsors`
- [x] Rule 9 `The roman numerals in your password should multiply to 35.`
- [x] Rule 10 `Your password must include this CAPTCHA:`
- [x] Rule 11 `Your password must include today's Wordle answer.`
- [x] Rule 12 `Your password must include a two letter symbol from the periodic table.`
- [x] Rule 13 `Your password must include the current phase of the moon as an emoji.`
- [x] Rule 14 `Your password must include the name of this country.`
- [x] Rule 15 `Your password must include a leap year.`
- [x] Rule 16 `Your password must include the best move in algebraic chess notation.`
- [x] Rule 17 `🥚 ← This is my chicken Paul. He hasn't hatched yet, please put him in your password and keep him safe.`
- [x] Rule 18 `The elements in your password must have atomic numbers that add up to 200.`
- [x] Rule 19 `All the vowels in your password must be bolded.`
- [x] Rule 20 `Oh no! Your password is on fire. Quick, put it out!`
- [x] Rule 21 `Your password is not strong enough 🏋️‍♂️`
- [x] Rule 22 `Your password must contain one of the following affirmations`
- [x] Rule 23 `Paul has hatched! Please don't forget to feed him, he eats three 🐛 every minute.`
- [x] Rule 24 `Your password must include the URL of a xx minute yy second long YouTube video.`
- [x] Rule 25 `A sacrifice must be made. Pick 2 letters that you will no longer be able to use.`
- [x] Rule 26 `Your password must contain twice as many italic characters as bold.`
- [x] Rule 27 `At least 30% of your password must be in the Wingdings font.`
- [x] Rule 28 `Your password must include this color in hex.`
- [x] Rule 29 `All roman numerals must be in Times New Roman..`
- [x] Rule 30 `The font size of every digit must be equal to its square.`
- [x] Rule 31 `Every instance of the same letter must have a different font size.`

### Notable features:
- Automatically solves captcha
- Automatically finds wordle answer
- Automatically calculates the current moon phase with great accuracy
- Automatically finds the name of the country in the geoguesser embed
- Solves any chess puzzle using the Stockfish chess engine, after parsing the image
- Automatically balances out all digits, Roman numerals and elements
- Automatically finds the correct youtube video with exact length. (I made a half-finished scraper before I found "the spreadsheet" . I diddnt have the heart to delete it so it's just commented out lol)
- Automatically ajusts the password's length to be a prime number


### Problems:
- `Rule 16` Occasionally, the best chess move will be incorrect.
- `Rule 24` Fails a significant amount of times because of unwanted elements in the video url. (You can help fix this issue by finding new links for assets/youtube_links.json)


### Credit
#### A big thanks to:
+ @[nickacide](https://github.com/nickacide) for debugging the website code, and helping me think of solutions
+ @[pog5](https://github.com/pog5) for creating a [helpful guide](https://github.com/pog5/nealpasswordgame) and jumpstarting my progress
+ @[shelerr](https://www.youtube.com/@shelerr) for making ["the spreadsheet"](https://drive.google.com/file/d/1UZdXQVfrnDnJ1WtWPsZiYCbO2BPsRCip/view)

#### A big 🖕 to:
+ Whatever program obfusated Neal's code.

#### Sorry if some parts of my code is ugly. I usually fix it up at the end, but I'm not finished yet.
