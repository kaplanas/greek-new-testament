import os
import csv
import re
import pymysql
import unicodedata
import pandas as pd
import numpy as np

RAW_DATA_DIR = 'dodson/'
DEFINITION_EDITS = pd.read_csv(RAW_DATA_DIR + 'definition_edits.csv', dtype=str)
SYNONYMS = pd.read_csv(RAW_DATA_DIR + 'synonyms.csv', dtype=str)
NOUN_FORM_EDITS = pd.read_csv(RAW_DATA_DIR + 'noun_forms.csv', dtype=str)
ADJECTIVE_FORM_EDITS = pd.read_csv(RAW_DATA_DIR + 'adjective_forms.csv', dtype=str)
VERB_FORM_EDITS = pd.read_csv(RAW_DATA_DIR + 'verb_forms.csv', dtype=str)
ASCII_UNICODE_MAPPING = [('\\*\\(/a\\|', 'ᾍ'),
                         ('\\*\\)/a', 'Ἄ'), ('\\*\\)=a', 'Ἆ'), ('\\*\\(/a', 'Ἅ'), ('a\\)/=', 'ἄ῀'), ('a\\)=\\|', 'ᾆ'),
                         ('a\\(/=', 'ἅ῀'), ('a\\(/\\|', 'ᾅ'), ('a\\(=\\|', 'ᾇ'), ('a\\)/\\|', 'ᾄ'),
                         ('\\*\\)a', 'Ἀ'), ('\\*a\\)', 'Ἀ'), ('\\*\\(a', 'Ἁ'), ('a\\)/', 'ἄ'), ('a/\\)', 'ἄ'),
                         ('a\\)\\\\', 'ἂ'), ('a\\)=', 'ἆ'), ('a=\\)', 'ἆ'), ('a\\+\\)', 'ἀ̈'), ('a\\(/', 'ἅ'),
                         ('a\\(\\\\', 'ἃ'), ('a\\(=', 'ἇ'), ('a\\)\\|', 'ᾀ'), ('a/\\|', 'ᾴ'), ('a=\\|', 'ᾷ'),
                         ('a\\+/', 'ά̈'), ('a/\\+', 'ά̈'),
                         ('\\*a', 'Α'), ('a\\)', 'ἀ'), ('a\\(', 'ἁ'), ('a/', 'ά'), ('a\\\\', 'ὰ'), ('a=', 'ᾶ'),
                         ('a\\|', 'ᾳ'), ('a\\+', 'α̈'),
                         ('a', 'α'),
                         ('\\*b', 'Β'), ('b', 'β'),
                         ('\\*g', 'Γ'), ('g', 'γ'),
                         ('\\*d', 'Δ'), ('d', 'δ'),
                         ('\\*\\)/e', 'Ἔ'), ('\\*\\(/e', 'Ἕ'),
                         ('\\*\\)e', 'Ἐ'), ('\\*\\(e', 'Ἑ'), ('e\\)/', 'ἔ'), ('e\\)\\\\', 'ἒ'), ('e\\)=', 'ἐ῀'),
                         ('e\\(/', 'ἕ'),
                         ('\\*e', 'Ε'), ('e\\)', 'ἐ'), ('e\\(', 'ἑ'), ('e/', 'έ'), ('e\\\\', 'ὲ'), ('e=', 'ε῀'),
                         ('e', 'ε'),
                         ('\\*z', 'Ζ'), ('z', 'ζ'),
                         ('\\*\\)/h', 'Ἤ'), ('\\*\\(/h', 'Ἥ'), ('h\\)/=', 'ή῀'), ('h\\)/\\|', 'ᾔ'), ('h\\)=\\|', 'ᾖ'),
                         ('h\\(/\\|', 'ᾕ'), ('h\\(=\\|', 'ᾗ'),
                         ('\\*\\)h', 'Ἠ'), ('\\*\\(h', 'Ἡ'), ('h\\)/', 'ἤ'), ('h\\)=', 'ἦ'), ('h\\)\\|', 'ᾐ'),
                         ('h\\(/', 'ἥ'), ('h\\(=', 'ἧ'), ('h=\\(', 'ἧ'), ('h\\(\\|', 'ᾑ'), ('h\\)\\\\', 'ἢ'),
                         ('h/\\|', 'ῄ'), ('h\\|/', 'ῄ'), ('h=\\|', 'ῇ'),
                         ('h\\)', 'ἠ'), ('h\\(', 'ἡ'), ('h/', 'ή'), ('h\\\\', 'ὴ'), ('h=', 'ῆ'), ('h\\|', 'ῃ'),
                         ('h', 'η'),
                         ('\\*q', 'Θ'), ('q', 'θ'),
                         ('\\*\\)/i', 'Ἴ'), ('\\*\\)=i', 'Ἶ'), ('i\\)/=', 'ἴ῀'), ('i\\)/\\+', 'ΐ᾿'),
                         ('\\*\\)i', 'Ἰ'), ('\\*\\(i', 'Ἱ'), ('i\\)/', 'ἴ'), ('i\\)=', 'ἶ'), ('i\\)\\+', 'ϊ᾿'),
                         ('i\\+\\)', 'ϊ᾿'), ('i\\(/', 'ἵ'), ('i\\(=', 'ἷ'), ('i/=', 'ί῀'), ('i/\\+', 'ΐ'),
                         ('i\\+/', 'ΐ'), ('i=\\+', 'ῗ'), ('i\\+=', 'ῗ'),
                         ('i\\)', 'ἰ'), ('i\\(', 'ἱ'), ('i/', 'ί'), ('i\\\\', 'ὶ'), ('i=', 'ῖ'), ('i\\+', 'ϊ'),
                         ('i', 'ι'),
                         ('\\*k', 'Κ'), ('k', 'κ'),
                         ('\\*l', 'Λ'), ('l', 'λ'),
                         ('\\*m', 'Μ'), ('m', 'μ'),
                         ('\\*n', 'Ν'), ('n=', 'ν'), ('n', 'ν'),
                         ('\\*c', 'Ξ'), ('c', 'ξ'),
                         ('\\*\\)/o', 'Ὄ'), ('\\*\\(/', 'Ὅ'), ('o\\)/\\+', 'ὄ̈'),
                         ('\\*\\)o', 'Ὀ'), ('\\*\\(o', 'Ὁ'), ('\\*o\\)', 'Ὀ'), ('o\\)/', 'ὄ'), ('o/\\)', 'ὄ'),
                         ('o\\)\\\\', 'ὂ'), ('o\\(/', 'ὅ'), ('o\\(=', 'ὁ῀'), ('o/=', 'ό῀'),
                         ('\\*o', 'Ο'), ('o\\)', 'ὀ'), ('o\\(', 'ὁ'), ('o/', 'ό'), ('o\\\\', 'ὸ'), ('o=', 'ο῀'),
                         ('o\\|', 'οι'), ('o\\+', 'ο̈'),
                         ('o', 'ο'),
                         ('\\*p', 'Π'), ('p', 'π'),
                         ('\\*\\)r', 'Ρ᾿'), ('\\*\\(r', 'Ῥ'), ('r\\)', 'ῤ'), ('r\\(', 'ῥ'), ('r', 'ρ'),
                         ('\\*s', 'Σ'), ('s\\|?($|[:,;.?! ])', 'ς'), ('s', 'σ'),
                         ('t=\\|', 't'), ('\\*t', 'Τ'), ('t/', 't'), ('t', 'τ'),
                         ('u\\(==', 'ὗ'),
                         ('\\*\\(u', 'Ὑ'), ('u\\)/', 'ὔ'), ('u\\)\\\\', 'ὒ'), ('u\\)=', 'ὖ'), ('u\\(/', 'ὕ'),
                         ('u\\(=', 'ὗ'), ('u/\\+', 'ΰ'), ('u\\+/', 'ΰ'), ('u\\+=', 'ῧ'), ('u=\\+', 'ῧ'),
                         ('u\\)', 'ὐ'), ('u\\(', 'ὑ'), ('u/', 'ύ'), ('u=', 'ῦ'), ('u\\+', 'ϋ'),
                         ('u', 'υ'),
                         ('\\*f', 'Φ'), ('f', 'φ'),
                         ('\\*x', 'Χ'), ('x', 'χ'),
                         ('\\*y', 'Ψ'), ('y', 'ψ'),
                         ('\\*\\)/w', 'Ὤ'), ('\\*\\)=w', 'Ὦ'), ('w\\)/\\|', 'ᾤ'), ('w\\)=\\|', 'ᾦ'), ('w\\(=\\|', 'ᾧ'),
                         ('\\*\\)w', 'Ὠ'), ('\\*\\(w', 'Ὡ'), ('w\\)/', 'ὤ'), ('w\\)=', 'ὦ'), ('w\\)\\|', 'ᾠ'),
                         ('w\\(/', 'ὥ'), ('w\\(=', 'ὧ'), ('w\\(\\|', 'ᾡ'), ('w/\\|', 'ῴ'), ('w=\\|', 'ῷ'),
                         ('w\\|=', 'ῷ'),
                         ('\\*w', 'Ω'), ('w\\(', 'ὡ'), ('w\\)', 'ὠ'), ('w/', 'ώ'), ('w=', 'ῶ'), ('w\\|', 'ῳ'),
                         ('w', 'ω'),
                         ('^/', ''), ('^=', ''), ('/$', '')]
