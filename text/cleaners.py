""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from .numbers import normalize_numbers


# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
  ('mrs', 'misess'),
  ('mr', 'mister'),
  ('dr', 'doctor'),
  ('st', 'saint'),
  ('co', 'company'),
  ('jr', 'junior'),
  ('maj', 'major'),
  ('gen', 'general'),
  ('drs', 'doctors'),
  ('rev', 'reverend'),
  ('lt', 'lieutenant'),
  ('hon', 'honorable'),
  ('sgt', 'sergeant'),
  ('capt', 'captain'),
  ('esq', 'esquire'),
  ('ltd', 'limited'),
  ('col', 'colonel'),
  ('ft', 'fort'),
]]

# pinyin-to-katakana map
map_path = './py2kn.json'
with open(map_path, 'r', encoding='utf-8') as f:
  py2kn_map = json.load(f)

punc_map = {'、': ',', '。': '.', '！': '!'} # punctuation map

# Regular expression matching Japanese without punctuation marks:
_japanese_characters = re.compile(r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Regular expression matching non-Japanese characters or punctuation marks:
_japanese_marks = re.compile(r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Tokenizer for Japanese
tokenizer = Tokenizer()


def expand_abbreviations(text):
  for regex, replacement in _abbreviations:
    text = re.sub(regex, replacement, text)
  return text


def expand_numbers(text):
  return normalize_numbers(text)


def lowercase(text):
  return text.lower()


def collapse_whitespace(text):
  return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
  return unidecode(text)


def basic_cleaners(text):
  '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def transliteration_cleaners(text):
  '''Pipeline for non-English text that transliterates to ASCII.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def english_cleaners(text):
  '''Pipeline for English text, including number and abbreviation expansion.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = expand_numbers(text)
  text = expand_abbreviations(text)
  text = collapse_whitespace(text)
  return text

def chinese_cleaners(text_ch):
  '''Pipeline for converting Chinese text to Japanese Romaji'''
  # Chinese characters to pinyin
  py_raw = pypinyin.pinyin(text_ch, style=pypinyin.NORMAL)
  pys = []
  for py in py_raw:
    pys.append(py[0])

  # katakana to romaji
  text_jp = ''
  for py in pys:
    text_jp += ''.join(py2kn_map[py])

  romaji = pyopenjtalk.g2p(text_jp, kana=False)
  romaji = romaji.replace('pau',',')
  romaji = romaji.replace(' ','')
  romaji = romaji + '.'

  return romaji

def chinese_tokenization_cleaners(text_ch):
  # Chinese characters to pinyin
  py_raw = pypinyin.pinyin(text_ch, style=pypinyin.NORMAL)
  pys = []
  for py in py_raw:
    pys.append(py[0])

  # katakana to romaji
  # text_jp = ''
  romaji = ''
  for i, py in enumerate(pys):
    kn = py2kn_map[py]
    if kn in punc_map:
      rmj = punc_map[kn] + ' '
      kn += ' '
      romaji += rmj
    else:
      if py2kn_map[pys[i + 1]] in punc_map:
        # There should not be a space before punctuation
        rmj = pyopenjtalk.g2p(kn, kana=False).replace(' ', '')
        romaji += rmj
      else:
        rmj = pyopenjtalk.g2p(kn, kana=False).replace(' ', '') + ' '
        romaji += rmj
        kn += ' '
    # text_jp += kn
  # remove the space at the end of the text
  # text_jp = text_jp[:-1]
  romaji = romaji[:-1]

  return romaji