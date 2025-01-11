import os
import pymysql
import re
import pandas as pd
from bs4 import BeautifulSoup

RAW_DATA_DIR = 'perseus/'
DEFINITION_EDITS = pd.read_csv(RAW_DATA_DIR + 'definition_edits.csv', dtype=str)
SYNONYMS = pd.read_csv(RAW_DATA_DIR + 'synonyms.csv', dtype=str)
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
                         ('i\\+/', 'ΐ'), ('i=\\+', 'ῗ'), ('i\\+=', 'ῗ'),
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
                         ('\\*\\)/w', 'Ὤ'), ('w\\)/\\|', 'ᾤ'), ('w\\)=\\|', 'ᾦ'), ('w\\(=\\|', 'ᾧ'),
                         ('\\*\\)w', 'Ὠ'), ('\\*\\(w', 'Ὡ'), ('w\\)/', 'ὤ'), ('w\\)=', 'ὦ'), ('w\\)\\|', 'ᾠ'),
                         ('w\\(/', 'ὥ'), ('w\\(=', 'ὧ'), ('w\\(\\|', 'ᾡ'), ('w/\\|', 'ῴ'), ('w=\\|', 'ῷ'),
                         ('w\\|=', 'ῷ'),
                         ('\\*w', 'Ω'), ('w\\(', 'ὡ'), ('w\\)', 'ὠ'), ('w/', 'ώ'), ('w=', 'ῶ'), ('w\\|', 'ῳ'),
                         ('w', 'ω'),
                         ('^/', ''), ('^=', ''), ('/$', '')]
ASCII_UNICODE_ALPHABETIZATION_MAPPING = {'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ', 'h': 'η', 'q': 'θ',
                                         'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'c': 'ξ', 'o': 'ο', 'p': 'π',
                                         'r': 'ρ', 's': 'σ', 't': 'τ', 'u': 'υ', 'f': 'φ', 'x': 'χ', 'y': 'ψ', 'w': 'ω'}