ASCII_UNICODE_ALPHABETIZATION_MAPPING = {'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ', 'h': 'η', 'q': 'θ',
                                         'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'c': 'ξ', 'o': 'ο', 'p': 'π',
                                         'r': 'ρ', 's': 'σ', 't': 'τ', 'u': 'υ', 'f': 'φ', 'x': 'χ', 'y': 'ψ', 'w': 'ω'}
UNICODE_ACCENT_SWITCH_MAPPING = {'ὰ': 'ά', 'ᾲ': 'ᾴ', 'ἂ': 'ἄ', 'ἃ': 'ἅ', 'ᾂ': 'ᾄ', 'ᾃ': 'ᾅ', 'ὲ': 'έ', 'ἒ': 'ἔ',
                                 'ἓ': 'ἕ', 'ὴ': 'ή', 'ῂ': 'ῄ', 'ἢ': 'ἤ', 'ἣ': 'ἥ', 'ᾒ': 'ᾔ', 'ᾓ': 'ᾕ', 'ὶ': 'ί',
                                 'ῒ': 'ΐ', 'ἲ': 'ἴ', 'ἳ': 'ἵ', 'ὸ': 'ό', 'ὂ': 'ὄ', 'ὃ': 'ὅ', 'ὺ': 'ύ', 'ῢ': 'ΰ',
                                 'ὒ': 'ὔ', 'ὓ': 'ὕ', 'ὼ': 'ώ', 'ῲ': 'ῴ', 'ὢ': 'ὤ', 'ὣ': 'ὥ', 'ᾢ': 'ᾤ', 'ᾣ': 'ᾥ'}
