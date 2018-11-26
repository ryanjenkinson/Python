# README
This is a quick text_normaliser that I built in a day or so that takes into account the following text normalisations:
- Contractions (e.g I'm -> I am)
- Pronounciation (using CMUdict to get a US pronounciation for the input text)
- Numbers (including support for turning numbers into words using my own function num2words, including support for ordinals and decimal points, and multiplication, division etc of numbers e.g 12\*13 -> twelve times 13)
- Times (e.g 3:45pm -> three fourty five pm)
- Dates (including both UK and US date structures e.g 10/12/2010 (UK) -> tenth of december two thousand and ten)
- Removal of punctuation
- Spellchecker (using pyspellchecker https://github.com/barrust/pyspellchecker, I did implement my own based on the code at http://norvig.com/spell-correct.html but pyspellchecker is generally better, and is itself based on the Norvig method - see Github repo readme for more information as it's very interesting!)

The idea is that once we can normalise blocks of text, we are able to use it as a preprocessing step in various NLP models, so it felt instructive to be able to build such tools.