LEMMA_EDITS = {'a)gaqopoii/a': 'a)gaqopoii/+a', 'a(gi/zw': 'a(gia/zw', 'a)griela/inos': 'a)grie/laios',
               'a(droth/s': 'a(dro/ths', 'a)ei/dw': 'a)/|dw', 'a)ei/rw': 'ai)/rw', 'a)qe/mistos': 'a)qe/mitos',
               'a)qe/smios': 'a)/qesmos', '*(/aidhs': 'a(/|dhs', '*ai)nei/as': '*ai)ne/as', 'ai)ti/ama': 'ai)ti/wma',
               'a)la/bastos': 'a)la/bastros', 'a)le/w': 'a)lh/qw', 'a)llotrioepi/skopos': 'a)llotriepi/skopos',
               'a)nagignw/skw': 'a)naginw/skw', 'a)na/lhyis': 'a)na/lhmyis', 'a)namimnh/skw': 'a)namimnh/|skw',
               'a)necereu/nhtos': 'ἀνεξεραύνητος', 'a)nepi/lhptos': 'ἀνεπίλημπτος', 'a)noi/gnumi': 'a)noi/gw',
               'a)nti/lhyis': 'a)nti/lhmyis', 'a)ntipe/ran': 'a)ntipe/ra', 'a)nakai/nisis': 'a)nakai/nwsis',
               'a)para/skeuos': 'a)paraskeu/astos', 'a(plo/os': 'a(plou=s', 'a)pogi/gnomai': 'a)pogi/nomai',
               'a)podekto/s': 'a)po/dektos', 'a)poqnh/skw': 'a)poqnh/|skw', 'a)/pokrisis': 'a)po/krisis',
               'a)poni/zw': 'a)poni/ptw', 'a)porri/ptw': 'a)pori/ptw', 'a)postasi/ou': 'a)posta/sion',
               'a)proswpo/lhptos': 'a)proswpo/lhmptos', 'a)/rrafos': 'a)/rafos', 'a)re/skeia': 'a)reskei/a',
               'a)ro/w': 'a)rotria/w', 'a)rrenokoi/ths': 'a)rsenokoi/ths', 'a)rtigenh/s': 'a)rtige/nnhtos',
               'a)sqeno/w': 'a)sqene/w', '*au)/goustos': '*au)gou=stos', '*)axai/a': '*)axai/+a',
               '*)axaiiko/s': '*)axai+ko/s', 'a)yi/nqion': 'a)/yinqos', 'battologe/w': 'battaloge/w',
               'biata/s': 'biasth/s', 'blhte/on': 'blhte/os', 'bohqo/os': 'bohqo/s', 'bo/qros': 'bo/qunos',
               '*bore/as': 'borra=s', 'braduth/s': 'bradu/ths', 'bru/kw': 'bru/xw', 'bu/blos': 'bi/blos',
               'bursode/yhs': 'burseu/s', 'gi/gnomai': 'gi/nomai', 'gignw/skw': 'ginw/skw',
               'glwssokomei=on': 'glwsso/komon', 'gumnhteu/w': 'gumniteu/w', 'daneisth/s': 'danisth/s',
               'deka/polis': '*deka/polis', 'de/ndreon': 'de/ndron', 'diagi/gnomai': 'diagi/nomai',
               'diagignw/skw': 'diaginw/skw', 'di/dumos': '*di/dumos', 'diethri/s': 'dieti/a',
               '*diopeth/s': 'diopeth/s', 'diplo/os': 'diplou=s', 'dismu/rioi': 'dismuria/s', 'diuli/zw': 'diu+li/zw',
               'di/ya': 'di/yos', 'diwkth/r': 'diw/kths', 'dokimei=on': 'doki/mion', 'doth/r': 'do/ths',
               'du/w': 'du/nw', 'dusenteri/a': 'dusente/rion', 'duw/deka': 'dw/deka', 'dwdeka/fulos': 'dwdeka/fulon',
               'e)qeloqrhskei/a': 'e)qeloqrhski/a', 'e)qe/lw': 'qe/lw', 'ei)/soptron': 'e)/soptron',
               'e(katontae/ths': 'e(katontaeth/s', 'e)lasso/w': 'e)latto/w', 'e)lee/w': 'e)lea/w', 'e)ne/os': 'e)neo/s',
               'e)nnu/xios': 'e)/nnuxos', 'e)nw/pios': 'e)nw/pion', 'e)cagora/cw': 'e)cagora/zw',
               'e)capi/nhs': 'e)ca/pina', 'e)cereuna/w': 'e)cerauna/w', 'e)cwte/rw': 'e)cw/teros',
               'e)pa/nagkos': 'e)pa/nagkes', 'e)pigi/gnomai': 'e)pigi/nomai', 'e)pigignw/skw': 'e)piginw/skw',
               'e)pidei/knumi (nu/w': 'e)pidei/knumi', 'e)pidu/w ': 'e)pidu/w', 'e)pilh/qw': 'e)pilanqa/nw',
               'e)pirra/ptw': 'e)pira/ptw', 'e)pirri/ptw': 'e)piri/ptw', 'e)reuna/w': 'e)rauna/w',
               'e)rh=mos': 'e)/rhmos', 'e)ru/w': 'r(u/omai', 'e)/swqen ': 'e)/swqen', 'e(toi=mos': 'e(/toimos',
               'e)fech=s': 'kaqech=s', 'zeukth/rios': 'zeukthri/a', 'zw=': 'za/w', 'zwh/ ': 'zwh/',
               'zwogone/w': 'zw|ogone/w', 'zwopoie/w': 'zw|opoie/w', 'h(du/osmos': 'h(du/osmon',
               'h(likiw/ths': 'sunhlikiw/ths', 'h(miwri/a': 'h(miw/rion', 'h(ssa/omai': 'h(tta/omai',
               'qanath/foros': 'qanathfo/ros', 'qeo/maxos': 'qeoma/xos', 'qeristh/r': 'qeristh/s',
               'qrh=skos': 'qrhsko/s', 'i)de/a': 'ei)de/a', 'i)dou=': 'i)dou/', 'i(keth/rios': 'i(kethri/a',
               'i(/laos': 'i(/leos', '*)=iris': 'i)=ris', 'i)xqu=s': 'i)xqu/s', 'kaqarmo/s': 'kaqarismo/s',
               'kaqhme/rios': 'kaqhmerino/s', 'kai/ toi': 'kai/toi', 'kakopa/qeia': 'kakopaqi/a',
               'ka/kourgos': 'kakou=rgos', 'karpo/foros': 'karpofo/ros', 'katagignw/skw': 'kataginw/skw',
               'kataliqo/w': 'kataliqa/zw', 'katamu/w': 'kammu/w', 'kate/nanta': 'kate/nanti',
               'kate/nwpa': 'katenw/pion', 'kauthria/zw': 'kausthria/zw', 'kentori/wn': 'kenturi/wn',
               'kefalaio/w': 'kefalio/w', 'klauqmonh/': 'klauqmo/s', 'klhro/nomos': 'klhrono/mos',
               'knafeu/s': 'gnafeu/s', 'kollu/rion': 'kollou/rion', 'kra/bbatos': 'kra/battos',
               'krei/sswn': 'krei/ttwn', 'kri/banos': 'kli/banos', 'krupth/': 'kru/pth', 'la/qrh|': 'la/qra|',
               'legew/n': 'legiw/n', 'lh=yis': 'lh=myis', '*ma/gos': 'ma/gos', 'ma/kroqen': 'makro/qen',
               'mesonu/ktios': 'mesonu/ktion', 'mei/gnumi': 'mi/gnumi', 'meta/lhyis': 'meta/lhmyis',
               'mhtraloi/as': 'mhtrolw/|as', 'mimnh/skw': 'mimnh/|skw', 'nea/niskos': 'neani/skos',
               'new/koros': 'newko/ros', 'ni/zw': 'ni/ptw', 'no/os': 'nou=s', 'nouqe/thsis': 'nouqesi/a',
               'nw=ton': 'nw=tos', 'cenodoke/w': 'cenodoxe/w', 'cure/w': 'cura/w', 'oi)kodo/mhsis': 'oi)kodomh/',
               'oi)ko/domos': 'oi)kodo/mos', 'oi)ko/nomos': 'oi)kono/mos', 'oi)/omai': 'oi)=mai',
               'o)/lonqos': 'o)/lunqos', 'o)mi/xlh': 'o(mi/xlh', 'o)pta/zomai': 'o)pta/nomai', 'o)/rguia': 'o)rguia/',
               'o)rqreu/w': 'o)rqri/zw', 'ou)de/ pw,': 'ou)de/pw', 'ou)ra/noqen': 'ou)rano/qen',
               'o)fqalmodoulei/a': 'o)fqalmodouli/a', 'pandokeu/s': 'pandoxeu/s', 'panoikesi/a|': 'panoikei/',
               'pa/nourgos': 'panou=rgos', 'pantaxh=': 'pantaxh=|', 'paragi/gnomai': 'paragi/nomai',
               'parakaqi/zw': 'parakaqe/zw', 'pareisdu/nw': 'pareisdu/w', 'parqenei/a': 'parqeni/a',
               'paroiniko/s': 'pa/roinos', 'patraloi/as': 'patrolw/|as', 'pedieino/s': 'pedino/s',
               'perii/sthmi': 'perii/+sthmi', 'perikru/ptw': 'perikru/bw', 'perirrh/gnumi': 'perirh/gnumi',
               'pe/rnhmi': 'pipra/skw', 'piqano/s': 'peiqo/s', 'plh/mura': 'plh/mmura',
               'plo/os': 'plou=s', 'podapo/s': 'potapo/s', 'porfu/reos': 'porfurou=s',
               'pranh/s': 'prhnh/s', 'prau+pa/qeia': 'prau+pa/qia', 'progi/gnomai': 'progi/nomai',
               'progignw/skw': 'proginw/skw', 'pro/slhyis': 'pro/slhmyis', 'pro/sw': 'po/rrw', 'pro/swqen': 'po/rrwqen',
               'proswpolh/pths': 'proswpolh/mpths', 'proswpolhyi/a': 'proswpolhmyi/a', '*pu/qwn': 'pu/qwn',
               'pw=ma': 'po/ma', 'r(a/bdouxos': 'r(abdou=xos', 'r(oizhda/': 'r(oizhdo/n', 'r(upai/nw': 'r(upareu/w',
               '*sabbatismo/s': 'sabbatismo/s', '*sa/bbaton': 'sa/bbaton', 'salpigkth/s': 'salpisth/s',
               'sa/pfeiros': 'sa/pfiros', 'shmiki/nqion': 'simiki/nqion', 'sidh/reos': 'sidhrou=s',
               'sitometri/a': 'sitome/trion', 'sto/rnumi': 'strw/nnumi', 'sugklhro/nomos': 'sugklhrono/mos',
               'suke/a': 'sukh=', 'suko/moros': 'sukomore/a', 'sumparagi/gnomai': 'sumparagi/nomai',
               'sunanamei/gnumi': 'sunanami/gnumi', 'sunapoqnh/skw': 'sunapoqnh/|skw', 'tamiei=on': 'tamei=on',
               'taraxh/': 'ta/raxos', '*tartaro/w': 'tartaro/w', 'tekni/dion': 'tekni/on',
               'tessarakontaeth/s': 'tesserakontaeth/s', 'tetraplo/os': 'tetraplou=s', 'to/pazos': 'topa/zion',
               'tri/stegos': 'tri/stegon', '*tufwniko/s': 'tufwniko/s', 'u(pomimnh/skw': 'u(pomimnh/|skw',
               'u(posto/rnumi': 'u(postrwnnu/w', 'faino/lh': 'failo/nhs', 'filoniki/a': 'filoneiki/a',
               'filo/nikos': 'filo/neikos', 'fw/sforos': 'fwsfo/ros', 'xalkoli/banos': 'xalkoli/banon',
               'xei/maros': 'xei/marros', 'xeiro/grafos': 'xeiro/grafon', 'xh/ra': 'xh/ros',
               'xrewfeile/ths': 'xreofeile/ths', '<*> xrh=sis,': 'xrh=sis', 'yeudo/logos': 'yeudolo/gos',
               'yeudoma/rtus': 'yeudo/martus', 'ywmo/s': 'ywmi/on', 'w)di/s': 'w)di/n'}