GREEK_CAPITALS = '^[' + ''.join(set(chr(cp)
                                    for cp in range(0x0370, 0x1FFF)
                                    if "GREEK CAPITAL" in unicodedata.name(chr(cp), ""))) + ']'
LEMMA_EDITS = {'*)/abel': '*(/abel', '*)abia/qar': '*)abiaqa/r', '*)agabos': '*(/agabos', '*(/agar': '*(aga/r',
               '*(/a|dhs': 'a(/|dhs', '*)akeldama/': '*(akeldama/x', '*(allhlou/i+a': 'a(llhloui+a/',
               'a)llotrioepi/skopos': 'a)llotriepi/skopos', '*)alfai/os': '*(alfai=os', '*)ampli/as': '*)amplia=tos',
               'a)mfo/teroi': 'a)mfo/teros', 'a)na/lhyis': 'a)na/lhmyis', 'a)namimnh/skw': 'a)namimnh/|skw',
               '*)anani/as': '*(anani/as', 'a)nemi/zw': 'a)nemi/zomai', 'a)necereu/nhtos': 'a)necerau/nhtos',
               'a)nepi/lhptos': 'a)nepi/lhmptos', '*)/annas': '*(/annas', 'a)ntikru/': 'a)/ntikrus',
               'a)nti/lhyis': 'a)nti/lhmyis', '*)anti/pas': '*)antipa=s', 'a)ntipe/ran': 'a)ntipe/ra',
               'a)nw/teron': 'a)nw/teros', '*)apollw/s': '*)apollw=s', 'a)porri/ptw': 'a)pori/ptw',
               'a)re/skeia': 'a)reskei/a', '*)are/tas': '*(are/tas', '*)arimaqai/a': '*(arimaqai/a',
               '*)/assos': '*)=assos', '*au)gou/stos': '*au)gou=stos', '*)/axaz': '*)axa/z', '*)axai+a': '*)axai/+a',
               '*)axei/m': '*)axi/m', 'bai+/on': 'ba/i+on', 'bala/ntion': 'balla/ntion', '*bari+hsou=s': '*barihsou=s',
               '*bariwna=s': '*bariwna=', '*barna/bas': '*barnaba=s', '*barti/maios': '*bartimai=os',
               'battologe/w': 'battaloge/w', '*beli/ar': '*belia/r', '*bhqlee/m': '*bhqle/em', 'bi/azomai': 'bia/zw',
               'biblida/rion': 'biblari/dion', 'biquni/a': '*biquni/a', '*boanerge/s': '*boanhrge/s',
               '*boo/z': '*bo/es', 'braduth/s': 'bradu/ths', '*gabbaqa=': '*gabbaqa', '*geqshmanh=': '*geqshmani/',
               '*gergeshno/s': '*gerashno/s', 'geu/omai': 'geu/w', 'gumnhteu/w': 'gumniteu/w',
               'daneisth/s': 'danisth/s', 'decio/labos': 'deciola/bos', 'diarrh/ssw': 'diarrh/gnumi',
               'diasw/zw': 'diasw/|zw', '*diotrefh/s': '*diotre/fhs', 'dusenteri/a': 'dusente/rion',
               '*(/eber': '*)/eber', 'e)qeloqrhskei/a': 'e)qeloqrhski/a', 'ei)dwlolatrei/a': 'ei)dwlolatri/a',
               'e(katontae/ths': 'e(katontaeth/s', 'e)kkrema/nnumi': 'e)kkre/mamai', 'e)klanqa/nomai': 'e)klanqa/nw',
               'e)kle/gomai': 'e)kle/gw', '*)elaiw/n': 'e)laiw/n', 'e)lee/w': 'e)lea/w', '*)eliakei/m': '*)eliaki/m',
               '*)elissai=os': '*)elisai=os', 'e(lku/w': 'e(/lkw', '*)elmwda/m': '*)elmada/m',
               '*)emmaou/s': '*)emmaou=s', '*)emmo/r': '*(emmw/r', 'e)mpi/plhmi': 'e)mpi/mplhmi',
               'e)ndo/mhsis': 'e)ndw/mhsis', 'e)ndoca/zw': 'e)ndoca/zomai', '*)enw/x': '*(enw/x',
               'e)cereuna/w': 'e)cerauna/w', 'e)coloqreu/w': 'e)coleqreu/w', 'e)coudeno/w': 'e)coudene/w',
               'e)paqroi/zw': 'e)paqroi/zomai', 'e)panamimnh/skw': 'e)panamimnh/|skw', 'e)parxi/a': 'e)parxei/a',
               'e)pirra/ptw': 'e)pira/ptw', 'e)pirri/ptw': 'e)piri/ptw', 'e)pifau/w': 'e)pifau/skw',
               'e)reuna/w': 'e)rauna/w', '*)esli/': '*(esli/', '*eu)/a': '*eu(/a', '*eu)roklu/dwn': 'eu)raku/lwn',
               '*)efrai+/m': '*)efrai/m', '*zara/': '*za/ra', '*zoroba/bel': '*zorobabe/l', 'zwogone/w': 'zw|ogone/w',
               'h(=ttwn': 'h(/sswn', '*qa/mar': '*qama/r', 'qrh=skos': 'qrhsko/s', '*)ia/eiros': '*)ia/i+ros',
               '*)ianna/': '*)iannai/', '*)iannh=s': '*)ia/nnhs', '*)iare/d': '*)ia/ret',
               '*(ierousalh/m': '*)ierousalh/m', '*)ioudai+/zw': 'i)oudai+/zw', '*)isaxa/r': '*)issaxa/r',
               '*)iwa/qam': '*)iwaqa/m', '*)iwna/n': '*)iwna/m', '*)iwrei/m': '*)iwri/m', '*kai+na/n': '*kai+na/m',
               'kakopa/qeia': 'kakopaqi/a', '*kana=': '*kana/', 'katio/w': 'katio/omai', '*kapernaou/m': '*kafarnaou/m',
               'keno/docas': 'keno/docos', 'kefalaio/w': 'kefalio/w', '*klau=dh': '*kau=da',
               'kina/mwmon': 'kinna/mwmon', 'klei=s': 'klei/s', '*kore/': '*ko/re', 'ku/lisma': 'kulismo/s',
               '*kw=s': '*kw/s', '*laodikei/a': '*laodi/keia', 'legew/n': 'legiw/n', '*leui+/': '*leui/',
               '*leui+/s': '*leui/s', '*leui+/ths': '*leui/ths', '*leui+tiko/s': '*leuitiko/s', 'lh=yis': 'lh=myis',
               'liqo/strwton': 'liqo/strwtos', '*li=nos': '*li/nos', 'logi/a': 'logei/a', '*maa/q': '*ma/aq',
               '*maqousa/la': '*maqousala/', 'massa/omai': 'masa/omai', '*matqai=os': '*maqqai=os',
               '*matqa/t': '*maqqa/t', '*matqi/as': '*maqqi/as', '*ma/rkos': '*ma=rkos', '*melea=s': '*melea/',
               'me/lei': 'me/lw', '*melxisede/k': '*melxise/dek', 'meta/lhyis': 'meta/lhmyis',
               'mhtralw/|as': 'mhtrolw/|as', 'mimnh/skomai': 'mimnh/|skomai', 'moggila/los': 'mogila/los',
               'muri/oi': 'mu/rioi', '*mwsh=s': '*mwu+sh=s', '*naqa/n': '*naqa/m', '*neema/n': '*naima/n',
               '*nefqalei/m': '*nefqali/m', 'nhfale/os': 'nhfa/lios', 'nossia/': 'nossi/a', '*numfa=s': '*nu/mfas',
               'oi)keiako/s': 'oi)kiako/s', 'oi)/mai': 'oi)=mai', 'oi(/os': 'oi(=os', 'ou)kouro/s': 'oi)kourgo/s',
               'o)sfu/s': 'o)sfu=s', 'o)fqalmodoulei/a': 'o)fqalmodouli/a', 'panoiki/': 'panoikei/',
               'parakaqi/zw': 'parakaqe/zw', '*patro/bas': '*patroba=s', 'perikru/ptw': 'perikru/bw',
               'perilei/pw': 'perilei/pomai', 'perirrh/gnumi': 'perirh/gnumi', 'peteino/n': 'peteino/s',
               'plhmmu/ra': 'plh/mmura', 'plhsi/on': 'plh/sios', 'plo/os': 'plou=s', 'poreu/omai': 'poreu/w',
               'pra|u+/ths': 'prau+/ths', 'pro/sklhsis': 'pro/sklisis', 'pro/slhyis': 'pro/slhmyis',
               'proswpolhpte/w': 'proswpolhmpte/w', 'proswpolh/pths': 'proswpolh/mpths',
               'proswpolhyi/a': 'proswpolhmyi/a', 'prw/i+mos': 'pro/i+mos', 'prw/|ra': 'prw=|ra', 'pte/rna': 'pte/rnos',
               'ptu/rw': 'ptu/romai', 'puro/s': 'purro/s', '*(ragau=': '*(ragau/', 'r(e/da': 'r(edh/',
               '*(roubi/m': '*(roubh/n', 'r(upareu/omai': 'r(upareu/w', 'sabaw/q': '*sabaw/q',
               '*samarei/ths': '*samari/ths', '*samarei=tis': '*samari=tis', '*sapfei/rh': '*sa/pfira',
               'sa/pfeiros': 'sa/pfiros', '*sebasto/s': 'sebasto/s', '*semei+/': '*semei+/n', 'shriko/s': 'siriko/s',
               'sidh/reos': 'sidhrou=s', '*solomw/n': '*solomw=n', 'spi=los': 'spi/los', 'spla/gxna': 'spla/gxnon',
               'strwnnu/w': 'strw/nnumi', '*stwi+ko/s': '*stoi+ko/s', 'sugkakouxe/w': 'sugkakouxe/omai',
               'sugkatayhfi/zw': 'sugkatayhfi/zomai', 'sukomwrai/a': 'sukomore/a', 'summorfo/w': 'summorfi/zomai',
               'sunde/w': 'sunde/omai', 'sunepi/sthmi': 'sunefi/sthmi', 'sustauro/w': 'sustauro/omai',
               'sfuro/n': 'sfudro/n', '*tabhqa/': '*tabiqa/', 'tessara/konta': 'tessera/konta',
               'tessarakontaeth/s': 'tesserakontaeth/s', 'tetra/rxhs': 'tetraa/rxhs', 'tetrarxe/w': 'tetraarxe/w',
               'u(perekxu/nw': 'u(perekxu/nnomai', 'felo/nhs': 'failo/nhs', 'fa/rmakos': 'farmako/s',
               '*fortouna/tos': '*fortouna=tos', 'xa/lkou=s': 'xalkou=s', '*xanaa/n': '*xana/an', 'xh/ra': 'xh/ros',
               'xrewfeile/ths': 'xreofeile/ths', 'xri/sma': 'xri=sma', '*)wbh/d': '*)iwbh/d'}
NOUN_FORM_LEMMAS = ['ἐγώ', 'ἐμαυτοῦ', 'σεαυτοῦ', 'σύ', 'τις']
ADJECTIVE_FORM_LEMMAS = ['ἀλλήλων', 'αὐτός', 'ἑαυτοῦ', 'ἐκεῖνος', 'ἡλίκος', 'ὅδε', 'οἷος', 'ὁποῖος', 'ὅς', 'ὅσος',
                         'ὅστις', 'οὗτος', 'πηλίκος', 'ποῖος', 'πόσος', 'ποταπός', 'τηλικοῦτος', 'τοιόσδε', 'τοιοῦτος',
                         'τοσοῦτος']


def ascii_to_unicode(ascii_string):
    """Convert an ASCII representation of Greek to Unicode."""
    unicode = ascii_string
    for a, u in ASCII_UNICODE_MAPPING:
        if bool(re.search(a, unicode)):
            unicode = re.sub(a, u, unicode)
    return unicode


def get_noun_forms(lemmas_df, db_con, lxx_df):
    """Get the genitive singular of nouns."""

    # Initialize the value we'll return.
    nouns_df = lemmas_df[['Lemma', 'POS']].copy()

    # Get noun wordforms from the NT and LXX.
    sql = """SELECT DISTINCT Lemma, POS, Number, NCase, NounClassType, Wordform
             FROM words
             WHERE POS = 'noun'
                   OR POS IN """
    sql = sql + '(' + ', '.join(["'" + n + "'" for n in NOUN_FORM_LEMMAS]) + ')'
    nt_nouns_df = pd.read_sql(sql, db_con)
    lxx_nouns_df = lxx_df[(lxx_df.pos == 'noun') | (lxx_df.lemma.isin(NOUN_FORM_LEMMAS))]
    lxx_nouns_df = lxx_nouns_df[['lemma', 'pos', 'number', 'case', 'wordform']]
    lxx_nouns_df.rename(columns={'lemma': 'Lemma', 'pos': 'POS', 'number': 'Number', 'case': 'NCase',
                                 'wordform': 'Wordform'},
                        inplace=True)
    lxx_nouns_df['NounClassType'] = 'unknown'
    forms_df = pd.concat([nt_nouns_df, lxx_nouns_df]).copy()
    forms_df.drop_duplicates(inplace=True)
    forms_df.Wordform = forms_df.Wordform.replace(UNICODE_ACCENT_SWITCH_MAPPING, regex=True)
    forms_df.Wordform = np.where(forms_df.Lemma.str.istitle(), forms_df.Wordform, forms_df.Wordform.str.lower())

    # Get lemmas that don't need a genitive singular.
    no_gs_df = nt_nouns_df.groupby(['Lemma', 'POS'])\
                          .filter(lambda x: x.Number.str.contains('singular').all() and
                                            x.NCase.str.contains('nominative').all())\
                          [['Lemma', 'POS']]
    no_gs_df.drop_duplicates(inplace=True)
    no_gs_df['genitive_singular'] = '―'

    # Get genitive singular forms.
    gs_df = forms_df[(~forms_df.Lemma.isin(no_gs_df.Lemma)) &
                     (((forms_df.Number == 'singular') & (forms_df.NCase == 'genitive')) |
                      (forms_df.NounClassType == 'undeclined'))].groupby(['Lemma', 'POS']).first()
    gs_df.reset_index(inplace=True)
    gs_df.rename(columns={'Wordform': 'genitive_singular'}, inplace=True)

    # Combine noun forms.
    gs_df = pd.concat([no_gs_df, gs_df, NOUN_FORM_EDITS])
    nouns_df = nouns_df.merge(gs_df, on=['Lemma', 'POS'], how='left')
    nouns_df['noun_forms'] = nouns_df['genitive_singular']

    # Return the forms.
    return nouns_df[['Lemma', 'POS', 'noun_forms']]