def ascii_to_unicode(ascii_string):
    """Convert an ASCII representation of Greek to Unicode."""
    unicode = ascii_string
    for a, u in ASCII_UNICODE_MAPPING:
        if bool(re.search(a, unicode)):
            unicode = re.sub(a, u, unicode)
    return unicode


def process_entries():
    """Load the xml of the LSJ entries."""

    # Load the xml.
    dfs = list()
    for file in os.listdir(RAW_DATA_DIR + 'lsj/'):
        if file.startswith('grc'):
            with open(RAW_DATA_DIR + 'lsj/' + file) as lsj:
                soup = BeautifulSoup(lsj, features='xml')
                df = pd.DataFrame([(e['key'], e.orth.text,
                                    re.sub('[,.:]$', '',
                                           s.select_one('tr').text + ' ' + ascii_to_unicode(s.select_one('tr').find_next_sibling().text))
                                    if s.select_one('tr').find_next_sibling() is not None
                                       and s.select_one('tr').find_next_sibling().name == 'foreign'
                                       and s.select_one('tr').find_next_sibling()['lang'] == 'greek'
                                       and s.text[(s.text.find(s.select_one('tr').text) + len(s.select_one('tr').text)):].strip().startswith(s.select_one('tr').find_next_sibling().text)
                                    else re.sub('[,.:]$', '', s.select_one('tr').text))
                                   for e in soup.find_all('entryFree')
                                   for s in e.find_all('sense')
                                   if len(s.find_all('tr')) > 0],
                                  columns=['lemma_key', 'lemma_ascii', 'definition'])
                df = df[df.definition.str.len() > 0].drop_duplicates()
                dfs.append(df)
    xml_df = pd.concat(dfs)

    # Clean up lemmas.
    xml_df['lemma_ascii'] = xml_df.lemma_ascii.replace('[-^_:]', '', regex = True)
    xml_df['lemma_ascii'] = xml_df.lemma_ascii.replace(LEMMA_EDITS)

    # Get one definition for each lemma.
    xml_df = xml_df[['lemma_ascii', 'definition']]
    xml_df = xml_df.groupby(['lemma_ascii']).agg('; '.join)
    xml_df.reset_index(inplace=True)

    # Add lemmas and edit definitions.
    e_df = pd.concat([xml_df[~xml_df.lemma_ascii.isin(DEFINITION_EDITS.lemma_ascii)],
                      DEFINITION_EDITS,
                      SYNONYMS.merge(xml_df.rename({'lemma_ascii': 'synonym'}, axis=1)[['synonym', 'definition']],
                                     on=['synonym'])[['lemma_ascii', 'definition']]])

    # Covert ASCII to unicode.
    e_df['lemma'] = e_df['lemma_ascii'].apply(ascii_to_unicode)

    # Create a field without diacritics, for sorting.
    e_df['lemma_sort'] = e_df['lemma_ascii']
    e_df.lemma_sort = e_df.lemma_sort.replace({'[^abgdezhqiklmncoprstufxyw]': ''}, regex = True)
    e_df.lemma_sort = e_df.lemma_sort.replace(ASCII_UNICODE_ALPHABETIZATION_MAPPING,  regex = True)

    # Return the lemmas.
    return e_df


if __name__ == '__main__':

    # Get lexicon entries.
    pd.set_option('display.max_columns', None)
    entries_df = process_entries()

    # Connect to the database.
    connection = pymysql.connect(host='localhost', user='root', password=os.environ['MYSQL_PASSWORD'], database='gnt')

    # Get lemmas that are present in the NT.
    sql = "SELECT DISTINCT Lemma FROM words"
    nt_lemmas_df = pd.read_sql(sql, connection)
    entries_df = entries_df.merge(nt_lemmas_df, left_on=['lemma'], right_on=['Lemma'])

    # Write lemmas to the database.
    entries_list = list(entries_df[['lemma', 'lemma_sort', 'definition']].to_records(index=False))
    entries_list = [tuple(el) for el in entries_list]
    with connection.cursor() as cur:
        sql = """INSERT INTO lemmas
                 (Lemma, LemmaSort, ShortDefinition)
                 VALUES
                 (%s, %s, %s)"""
        cur.executemany(sql, entries_list)
    connection.commit()

    # Close the database connection.
    connection.close()