def get_adjective_forms(lemmas_df, db_con, lxx_df):
    """Get the feminine and neuter nominative singular of adjectives."""

    # Initialize the value we'll return.
    adjectives_df = lemmas_df[['Lemma', 'POS']].copy()

    # Get adjective wordforms from the NT and LXX.
    sql = """SELECT DISTINCT Lemma, POS, Gender, Number, NCase, NounClassType, Wordform
             FROM words
             WHERE POS = 'adj'
                   OR POS = 'det'
                   OR Lemma IN """
    sql = sql + '(' + ', '.join(["'" + a + "'" for a in ADJECTIVE_FORM_LEMMAS]) + ')'
    nt_adjectives_df = pd.read_sql(sql, connection)
    lxx_adjectives_df = lxx_df[(lxx_df.pos == 'adjective') | (lxx_df.lemma.isin(ADJECTIVE_FORM_LEMMAS))]
    lxx_adjectives_df = lxx_adjectives_df[['lemma', 'pos', 'gender', 'number', 'case', 'wordform']]
    lxx_adjectives_df.rename(columns={'lemma': 'Lemma', 'pos': 'POS', 'gender': 'Gender', 'number': 'Number',
                                      'case': 'NCase', 'wordform': 'Wordform'},
                             inplace=True)
    lxx_adjectives_df['NounClassType'] = 'unknown'
    forms_df = pd.concat([nt_adjectives_df, lxx_adjectives_df])
    forms_df.drop_duplicates(inplace=True)
    forms_df.Wordform = forms_df.Wordform.replace(UNICODE_ACCENT_SWITCH_MAPPING, regex=True)
    forms_df.Wordform = np.where(forms_df.Lemma[0] in GREEK_CAPITALS, forms_df.Wordform, forms_df.Wordform.str.lower())

    # Get lemmas that don't need a feminine.
    no_f_df = nt_adjectives_df.groupby(['Lemma', 'POS'])\
                              .filter(lambda x: ~x.Gender.str.contains('feminine').any())\
                              [['Lemma', 'POS']]
    no_f_df.drop_duplicates(inplace=True)
    no_f_df['feminine'] = '―'

    # Get feminine forms.
    f_df = forms_df[(~forms_df.Lemma.isin(no_f_df.Lemma)) & (forms_df.NCase == 'nominative') &
                    (forms_df.Number == 'singular') & (forms_df.Gender == 'feminine')]\
                   .groupby(['Lemma', 'POS']).first().copy()
    f_df.reset_index(inplace=True)
    f_df.rename(columns={'Wordform': 'feminine'}, inplace=True)
    m_df = forms_df[(forms_df.NounClassType.isin(['second declension', 'third declension, vowel stem',
                                                  'third declension, consonant stem'])) &
                    (~forms_df.Lemma.isin(no_f_df.Lemma)) & (~forms_df.Lemma.isin(f_df.Lemma))].copy()
    m_df = m_df[['Lemma', 'POS']]
    m_df.drop_duplicates(inplace=True)
    m_df['feminine'] = m_df.Lemma
    f_edits = ADJECTIVE_FORM_EDITS[['Lemma', 'POS', 'feminine']]
    f_edits = f_edits[~f_edits.feminine.isna()]

    # Get lemmas that don't need a neuter.
    no_n_df = nt_adjectives_df.groupby(['Lemma', 'POS'])\
                              .filter(lambda x: ~x.Gender.str.contains('neuter').any())\
                              [['Lemma', 'POS']]
    no_n_df.drop_duplicates(inplace=True)
    no_n_df['neuter'] = '―'

    # Get neuter forms.
    n_df = forms_df[(~forms_df.Lemma.isin(no_n_df.Lemma)) & (forms_df.NCase.isin(['nominative', 'accusative'])) &
                    (forms_df.Number == 'singular') & (forms_df.Gender == 'neuter')]\
                   .groupby(['Lemma', 'POS']).first().copy()
    n_df.reset_index(inplace=True)
    n_df.rename(columns={'Wordform': 'neuter'}, inplace=True)
    n_edits = ADJECTIVE_FORM_EDITS[['Lemma', 'POS', 'neuter']]
    n_edits = n_edits[~n_edits.neuter.isna()]

    # Combine adjective forms.
    f_df = pd.concat([no_f_df, f_df, m_df, f_edits])
    n_df = pd.concat([no_n_df, n_df, n_edits])
    adjectives_df = adjectives_df.merge(f_df, on=['Lemma', 'POS'], how='left')
    adjectives_df = adjectives_df.merge(n_df, on=['Lemma', 'POS'], how='left')
    adjectives_df['adjective_forms'] = adjectives_df['feminine'] + ', ' + adjectives_df['neuter']

    # Return the forms.
    return adjectives_df[['Lemma', 'POS', 'adjective_forms']]


def get_verb_forms(lemmas_df, db_con, lxx_df):
    """Get principal parts of verbs."""

    # Initialize the value we'll return.
    verbs_df = lemmas_df[['Lemma', 'POS']].copy()

    # Get verb wordforms from the NT and LXX.
    sql = "SELECT DISTINCT Lemma, POS, Gender, Number, NCase, Person, Tense, Mood, Voice, Wordform FROM words WHERE POS = 'verb'"
    nt_verbs_df = pd.read_sql(sql, connection)
    lxx_verbs_df = lxx_df[lxx_df.pos == 'verb']
    lxx_verbs_df = lxx_verbs_df[['lemma', 'pos', 'gender', 'number', 'case', 'person', 'tense', 'mood', 'voice',
                                 'wordform']]
    lxx_verbs_df.rename(columns={'lemma': 'Lemma', 'pos': 'POS', 'gender': 'Gender', 'number': 'Number',
                                 'case': 'NCase', 'person': 'Person', 'tense': 'Tense', 'mood': 'Mood',
                                 'voice': 'Voice', 'wordform': 'Wordform'},
                        inplace=True)
    forms_df = pd.concat([nt_verbs_df, lxx_verbs_df])
    forms_df.drop_duplicates(inplace=True)
    forms_df.Wordform = forms_df.Wordform.replace(UNICODE_ACCENT_SWITCH_MAPPING, regex=True)
    forms_df.Wordform = forms_df.Wordform.str.lower()

    # Get lemmas that don't need a future active.
    no_fa_df = nt_verbs_df.groupby(['Lemma', 'POS'])\
                          .filter(lambda x: ~(x.Tense.str.contains('future') &
                                              x.Voice.isin(['active', 'middle'])).any())\
                          [['Lemma', 'POS']]
    no_fa_df.drop_duplicates(inplace=True)
    no_fa_df['future_active'] = '―'

    # Get future active forms.
    fa_df = forms_df[(~forms_df.Lemma.isin(no_fa_df.Lemma)) & (forms_df.Person == 'first') &
                     (forms_df.Number == 'singular') & (forms_df.Mood == 'indicative') & (forms_df.Voice == 'active') &
                     (forms_df.Tense == 'future')]\
                    .groupby(['Lemma', 'POS']).first().copy()
    fa_df.reset_index(inplace=True)
    fa_df = fa_df[['Lemma', 'POS', 'Wordform']]
    fa_df.rename(columns={'Wordform': 'future_active'}, inplace=True)
    fa_edits = VERB_FORM_EDITS[['Lemma', 'POS', 'future_active']]
    fa_edits = fa_edits[~fa_edits.future_active.isna()]

    # Get lemmas that don't need an aorist active.
    no_aa_df = nt_verbs_df.groupby(['Lemma', 'POS'])\
                          .filter(lambda x: ~(x.Tense.str.contains('aorist') &
                                              x.Voice.isin(['active', 'middle'])).any())\
                          [['Lemma', 'POS']]
    no_aa_df.drop_duplicates(inplace=True)
    no_aa_df['aorist_active'] = '―'

    # Get aorist active forms.
    aa_df = forms_df[(~forms_df.Lemma.isin(no_aa_df.Lemma)) & (forms_df.Person == 'first') &
                     (forms_df.Number == 'singular') & (forms_df.Mood == 'indicative') & (forms_df.Voice == 'active') &
                     (forms_df.Tense == 'aorist') & (forms_df.Lemma != 'ἀνθίστημι')]\
                    .groupby(['Lemma', 'POS']).first().copy()
    aa_df.reset_index(inplace=True)
    aa_df = aa_df[['Lemma', 'POS', 'Wordform']]
    aa_df.rename(columns={'Wordform': 'aorist_active'}, inplace=True)
    aa_edits = VERB_FORM_EDITS[['Lemma', 'POS', 'aorist_active']]
    aa_edits = aa_edits[~aa_edits.aorist_active.isna()]

    # Get lemmas that don't need a perfect active.
    no_pa_df = nt_verbs_df.groupby(['Lemma', 'POS'])\
                          .filter(lambda x: ~(x.Tense.isin(['perfect', 'pluperfect']) &
                                              x.Voice.str.contains('active')).any())\
                          [['Lemma', 'POS']]
    no_pa_df.drop_duplicates(inplace=True)
    no_pa_df['perfect_active'] = '―'

    # Get perfect active forms.
    pa_df = forms_df[(~forms_df.Lemma.isin(no_pa_df.Lemma)) & (forms_df.Person == 'first') &
                     (forms_df.Number == 'singular') & (forms_df.Mood == 'indicative') & (forms_df.Voice == 'active') &
                     (forms_df.Tense == 'perfect')]\
                    .groupby(['Lemma', 'POS']).first().copy()
    pa_df.reset_index(inplace=True)
    pa_df = pa_df[['Lemma', 'POS', 'Wordform']]
    pa_df.rename(columns={'Wordform': 'perfect_active'}, inplace=True)
    pa_edits = VERB_FORM_EDITS[['Lemma', 'POS', 'perfect_active']]
    pa_edits = pa_edits[~pa_edits.perfect_active.isna()]

    # Get lemmas that don't need a perfect middle.
    no_pm_df = nt_verbs_df.groupby(['Lemma', 'POS'])\
                          .filter(lambda x: ~(x.Tense.isin(['perfect', 'pluperfect']) &
                                              x.Voice.isin(['middle', 'passive'])).any())\
                          [['Lemma', 'POS']]
    no_pm_df.drop_duplicates(inplace=True)
    no_pm_df['perfect_middle'] = '―'

    # Get perfect middle forms.
    pm_df = forms_df[(~forms_df.Lemma.isin(no_pm_df.Lemma)) & (forms_df.Person == 'first') &
                     (forms_df.Number == 'singular') & (forms_df.Mood == 'indicative') & (forms_df.Voice == 'middle') &
                     (forms_df.Tense == 'perfect')]\
                    .groupby(['Lemma', 'POS']).first().copy()
    pm_df.reset_index(inplace=True)
    pm_df = pm_df[['Lemma', 'POS', 'Wordform']]
    pm_df.rename(columns={'Wordform': 'perfect_middle'}, inplace=True)
    pm_edits = VERB_FORM_EDITS[['Lemma', 'POS', 'perfect_middle']]
    pm_edits = pm_edits[~pm_edits.perfect_middle.isna()]

    # Get lemmas that don't need a future passive.
    no_fp_df = nt_verbs_df.groupby(['Lemma', 'POS'])\
                          .filter(lambda x: ~(x.Tense.isin(['future', 'aorist']) &
                                              x.Voice.str.contains('passive')).any())\
                          [['Lemma', 'POS']]
    no_fp_df.drop_duplicates(inplace=True)
    no_fp_df['future_passive'] = '―'

    # Get future passive forms.
    fp_df = forms_df[(~forms_df.Lemma.isin(no_fp_df.Lemma)) & (forms_df.Person == 'first') &
                     (forms_df.Number == 'singular') & (forms_df.Mood == 'indicative') & (forms_df.Voice == 'passive') &
                     (forms_df.Tense == 'future')]\
                    .groupby(['Lemma', 'POS']).first().copy()
    fp_df.reset_index(inplace=True)
    fp_df = fp_df[['Lemma', 'POS', 'Wordform']]
    fp_df.rename(columns={'Wordform': 'future_passive'}, inplace=True)
    fp_edits = VERB_FORM_EDITS[['Lemma', 'POS', 'future_passive']]
    fp_edits = fp_edits[~fp_edits.future_passive.isna()]

    # Combine verb forms.
    fa_df = pd.concat([no_fa_df, fa_df, fa_edits])
    aa_df = pd.concat([no_aa_df, aa_df, aa_edits])
    pa_df = pd.concat([no_pa_df, pa_df, pa_edits])
    pm_df = pd.concat([no_pm_df, pm_df, pm_edits])
    fp_df = pd.concat([no_fp_df, fp_df, fp_edits])
    verbs_df = verbs_df.merge(fa_df, on=['Lemma', 'POS'], how='left')
    verbs_df = verbs_df.merge(aa_df, on=['Lemma', 'POS'], how='left')
    verbs_df = verbs_df.merge(pa_df, on=['Lemma', 'POS'], how='left')
    verbs_df = verbs_df.merge(pm_df, on=['Lemma', 'POS'], how='left')
    verbs_df = verbs_df.merge(fp_df, on=['Lemma', 'POS'], how='left')
    verbs_df['verb_forms'] = verbs_df['future_active'] + ', ' + verbs_df['future_passive'] + ', ' + \
                             verbs_df['perfect_active'] + ', ' + verbs_df['perfect_middle'] + ', ' + \
                             verbs_df['future_passive']

    # Return the forms.
    return verbs_df[['Lemma', 'POS', 'verb_forms']]


if __name__ == '__main__':

    # Get the lexicon entries.
    pd.set_option('display.max_columns', None)
    entries_df = pd.read_csv(RAW_DATA_DIR + 'dodson.csv', quoting=csv.QUOTE_ALL, sep='\t', header = 0,
                             names=['strongs', 'gk', 'greek_word', 'definition', 'long_definition'])
    entries_df['lemma_ascii'] = entries_df.greek_word.replace(', .*$', '', regex=True)
    entries_df['lemma_ascii'] = entries_df.lemma_ascii.replace(LEMMA_EDITS)
    entries_df['definition'] = entries_df.definition.str.replace(r'^(I|the|a|an) ', '', regex=True)
    entries_df['definition'] = entries_df.definition.str.replace(r'^am( |,)', 'be\\1', regex=True)
    entries_df = entries_df[['lemma_ascii', 'definition']]
    entries_df = entries_df.groupby(['lemma_ascii']).agg('; '.join)
    entries_df.reset_index(inplace=True)

    # Connect to the database.
    connection = pymysql.connect(host='localhost', user='root', password=os.environ['MYSQL_PASSWORD'], database='gnt')

    # Add lemmas and edit definitions.
    lemmas_df = pd.concat([entries_df[~entries_df.lemma_ascii.isin(DEFINITION_EDITS.lemma_ascii)],
                           DEFINITION_EDITS,
                           SYNONYMS.merge(entries_df.rename({'lemma_ascii': 'synonym'},
                                                            axis=1)[['synonym', 'definition']],
                                          on=['synonym'])[['lemma_ascii', 'definition']]])
    lemmas_df['Lemma'] = lemmas_df['lemma_ascii'].apply(ascii_to_unicode)

    # Create a field without diacritics, for sorting.
    lemmas_df['lemma_sort'] = lemmas_df['lemma_ascii']
    lemmas_df.lemma_sort = lemmas_df.lemma_sort.replace({'[^abgdezhqiklmncoprstufxyw]': ''}, regex = True)
    lemmas_df.lemma_sort = lemmas_df.lemma_sort.replace(ASCII_UNICODE_ALPHABETIZATION_MAPPING,  regex = True)

    # Get lemmas that are present in the NT.
    sql = "SELECT DISTINCT Lemma, POS FROM words"
    nt_lemmas_df = pd.read_sql(sql, connection)
    nt_lemmas_df.Lemma = nt_lemmas_df.Lemma.replace({'καταβιβάζω': 'καταβιβάζω'})
    entries_df = lemmas_df.merge(nt_lemmas_df, on=['Lemma'])

    # Get wordforms from the LXX.
    lxx_wordforms_df = pd.read_csv('../text_data/lxx_text.csv')
    lxx_wordforms_df.lemma = lxx_wordforms_df.lemma.replace({'·': ''}, regex=True)

    # Get principal parts.
    entries_df = entries_df[['Lemma', 'lemma_sort', 'POS', 'definition']]
    entries_df = entries_df.merge(get_noun_forms(entries_df, connection, lxx_wordforms_df),
                                  on=['Lemma', 'POS'], how='left')
    entries_df = entries_df.merge(get_adjective_forms(entries_df, connection, lxx_wordforms_df),
                                  on=['Lemma', 'POS'], how='left')
    entries_df = entries_df.merge(get_verb_forms(entries_df, connection, lxx_wordforms_df),
                                  on=['Lemma', 'POS'], how='left')
    entries_df['principal_parts'] = entries_df.noun_forms.combine_first(entries_df.adjective_forms)\
                                                         .combine_first(entries_df.verb_forms)
    entries_df.replace(np.nan, None, inplace=True)

    # Write lemmas to the database.
    entries_list = list(entries_df[['Lemma', 'lemma_sort', 'POS', 'principal_parts', 'definition']].to_records(index=False))
    entries_list = [tuple(el) for el in entries_list]
    with connection.cursor() as cur:
        sql = """INSERT INTO lemmas
                 (Lemma, LemmaSort, POS, PrincipalParts, ShortDefinition)
                 VALUES
                 (%s, %s, %s, %s, %s)"""
        cur.executemany(sql, entries_list)
    connection.commit()

    # Close the database connection.
    connection.close()
