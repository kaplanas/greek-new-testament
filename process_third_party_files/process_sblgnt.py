import pandas as pd
import numpy as np
import pymysql
import re
import unicodedata
import os
from xml.etree import ElementTree
from collections import defaultdict, Counter
from typing import Any, List, Dict

SBL_DIR = 'sblgnt'
SBL_FILES = ['01-matthew.xml', '02-mark.xml', '03-luke.xml', '04-john.xml', '05-acts.xml', '06-romans.xml',
             '07-1corinthians.xml', '08-2corinthians.xml', '09-galatians.xml', '10-ephesians.xml', '11-philippians.xml',
             '12-colossians.xml', '13-1thessalonians.xml', '14-2thessalonians.xml', '15-1timothy.xml',
             '16-2timothy.xml', '17-titus.xml', '18-philemon.xml', '19-hebrews.xml', '20-james.xml', '21-1peter.xml',
             '22-2peter.xml', '23-1john.xml', '24-2john.xml', '25-3john.xml', '26-jude.xml', '27-revelation.xml']
HEAD_EDITS = pd.read_csv(SBL_DIR + '/head_edits.csv',
                         dtype=defaultdict(lambda: str,
                                           {'chapter': np.float64, 'verse': np.float64, 'position': np.float64,
                                            'new_head_verse': np.float64, 'new_head_position': np.float64}))
CUTS = pd.read_csv(SBL_DIR + '/cuts.csv',
                   dtype=defaultdict(lambda: str,
                                     {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
CASE_EDITS = pd.read_csv(SBL_DIR + '/case_edits.csv',
                         dtype=defaultdict(lambda: str,
                                           {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
GENDER_EDITS = pd.read_csv(SBL_DIR + '/gender_edits.csv',
                           dtype=defaultdict(lambda: str,
                                             {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
POS_EDITS = pd.read_csv(SBL_DIR + '/pos_edits.csv', dtype=str)
LEMMA_EDITS = pd.read_csv(SBL_DIR + '/lemma_edits.csv', dtype=str)
AUTOS_FORMS = ['αὐτά', 'αὐτὰ', 'αὐταῖς', 'αὐτάς', 'αὐτὰς', 'αὐτὴ', 'αὐτῇ', 'αὐτήν', 'αὐτὴν', 'αὐτῆς', 'αὐτό', 'αὐτὸ',
               'Αὐτοὶ', 'αὐτοὶ', 'αὐτοί', 'αὐτοῖς', 'αὐτόν', 'αὐτὸν', 'αὐτός', 'αὐτὸς', 'Αὐτὸς', 'αὐτοῦ', 'αὐτούς',
               'αὐτοὺς', 'αὐτῷ', 'Αὐτῶν', 'αὐτῶν']
INDIVIDUAL_POS_EDITS = pd.read_csv(SBL_DIR + '/individual_pos_edits.csv',
                                   dtype=defaultdict(lambda: str,
                                                     {'chapter': np.float64, 'verse': np.float64,
                                                      'position': np.float64}))
GENITIVE_EDITS = pd.read_csv(SBL_DIR + '/genitive_edits.csv',
                             dtype=defaultdict(lambda: str,
                                               {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
DATIVE_EDITS = pd.read_csv(SBL_DIR + '/dative_edits.csv',
                           dtype=defaultdict(lambda: str,
                                             {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
ACCUSATIVE_EDITS = pd.read_csv(SBL_DIR + '/accusative_edits.csv',
                               dtype=defaultdict(lambda: str,
                                               {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
OTHER_RELATION_EDITS = pd.read_csv(SBL_DIR + '/other_relation_edits.csv',
                                   dtype=defaultdict(lambda: str,
                                                     {'chapter': np.float64, 'verse': np.float64,
                                                      'position': np.float64}))
RELATION_EDITS = {'genitive': GENITIVE_EDITS, 'dative': DATIVE_EDITS, 'accusative': ACCUSATIVE_EDITS,
                  'other': OTHER_RELATION_EDITS}
TYPE_EDITS = pd.read_csv(SBL_DIR + '/type_edits.csv',
                         dtype=defaultdict(lambda: str,
                                           {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))

BOOKS_OF_THE_BIBLE = ['Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor', 'Gal', 'Eph', 'Phil', 'Col',
                      '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb', 'Jas', '1Pet', '2Pet', '1John',
                      '2John', '3John', 'Jude', 'Rev']
PRETTY_BOOKS_OF_THE_BIBLE = ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians',
                             'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians',
                             '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James',
                             '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']
GREEK_CAPITALS = '^[' + ''.join(set(chr(cp)
                                    for cp in range(0x0370, 0x1FFF)
                                    if "GREEK CAPITAL" in unicodedata.name(chr(cp), ""))) + ']'
SECOND_POSITION_CLITICS = ['ἄρα', 'γάρ', 'γέ', 'δέ', 'μέν', 'μέντοι', 'οὖν', 'τέ']
SON_OF_WORDS = ['ἀδελφή', 'ἀδελφός', 'ἀνήρ', 'γυνή', 'θυγάτηρ', 'μήτηρ', 'πατήρ', 'τέκνον', 'υἱός']
SON_OF_POS = ['noun', 'personal pronoun', 'personal pronoun with kai', 'demonstrative pronoun',
              'demonstrative pronoun with kai', 'reflexive pronoun', 'interrogative pronoun', 'relative pronoun']
KEEP_DETERMINER_POS = ['noun', 'verb', 'adj', 'adv', 'adverb with kai', 'relative adverb', 'interrogative adverb',
                       'indefinite adverb', 'conj']
KEEP_DETERMINER_LEMMAS = ['Ἀθηναῖος', 'Ἀδραμυττηνός', 'Αἰγύπτιος', 'Ἀλεξανδρῖνος', 'Ἄλφα', 'Ἀσιανός', 'Ἀσιάρχης',
                          'Ἀχαϊκός', 'Βεροιαῖος', 'Γαδαρηνός', 'Γαλατικός', 'Γερασηνός', 'Δαμασκηνός', 'Δερβαῖος',
                          'Διάβολος', 'Ἑβραῖος', 'Ἐλαμίτης', 'Ἕλλην', 'Ἑλληνικός', 'Ἑλληνιστής', 'Ἐπικούρειος',
                          'Ἐφέσιος', 'Ζηλωτής', 'Ἡρῳδιανοί', 'Θάλασσα', 'Θεσσαλονικεύς', 'Ἱεροσολυμίτης', 'Ἰορδάνης',
                          'Ἰουδαϊκός', 'Ἰουδαῖος', 'Ἰταλικός', 'Ἰτουραῖος', 'Καναναῖος', 'Κορίνθιος', 'Κόρινθος',
                          'Κύπριος', 'Κυρηναῖος', 'Κυρήνιος', 'Λαοδικεύς', 'Λευίτης', 'Λευιτικός', 'Λιβερτῖνος',
                          'Μῆδος', 'Ναζαρηνός', 'Ναζωραῖος', 'Νινευίτης', 'Πάρθος', 'Ποντικός', 'Ῥωμαῖος',
                          'Σαδδουκαῖος', 'Σαμαρίτης', 'Σαμαρῖτις', 'Σεβαστός', 'Σιδώνιος', 'Σύρος', 'Συροφοινίκισσα',
                          'Τύριος', 'Φαρισαῖος', 'Φιλιππήσιος', 'Χαλδαῖος', 'Χαναναῖος', 'Χριστιανός', 'Χριστός', 'Ὦ']
NEGATION = ['μή', 'μήτι', 'οὐ', 'οὐκοῦν', 'οὐχί']
EXTENDED_NEGATION = ['μηδέ', 'μηδείς', 'οὐδαμῶς', 'οὐδέ', 'οὐδείς', 'οὐκέτι', 'οὔπω']
COPULA = ['εἰμί']
GENERAL_CONJUNCTIONS = ['ἀλλά', 'εἴτε', 'ἤ', 'ἤπερ', 'ἤτοι', 'καί', 'καίπερ', 'μηδέ', 'μήτε', 'οὐδέ', 'οὔπω', 'οὔτε',
                        'πλήν', 'ὡς', 'ὡσεί']
SENTENTIAL_CONJUNCTIONS = ['ἄρα', 'ἄχρι', 'διό', 'διότι', 'ἐάν', 'ἐάνπερ', 'εἰ', 'εἴπερ', 'ἐπάν', 'ἐπεί', 'ἐπειδή',
                           'ἕως', 'ἡνίκα', 'ἵνα', 'καθάπερ', 'καθό', 'καθότι', 'καθώς', 'κἄν', 'μέχρι(ς)', 'μήποτε',
                           'νή', 'ὁπότε', 'ὅπως', 'ὁσάκις', 'ὅταν', 'ὅτε', 'ὅτι', 'πρίν', 'ὥσπερ', 'ὥστε']
COORDINATING_CONJUNCTIONS = ['ἀλλά', 'εἴτε', 'ἤ', 'ἤτοι', 'καί', 'καίτοι', 'μηδέ', 'μήτε', 'οὐδέ', 'οὔτε', 'πλήν']
BURIED_CONJUNCTIONS = ['ἄχρι', 'διότι', 'ἐάν', 'ἐάνπερ', 'εἰ', 'εἴπερ', 'ἐπάν', 'ἐπεί', 'ἐπειδή', 'ἕως', 'ἡνίκα', 'ἵνα',
                       'καθάπερ', 'καθό', 'καθότι', 'καθώς', 'κἄν', 'μέχρι(ς)', 'μήποτε', 'νή', 'ὁπότε', 'ὅπως',
                       'ὁσάκις', 'ὅταν', 'ὅτε', 'πρίν', 'ὥσπερ', 'ὥστε']
ADVERB_CONJUNCTIONS = ['καί', 'μηδέ', 'μήτε', 'οὐδέ', 'οὔπω', 'οὔτε']
PARTITIVE_HEADS = ['δύο', 'εἷς', 'ἕκαστος', 'τίς', 'τις', 'οὐδείς', 'πᾶς']
PARTITIVE_PS = ['ἀπό', 'ἐκ', 'ἐν']
SENTENTIAL_COMPLEMENT_HEADS = ['ἀγνοέω', 'ἀκούω', 'ἀναγγέλλω', 'ἀναγινώσκω', 'ἀποκρίνομαι', 'ἀπολογέομαι', 'ἀρνέομαι',
                               'βοάω', 'γινώσκω', 'γνωρίζω', 'γνωστός', 'γράφω', 'δείκνυμι', 'δέω', 'δῆλος',
                               'διαλογίζομαι', 'διαμαρτύρομαι', 'διδάσκω', 'δοκέω', 'ἐλπίζω', 'ἐντέλλομαι',
                               'ἐξομολογέω', 'ἐπερωτάω', 'ἐπιγινώσκω', 'ἐπίσταμαι', 'ἐπιτάσσω', 'ἐρωτάω', 'θεάομαι',
                               'θέλω', 'θεωρέω', 'καταλαμβάνω', 'λαλέω', 'λέγω', 'λογίζομαι', 'μαρτυρέω', 'μαρτύρομαι',
                               'μιμνῄσκομαι', 'μνημονεύω', 'νοέω', 'νομίζω', 'οἶδα', 'οἶμαι', 'ὀμνύω', 'ὁμολογέω',
                               'ὁράω', 'πείθω', 'πιστεύω', 'πληροφορέω', 'πρόδηλος', 'προευαγγελίζομαι', 'προλέγω',
                               'προοράω', 'προφητεύω', 'συμβιβάζω', 'συμβουλεύω', 'συμμαρτυρέω', 'συνίημι',
                               'ὑποδείκνυμι', 'φανερόω', 'φημί']
INFINITIVE_ARGUMENT_HEADS = ['ἀγωνίζομαι', 'αἰτέω', 'ἀναγκάζω', 'αἱρέομαι', 'αἰσχύνομαι', 'ἀπαγγέλλω', 'ἀναμιμνῄσκω',
                             'ἀναπείθω', 'ἀξιόω', 'ἀπαρνέομαι', 'ἀπειλέω', 'ἀποκρίνομαι', 'ἀρνέομαι', 'ἄρχω', 'ἀφίημι',
                             'βοάω', 'βούλομαι', 'γινώσκω', 'δείκνυμι', 'δέομαι', 'δέω', 'δηλόω', 'διαμαρτύρομαι',
                             'διατάσσω', 'διδάσκω', 'διϊσχυρίζομαι', 'δοκέω', 'δύναμαι', 'δυνατέω', 'ἐάω', 'ἐγκόπτω',
                             'εἴωθα', 'ἐκλέγομαι', 'ἐλπίζω', 'ἐνεδρεύω', 'ἐνορκίζω', 'ἐντέλλομαι', 'ἐξαιτέομαι',
                             'ἐξαπορέομαι', 'ἐξισχύω', 'ἐπαγγέλλομαι', 'ἐπαισχύνομαι', 'ἐπερωτάω', 'ἐπιδείκνυμι',
                             'ἐπιζητέω', 'ἐπιθυμέω', 'ἐπικρίνω', 'ἐπιλανθάνομαι', 'ἐπιμαρτυρέω', 'ἐπιποθέω',
                             'ἐπισκέπτομαι', 'ἐπιτάσσω', 'ἐπιτελέω', 'ἐπιτίθημι', 'ἐπιτρέπω', 'ἐπιχειρέω', 'ἐρωτάω',
                             'ἑτοιμάζω', 'εὐδοκέω', 'εὐκαιρέω', 'εὔχομαι', 'ἐφοράω', 'ζητέω', 'ἡγέομαι', 'θέλω',
                             'ἰσχύω', 'κατακρίνω', 'καταλαμβάνω', 'καταλείπω', 'κατανεύω', 'καταξιόω', 'καταπαύω',
                             'κατασείω', 'κατισχύω', 'κελεύω', 'κηρύσσω', 'κινδυνεύω', 'κρίνω', 'κωλύω', 'λαγχάνω',
                             'λέγω', 'λογίζομαι', 'μανθάνω', 'μαρτυρέω', 'μέλλω', 'νεύω', 'νοέω', 'νομίζω', 'οἶδα',
                             'οἶμαι', 'ὀκνέω', 'ὀμνύω', 'ὁμολογέω', 'ὁρίζω', 'ὀφείλω', 'παραγγέλλω', 'παραδίδωμι',
                             'παραινέω', 'παραιτέομαι', 'παρακαλέω', 'πείθω', 'πειράζω', 'πειράω', 'ποιέω',
                             'προαιτιάομαι', 'προμελετάω', 'προσδοκάω', 'προενάρχομαι', 'προσέχω', 'προσκαλέομαι',
                             'προστάσσω', 'προστίθημι', 'προτίθεμαι', 'σημαίνω', 'σπουδάζω', 'συμβουλεύω', 'συνευδοκέω',
                             'συντίθεμαι', 'τάσσω', 'τολμάω', 'ὑποδείκνυμι', 'ὑποκρίνομαι', 'ὑπονοέω', 'φάσκω', 'φημί',
                             'φιλέω', 'φιλοτιμέομαι', 'φοβέομαι', 'χαρίζομαι', 'χρηματίζω', 'χρονίζω']
FIRST_DECLENSION = ['Γολγοθᾶ', 'Κεγχρεαί', 'Κολοσσαί', 'μνᾶ', 'Συράκουσαι']
FIRST_SECOND_DECLENSION = ['Ἀθῆναι', 'ἀλλήλων', 'ἀμφότεροι', 'διακόσιοι', 'δισχίλιοι', 'ἑαυτοῦ', 'ἐμαυτοῦ',
                           'ἑπτακισχίλιοι', 'Ἡρῳδιανοί', 'μύριοι', 'ὅδε', 'πεντακισχίλιοι', 'πεντακόσιοι', 'πορφυροῦς',
                           'σεαυτοῦ', 'σιδηροῦς', 'τετρακισχίλιοι', 'τετρακόσιοι', 'τετραπλοῦς', 'τοιόσδε',
                           'τριακόσιοι', 'τρισχίλιοι', 'χαλκοῦς', 'χίλιοι', 'χρυσοῦς']
SECOND_DECLENSION = ['ἀγενεαλόγητος', 'ἄγναφος', 'ἄγνωστος', 'ἀγοραῖος', 'ἀγράμματος', 'ἀδάπανος', 'ἄδηλος',
                     'ἀδιάκριτος', 'ἀδιάλειπτος', 'ἄδικος', 'ἀδόκιμος', 'ἄδολος', 'ἀδύνατος', 'ἄζυμος', 'ἀθέμιτος',
                     'ἄθεος', 'ἄθεσμος', 'ἀθῷος', 'ἀΐδιος', 'αἰφνίδιος', 'αἰώνιος', 'ἀκάθαρτος', 'ἄκακος', 'ἄκαρπος',
                     'ἀκατάγνωστος', 'ἀκατακάλυπτος', 'ἀκατάκριτος', 'ἀκατάλυτος', 'ἀκατάπαυστος', 'ἀκατάστατος',
                     'ἀκέραιος', 'ἄκρατος', 'ἀκρογωνιαῖος', 'ἀλάλητος', 'ἄλαλος', 'ἀλλόφυλος', 'ἄλογος', 'ἀλυπότερος',
                     'ἀμάραντος', 'ἀμάρτυρος', 'ἁμαρτωλός', 'ἄμαχος', 'ἄμεμπτος', 'ἀμέριμνος', 'ἀμετάθετος',
                     'ἀμετακίνητος', 'ἀμεταμέλητος', 'ἀμετανόητος', 'ἄμετρος', 'ἀμίαντος', 'ἀμώμητος', 'ἄμωμος',
                     'ἀναίτιος', 'ἄναλος', 'ἀναμάρτητος', 'ἀναντίρρητος', 'ἀνάξιος', 'ἀνάπηρος', 'ἀναπολόγητος',
                     'ἀναρίθμητος', 'ἀνδροφόνος', 'ἀνέγκλητος', 'ἀνεκδιήγητος', 'ἀνεκλάλητος', 'ἀνέκλειπτος', 'ἀνέλεος',
                     'ἀνένδεκτος', 'ἀνεξεραύνητος', 'ἀνεξίκακος', 'ἀνεξιχνίαστος', 'ἀνεπαίσχυντος', 'ἀνεπίλημπτος',
                     'ἀνεύθετος', 'ἀνήμερος', 'ἀνθρωπάρεσκος', 'ἄνιπτος', 'ἀνόητος', 'ἄνομος', 'ἀνόσιος', 'ἀντίτυπος',
                     'ἄνυδρος', 'ἀνυπόκριτος', 'ἀνυπότακτος', 'ἀόρατος', 'ἀπαίδευτος', 'ἀπαράβατος', 'ἀπαρασκεύαστος',
                     'ἀπείραστος', 'ἄπειρος', 'ἀπελεύθερος', 'ἀπέραντος', 'ἀπερίτμητος', 'ἄπιστος', 'ἀπόδεκτος',
                     'ἀπόδημος', 'ἀπόκρυφος', 'ἀποσυνάγωγος', 'ἀπρόσιτος', 'ἀπρόσκοπος', 'ἄπταιστος', 'ἄραφος', 'ἀργός',
                     'ἀργυροῦς', 'ἄρρητος', 'ἄρρωστος', 'ἀρτιγέννητος', 'ἀσάλευτος', 'ἄσβεστος', 'ἄσημος', 'ἄσιτος',
                     'ἄσοφος', 'ἄσπιλος', 'ἄσπονδος', 'ἀστήρικτος', 'ἄστοργος', 'ἀσύμφωνος', 'ἀσύνετος', 'ἀσύνθετος',
                     'ἄτακτος', 'ἄτεκνος', 'ἄτιμος', 'ἄτομος', 'ἄτοπος', 'αὐθαίρετος', 'αὐτοκατάκριτος', 'αὐτόφωρος',
                     'ἄφαντος', 'ἄφθαρτος', 'ἀφιλάγαθος', 'ἀφιλάργυρος', 'ἄφωνος', 'ἀχάριστος', 'ἀχειροποίητος',
                     'ἀχρεῖος', 'ἄχρηστος', 'βάρβαρος', 'βαρύτιμος', 'βασίλειος', 'βέβηλος', 'βλαβερός', 'βλάσφημος',
                     'βλητέος', 'βοηθός', 'βρώσιμος', 'Διάβολος', 'διάβολος', 'διάφορος', 'διθάλασσος', 'δίλογος',
                     'Διόσκουροι', 'δίστομος', 'δίψυχος', 'δόκιμος', 'δυσβάστακτος', 'δυσερμήνευτος', 'δύσκολος',
                     'δυσνόητος', 'ἔγγυος', 'ἐγκάθετος', 'ἔγκυος', 'εἰδωλόθυτος', 'εἰρηνοποιός', 'ἔκγονος', 'ἔκδηλος',
                     'ἔκδικος', 'ἔκδοτος', 'ἔκθαμβος', 'ἔκθετος', 'ἔκφοβος', 'ἔμφοβος', 'ἔμφυτος', 'ἔνδικος', 'ἔνδοξος',
                     'ἔννομος', 'ἔννυχος', 'ἔνοχος', 'ἔντιμος', 'ἐντόπιος', 'ἔντρομος', 'ἑξακόσιοι', 'ἔξυπνος',
                     'ἐπάρατος', 'ἐπίγειος', 'ἐπιθανάτιος', 'ἐπικατάρατος', 'ἐπίλοιπος', 'ἐπίορκος', 'ἐπιούσιος',
                     'ἐπιπόθητος', 'ἐπίσημος', 'ἐπουράνιος', 'ἔρημος', 'ἑτερόγλωσσος', 'εὐάρεστος', 'εὔθετος',
                     'εὔθυμος', 'εὔκαιρος', 'εὐκοπώτερος', 'εὐμετάδοτος', 'εὐπάρεδρος', 'εὐπερίστατος', 'εὐπρόσδεκτος',
                     'εὐρύχωρος', 'εὔσημος', 'εὔσπλαγχνος', 'εὔφημος', 'εὐχάριστος', 'εὔχρηστος', 'εὐώνυμος',
                     'ἐφήμερος', 'ἤρεμος', 'ἡσύχιος', 'θανατηφόρος', 'θεοδίδακτος', 'θεομάχος', 'θεόπνευστος',
                     'ἱερόθυτος', 'ἱερόσυλος', 'ἰσάγγελος', 'ἰσότιμος', 'ἰσόψυχος', 'κακοῦργος', 'καλοδιδάσκαλος',
                     'καρποφόρος', 'κατάδηλος', 'κατάλαλος', 'κατάλοιπος', 'καταχθόνιος', 'κατείδωλος', 'κενόδοξος',
                     'κόσμιος', 'λιθόστρωτος', 'μακροχρόνιος', 'ματαιολόγος', 'μεμψίμοιρος', 'μέτοχος', 'μογιλάλος',
                     'μονόφθαλμος', 'νεόφυτος', 'νήπιος', 'νηφάλιος', 'οἰκουργός', 'ὀκταήμερος', 'ὀλιγόπιστος',
                     'ὀλιγόψυχος', 'ὁλόκληρος', 'ὁμότεχνος', 'ὀστράκινος', 'ὄψιμος', 'πανοῦργος', 'παράδοξος',
                     'παράλιος', 'παράσημος', 'παρείσακτος', 'παρεπίδημος', 'πάροικος', 'πάροινος', 'παρόμοιος',
                     'πατροπαράδοτος', 'περίεργος', 'περίλυπος', 'περίοικος', 'περιούσιος', 'περίχωρος', 'πολυποίκιλος',
                     'πολύσπλαγχνος', 'πολύτιμος', 'ποταμοφόρητος', 'Ποτίολοι', 'πρόγονος', 'πρόδηλος', 'πρόδρομος',
                     'πρόθυμος', 'πρόϊμος', 'πρόσκαιρος', 'πρόσπεινος', 'πρόσφατος', 'πρωϊνός', 'πρωτότοκος',
                     'σητόβρωτος', 'σκληροτράχηλος', 'σκυθρωπός', 'σκῦλα', 'σκωληκόβρωτος', 'σπερμολόγος', 'σπόριμος',
                     'στυγητός', 'συνεργός', 'συγκληρονόμος', 'σύζυγος', 'συμμέτοχος', 'σύμμορφος', 'σύμφορος',
                     'σύμφυτος', 'σύμφωνος', 'σύμψυχος', 'σύντροφος', 'σύσσωμος', 'σωτήριος', 'ταλαίπωρος',
                     'τετράγωνος', 'τετράμηνος', 'τρίμηνος', 'ὕπανδρος', 'ὑπέρακμος', 'ὑπερήφανος', 'ὑπέρογκος',
                     'ὑπήκοος', 'ὑπόδικος', 'φιλάγαθος', 'φιλάδελφος', 'φίλανδρος', 'φιλάργυρος', 'φίλαυτος',
                     'φιλήδονος', 'Φίλιπποι', 'φιλόθεος', 'φιλόνεικος', 'φιλόξενος', 'φιλόστοργος', 'φιλότεκνος',
                     'φλύαρος', 'φρόνιμος', 'φωσφόρος', 'χειροποίητος', 'χρυσοδακτύλιος', 'ψευδολόγος', 'ψευδώνυμος',
                     'ὠφέλιμος']
THIRD_DECLENSION_CONSONANT_STEM = ['ἅλας', 'ἄρσην', 'γάλα', 'γέλως', 'γόης', 'Δάμαρις', 'δεκατέσσαρες', 'δισμυριάς',
                                   'Δορκάς', 'Ἑβραΐς', 'Ἐλαιῶν', 'Ἑλλάς', 'Ἕλλην', 'ἐσθής', 'Ἡρῳδιάς', 'ἱδρώς', 'ἰκμάς',
                                   'ἱμάς', 'ἶρις', 'Ἰωσῆς', 'Καῖσαρ', 'κέρας', 'Κλήμης', 'Κρής', 'λαμπάς', 'Λιμήν',
                                   'λιμήν', 'Λωΐς', 'μεγιστάν', 'μέλαν', 'μέλι', 'μήν', 'μυριάς', 'ὄρνις', 'οὖς',
                                   'παῖς', 'πέρας', 'πετρῶδες', 'πλήρης', 'ποιμήν', 'Πούδης', 'πρεσβῦτις', 'προφῆτις',
                                   'Πτολεμαΐς', 'πῦρ', 'Σαμαρῖτις', 'σής', 'Σολομῶν', 'σπιλάς', 'στιβάς', 'τέρας',
                                   'τέσσαρες', 'Τιβεριάς', 'τις', 'Τραχωνῖτις', 'Τρῳάς', 'φρέαρ', 'φρήν', 'φῶς',
                                   'χιλιάς', 'χλαμύς', 'χρώς', 'ψευδόμαρτυς', 'ὠδίν']
THIRD_DECLENSION_VOWEL_STEM = ['ἀβαρής', 'ἀγενής', 'αἰδώς', 'αἰσχροκερδής', 'ἀκλινής', 'ἀκρατής', 'ἀκριβής', 'ἀληθής',
                               'ἀλλογενής', 'ἀλυσιτελής', 'ἀμαθής', 'ἀνωφελής', 'ἀπειθής', 'ἁπλοῦς', 'ἀσεβής',
                               'ἀσθενής', 'αὐτάρκης', 'ἀσφαλής', 'αὐθάδης', 'ἀφανής', 'ἀψευδής', 'βοῦς', 'γῆρας',
                               'γραώδης', 'δαιμονιώδης', 'δάκρυον', 'διαυγής', 'διετής', 'διηνεκής', 'διοπετής',
                               'διπλοῦς', 'ἐγκρατής', 'εἰλικρινής', 'ἑκατονταετής', 'ἐκτενής', 'ἐμφανής', 'ἐνδεής',
                               'ἐνεργής', 'ἐπιεικής', 'ἐπισφαλής', 'ἐπιφανής', 'εὐγενής', 'εὐλαβής', 'εὐπειθής',
                               'εὐσεβής', 'ἡμιθανής', 'θειώδης', 'θεοσεβής', 'θεοστυγής', 'ἱεροπρεπής', 'κρέας',
                               'μεγαλοπρεπής', 'μονογενής', 'ναῦς', 'νοῦς', 'ὁλοτελής', 'ὁμοιοπαθής', 'ὀσφῦς', 'ὀφρῦς',
                               'παντελής', 'πένης', 'περικρατής', 'πλοῦς', 'πολυτελής', 'πραΰς', 'πρηνής', 'προπετής',
                               'προσφιλής', 'σίναπι', 'συγγενής', 'συμπαθής', 'ταχύ', 'ταχύς', 'τεσσερακονταετής',
                               'ὑγιής', 'ὗς', 'χοῦς', 'ψευδής']
UNDECLINED_NOUNS = ['Ἀαρών', 'Ἀβαδδών', 'αββα', 'Ἀβιά', 'Αἰνών', 'Ἄλφα', 'Ἁρμαγεδών', 'Ἀσήρ', 'Βηθσαϊδά', 'Βόος',
                    'Γαββαθα', 'Γεδεών', 'Δαλμανουθά', 'δεῖνα', 'Ζαβουλών', 'Ζάρα', 'Θάρα', 'ἵλεως', 'Ἰωδά', 'ἰῶτα',
                    'Καῦδα', 'Κεδρών', 'Κίς', 'Λευίς', 'Μαθουσαλά', 'Μαναήν', 'μάννα', 'μαράνα', 'Ματταθά', 'Μελεά',
                    'Μεννά', 'Μύρα', 'Ναασσών', 'Ναζαρά', 'πάσχα', 'Πάταρα', 'ῥακά', 'Ῥαμά', 'Ῥησά', 'Σαλά', 'Σαλμών',
                    'Σαμψών', 'Σάρεπτα', 'σίκερα', 'Σιών', 'Συμεών', 'Ταβιθά', 'ταλιθα']
IRREGULAR_NOUNS = ['ἄκων', 'ἀνήρ', 'Ἀντιπᾶς', 'ἅπας', 'Ἀπολλῶς', 'Ἁρέτας', 'ἀρήν', 'Ἀρτεμᾶς', 'ἀρχιποίμην', 'αὐτόχειρ',
                   'Βαριησοῦς', 'Βαρναβᾶς', 'βορρᾶς', 'γαστήρ', 'γόνυ', 'γυνή', 'Δημᾶς', 'δύο', 'εἷς', 'ἑκών', 'Ἐλύμας',
                   'Ἐπαφρᾶς', 'Ἑρμᾶς', 'Ζεύς', 'Ζηνᾶς', 'Θευδᾶς', 'θυγάτηρ', 'Ἱεροσόλυμα', 'Ἰωνᾶς', 'Καϊάφας', 'Κλωπᾶς',
                   'Κώς', 'Λευί', 'Λουκᾶς', 'μαμωνᾶς', 'Μανασσῆς', 'μέγας', 'μέλας', 'μηδείς', 'μήτηρ', 'Μωϋσῆς',
                   'Νύμφας', 'Ὀλυμπᾶς', 'ὄναρ', 'οὐδείς', 'Παρμενᾶς', 'πᾶς', 'πατήρ', 'ποδήρης', 'πολύς', 'πούς',
                   'σάββατον', 'Σατανᾶς', 'Σίλας', 'Σιλᾶς', 'Σκευᾶς', 'Στεφανᾶς', 'Σωσθένης', 'τετράπους', 'Τρεῖς',
                   'τρεῖς', 'χείρ', 'Χουζᾶς']
NUMBERS = ['εἷς', 'τρεῖς', 'τέσσαρες', 'διακόσιοι', 'τριακόσιοι', 'τετρακόσιοι', 'πεντακόσιοι', 'ἑξακόσιοι', 'χίλιοι',
           'χιλιάς', 'δισχίλιοι', 'τρισχίλιοι', 'τετρακισχίλιοι', 'πεντακισχίλιοι']
TITLES = ['ἀνθύπατος', 'βασιλεύς', 'δυνάστης', 'ἡγεμών', 'Καῖσαρ', 'κύριος', 'πατριάρχης', 'προφήτης', 'Χριστός']


class UncutSentence:

    # Initialize the sentence from an XML parse from the SBLGNT file.
    def __init__(self, sbl_tree):

        # Citation, full text, and tree.
        self.citation = sbl_tree[0].text
        self.text = sbl_tree[1].text
        if self.citation == 'John.8.7':
            self.text = 'ὡς δὲ ἐπέμενον ἐρωτῶντες αὐτόν, ἀνακύψας εἶπεν πρὸς αὐτούς Ὁ ἀναμάρτητος ὑμῶν πρῶτον ἐπ’ αὐτὴν τὸν λίθον βαλέτω'
        elif self.citation == 'John.8.9':
            self.text = 'οἱ δὲ ἀκούσαντες καὶ ὑπὸ τῆς συνειδήσεως ἐλεγχόμενοι ἐξήρχοντο εἷς καθ’ εἷς ἀρξάμενοι ἀπὸ τῶν πρεσβυτέρων, καὶ κατελείφθη μόνος, ὁ Ἰησοῦς καὶ ἡ γυνὴ ἐν μέσῳ οὖσα.'
        elif self.citation == '1Cor.12.8':
            self.text = 'ᾧ μὲν γὰρ διὰ τοῦ πνεύματος δίδοται λόγος σοφίας, ἄλλῳ δὲ λόγος γνώσεως κατὰ τὸ αὐτὸ πνεῦμα, ἑτέρῳ πίστις ἐν τῷ αὐτῷ πνεύματι, ἄλλῳ χαρίσματα ἰαμάτων ἐν τῷ ἑνὶ πνεύματι, ἄλλῳ ἐνεργήματα δυνάμεων, ⸁ἄλλῳ προφητεία, ἄλλῳ διακρίσεις πνευμάτων, ἑτέρῳ γένη γλωσσῶν, 2ἄλλῳ ἑρμηνεία γλωσσῶν·'
        elif self.citation == '2Cor.7.12':
            self.text = 'ἄρα εἰ καὶ ἔγραψα ὑμῖν, οὐχ ἕνεκεν τοῦ ἀδικήσαντος, οὐδὲ ⸁ἕνεκεν τοῦ ἀδικηθέντος, ἀλλ’ ἕνεκεν τοῦ φανερωθῆναι τὴν σπουδὴν ὑμῶν τὴν ὑπὲρ ἡμῶν πρὸς ὑμᾶς ἐνώπιον τοῦ θεοῦ.'
        elif self.text == 'τί γάρ; εἰ ἠπίστησάν τινες,':
            self.text = 'τί γάρ εἰ ἠπίστησάν τινες,'
        elif self.citation == 'John.8.3':
            self.text = 'ἄγουσιν δὲ οἱ γραμματεῖς καὶ οἱ Φαρισαῖοι πρὸς αὐτὸν γυναῖκα ἐν μοιχείᾳ καταλήφθεισαν καὶ στήσαντες αὐτὴν ἐν μέσῳ λέγουσιν αὐτῷ, πειράζοντες Διδάσκαλε, αὕτη ἡ γυνὴ κατελήφθη ἐπ’ αὐτοφόρῳ μοιχευομένη·'
        elif self.citation == 'Acts.13.43':
            self.text = 'λυθείσης δὲ τῆς συναγωγῆς ἠκολούθησαν πολλοὶ τῶν Ἰουδαίων καὶ τῶν σεβομένων προσηλύτων τῷ Παύλῳ καὶ τῷ Βαρναβᾷ, οἵτινες προσλαλοῦντες αὐτοῖς ἔπειθον αὐτοὺς προσμένειν τῇ χάριτι τοῦ θεοῦ.'
        elif self.citation == 'John.1.3':
            self.text = 'πάντα δι’ αὐτοῦ ἐγένετο, καὶ χωρὶς αὐτοῦ ἐγένετο οὐδὲ ἕν ὃ γέγονεν.'
        self.tree = sbl_tree[2]

        # Initialize the list of words.
        self.words = []

        # Counter for missing node IDs.
        missing_node_id = 1

        # Walk down the tree and get all the nodes.  Add pointers to parents, children, and heads.
        self.nodes = dict()
        path_to_node = []
        node_stack = [self.tree]
        while len(node_stack) > 0:
            node = node_stack[-1]
            if len(path_to_node) > 0 and node is path_to_node[-1]:
                path_to_node.pop()
                node_stack.pop()
                node_dict: dict[str, Any] = node.attrib
                if 'head' in node_dict:
                    node_dict['is_head'] = True
                else:
                    node_dict['is_head'] = False
                node_dict['tag'] = node.tag
                node_dict['text'] = node.text
                if 'osisId' in node_dict:
                    reference_parts = re.split('[.!]', node_dict['osisId'])
                    node_dict['book'] = reference_parts[0]
                    node_dict['chapter'] = int(reference_parts[1])
                    node_dict['verse'] = int(reference_parts[2])
                    node_dict['position'] = int(reference_parts[3])
                if len(path_to_node) > 0:
                    if 'n' not in path_to_node[-1].attrib:
                        path_to_node[-1].attrib['n'] = str(missing_node_id)
                        missing_node_id += 1
                    node_dict['parent_n'] = path_to_node[-1].attrib['n']
                    if len(path_to_node[-1]) == 1:
                        node_dict['is_head'] = True
                if 'n' not in node.attrib:
                    node.attrib['n'] = str(missing_node_id)
                    missing_node_id += 1
                self.nodes[node.attrib['n']] = node_dict
            else:
                path_to_node += [node]
                for child in reversed(node):
                    node_stack += [child]

        # Add a pointer to each node's head child.
        for key, node in self.nodes.items():
            if node['is_head']:
                self.nodes[node['parent_n']]['head_child_n'] = key

        # Various edits.
        #   - Some nodes have no head child.  In these cases, call the first child the head.
        #   - Copula verbs are consistently not coded as heads.  I want them to be heads.
        #   - Objects of prepositions are consistently not coded as heads.  I want them to be heads.
        #   - In conjoined phrases, the first conjoined element is usually coded as the head.  I want the conjunction
        #     itself to be the head.
        for key, node in self.nodes.items():
            if node['tag'] != 'w' and 'head_child_n' not in node:
                all_children = [(n['position'], k)
                                for k, n in self.nodes.items() if 'parent_n' in n and n['parent_n'] == key]
                all_children = sorted(all_children)
                node['head_child_n'] = all_children[0][1]
                self.nodes[all_children[0][1]]['is_head'] = True
            if 'role' in node and node['role'] == 'vc':
                node['is_head'] = True
                self.nodes[node['parent_n']]['head_child_n'] = key
                for k, n in self.nodes.items():
                    if 'parent_n' in n and n['parent_n'] == node['parent_n'] and k != key:
                        n['is_head'] = False
            if ('class' in node and node['class'] == 'prep') or \
                    ('lemma' in node and node['lemma'] in GENERAL_CONJUNCTIONS and
                     not (node['class'] == 'adv' and node['lemma'] in ADVERB_CONJUNCTIONS) and
                     ('role' not in node or node['role'] != 'adv') and
                     node['position'] == min(n['position']
                                             for k, n in self.nodes.items()
                                             if 'lemma' in n and n['lemma'] in GENERAL_CONJUNCTIONS and
                                                not (n['class'] == 'adv' and n['lemma'] in ADVERB_CONJUNCTIONS) and
                                                ('role' not in n or n['role'] != 'adv') and
                                                'position' in n and n['parent_n'] == node['parent_n'])) or \
                    ('lemma' in node and node['lemma'] in SENTENTIAL_CONJUNCTIONS and
                     (node['class'] in ['conj', 'ptcl'] or node['lemma'] in ['κἄν', 'ἵνα', 'ὅτι'])):
                sentential_complement = False
                if node['lemma'] == 'ὅτι':
                    if 'parent_n' in node and 'parent_n' in self.nodes[node['parent_n']]:
                        if 'role' in self.nodes[node['parent_n']] and self.nodes[node['parent_n']]['role'] == 's':
                            sentential_complement = True
                        else:
                            grandparent = self.nodes[self.nodes[node['parent_n']]['parent_n']]
                            head = self.nodes[grandparent['head_child_n']]
                            while 'head_child_n' in head:
                                head = self.nodes[head['head_child_n']]
                            if 'lemma' in head and head['lemma'] in SENTENTIAL_COMPLEMENT_HEADS:
                                sentential_complement = True
                node['is_head'] = True
                self.nodes[node['parent_n']]['head_child_n'] = key
                for k, n in self.nodes.items():
                    if 'parent_n' in n and n['parent_n'] == node['parent_n'] and k != key:
                        n['is_head'] = False
                if (node['lemma'] in BURIED_CONJUNCTIONS and
                    (node['class'] in ['conj', 'ptcl'] or node['lemma'] in ['κἄν', 'ἵνα', 'ὅτι'])) or \
                        (node['lemma'] == 'ὅτι' and not sentential_complement):
                    self.nodes[node['parent_n']]['is_head'] = True
                    self.nodes[self.nodes[node['parent_n']]['parent_n']]['head_child_n'] = node['parent_n']
                    for k, n in self.nodes.items():
                        if 'parent_n' in n and n['parent_n'] == self.nodes[node['parent_n']]['parent_n'] and \
                              k != node['parent_n']:
                            n['is_head'] = False

        # (We have to do these things in a separate loop because prepositions aren't reliably heads until the previous
        # loop finishes.)
        #   - Partitives are consistently coded with the genitive or PP as the head; I want the noun to be the head.
        #   - Determiners of nounless PPs are consistently coded as heads; I want the PP to be the head.
        for key, node in self.nodes.items():
            if 'lemma' in node and node['lemma'] in PARTITIVE_HEADS and 'parent_n' in node and \
                    self.nodes[node['parent_n']]['class'] != 'pp':
                possible_fake_head = self.nodes[node['parent_n']]
                while 'head_child_n' in possible_fake_head:
                    possible_fake_head = self.nodes[possible_fake_head['head_child_n']]
                possible_fake_head_case = None
                if 'case' in possible_fake_head:
                    possible_fake_head_case = possible_fake_head['case']
                if 'lemma' in possible_fake_head and possible_fake_head['lemma'] in GENERAL_CONJUNCTIONS:
                    for k, n in self.nodes.items():
                        if 'parent_n' in n and n['parent_n'] == possible_fake_head['parent_n'] and \
                                k != possible_fake_head['n']:
                            possible_fake_head_conjunct = n
                            while 'head_child_n' in possible_fake_head_conjunct:
                                possible_fake_head_conjunct = self.nodes[possible_fake_head_conjunct['head_child_n']]
                            if 'case' in possible_fake_head_conjunct:
                                possible_fake_head_case = possible_fake_head_conjunct['case']
                            break
                if ('lemma' in possible_fake_head and possible_fake_head['lemma'] in PARTITIVE_PS) or \
                        ((possible_fake_head_case == 'genitive' or possible_fake_head['class'] == 'num') and
                         'case' in node and node['case'] != 'genitive'):
                    possible_fake_head['relation'] = 'genitive, part-whole'
                    self.nodes[self.nodes[node['parent_n']]['head_child_n']]['is_head'] = False
                    self.nodes[node['parent_n']]['head_child_n'] = key
                    node['is_head'] = True
            if 'class' in node and node['class'] == 'det' and node['is_head']:
                for k, n in self.nodes.items():
                    if 'parent_n' in n and n['parent_n'] == node['parent_n'] and k != key:
                        self.nodes[node['parent_n']]['head_child_n'] = k
                        n['is_head'] = True
                        node['is_head'] = False
                        break

        # Propagate nodes' roles to their head children.  Make some edits along the way.
        #   - If we find a phrase whose role is "predicate", send that role all the way down to the lowest head.
        #   - Overwrite verbs' roles, except for some participles.
        path_to_node = []
        node_stack = [(k, n) for k, n in self.nodes.items() if 'parent_n' not in n]
        while len(node_stack) > 0:
            node = node_stack[-1]
            if len(path_to_node) > 0 and node is path_to_node[-1]:
                path_to_node.pop()
                node_stack.pop()
            else:
                path_to_node += [node]
                for child in reversed([(k2, n2) for k2, n2 in self.nodes.items()
                                       if 'parent_n' in n2 and n2['parent_n'] == node[0]]):
                    if 'head_child_n' in node[1] and node[1]['head_child_n'] == child[0] and \
                            'role' in node[1] and ('role' not in child[1] or node[1]['role'] in ['p', 'adv'] or
                                                   (child[1]['role'] == 'v' and
                                                    not ('mood' in child[1] and child[1]['mood'] == 'participle' and
                                                         node[1]['role'] != 's')) or
                                                   child[1]['class'] == 'cl'):
                        child[1]['role'] = node[1]['role']
                    node_stack += [child]

        # Get just the words.  For each word, get a pointer to its head (if any).  Add ID, morphological, and syntactic
        # information.
        for node_id, node in self.nodes.items():
            if node['tag'] == 'w':

                # Start a dictionary with the word's properties.
                word_dict = {'id': node['n'], 'book': node['book'], 'chapter': node['chapter'], 'verse': node['verse'],
                             'position': node['position'], 'lemma': node['lemma'], 'wordform': node['text'],
                             'pos': node['class'], 'is_head': node['is_head']}

                # Edit some properties by hand.
                if word_dict['lemma'] in list(POS_EDITS.lemma):
                    word_dict['pos'] = POS_EDITS.loc[POS_EDITS.lemma == word_dict['lemma'],].iloc[0]['pos']
                edit_targets = list(zip(LEMMA_EDITS['lemma'], LEMMA_EDITS['pos']))
                if (word_dict['lemma'], word_dict['pos']) in edit_targets:
                    edit_index = edit_targets.index((word_dict['lemma'], word_dict['pos']))
                    word_dict['lemma'] = LEMMA_EDITS['new_lemma'][edit_index]
                if word_dict['wordform'] in AUTOS_FORMS and word_dict['pos'] != 'adj':
                    word_dict['lemma'] = 'αὐτός'
                    word_dict['pos'] = 'personal pronoun'

                # Add properties that might or might not be present.
                for field in ['number', 'gender', 'case', 'person', 'tense', 'voice', 'mood', 'degree', 'noun_class',
                              'verb_class']:
                    if field in node:
                        word_dict[field] = node[field]
                    else:
                        word_dict[field] = None

                # Add fields that we'll populate later.
                word_dict['head'] = None
                word_dict['deps'] = []
                word_dict['relation'] = 'unknown'
                word_dict['noun_class_type'] = None
                word_dict['verb_class_type'] = None
                word_dict['nominal_type'] = None
                word_dict['case_type'] = None
                if 'role' in node:
                    word_dict['relation'] = node['role']

                # Get the head of this word, if any.
                walking_up = True
                word_is_root = False
                current_node = node
                while walking_up:
                    walking_up = current_node['is_head'] and 'parent_n' in self.nodes[current_node['parent_n']]
                    word_is_root = current_node['is_head'] and not walking_up
                    current_node = self.nodes[current_node['parent_n']]
                if not word_is_root:
                    found_head = False
                    while not found_head:
                        current_node = self.nodes[current_node['head_child_n']]
                        found_head = current_node['tag'] == 'w'
                    word_dict['head_id'] = current_node['n']

                # Add the word to the list of words.
                self.words += [word_dict]

        # Edit POS by hand.
        edits_df = pd.DataFrame(self.words)
        edits_df = edits_df.merge(INDIVIDUAL_POS_EDITS, left_on=['book', 'chapter', 'verse', 'position'],
                                  right_on=['book', 'chapter', 'verse', 'position'])
        edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
        if edits_df.shape[0] > 0:
            for word in self.words:
                if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                    edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'],
                                                     word['position']))
                    word['pos'] = edits_df['new_pos'][edit_index]

        # Sort the words.
        self.words = sorted(self.words, key=lambda d: (d['chapter'], d['verse'], d['position']))

        # In a chain of conjuncts, point each conjunct to the conjunction immediately before.
        for word in self.words:
            if 'head_id' in word:
                conj_head = self.nodes[word['head_id']]
                if conj_head['lemma'] in ['καί', 'ἤ', 'οὐδέ'] and \
                        ('role' not in conj_head or conj_head['role'] != 'adv'):
                    left_conj_children = [w for w in self.words
                                          if 'head_id' in w and w['head_id'] == word['head_id'] and
                                             w['lemma'] == conj_head['lemma'] and
                                             'pos' in w and w['pos'] == 'conj' and
                                             (w['verse'] * 100 + w['position']) <
                                             (word['verse'] * 100) + word['position'] and
                                             ((w['verse'] * 100) + w['position'] >
                                              (conj_head['verse'] * 100) + conj_head['position'] or
                                              (word['verse'] * 100) + word['position'] <
                                              (conj_head['verse'] * 100) + conj_head['position'])]
                    right_conj_children = [w for w in self.words
                                           if 'head_id' in w and w['head_id'] == word['head_id'] and
                                              w['lemma'] == conj_head['lemma'] and
                                              'pos' in w and w['pos'] == 'conj' and
                                              (word['verse'] * 100) + word['position'] <
                                              (w['verse'] * 100) + w['position'] <
                                              (conj_head['verse'] * 100) + conj_head['position']]
                    if len(left_conj_children) > 0:
                        left_conj_children = sorted(left_conj_children,
                                                    key=lambda d: (d['chapter'], d['verse'], d['position']))
                        word['head_id'] = left_conj_children[-1]['id']
                    elif len(right_conj_children) > 0:
                        right_conj_children = sorted(right_conj_children,
                                                     key=lambda d: (d['chapter'], d['verse'], d['position']))
                        word['head_id'] = right_conj_children[0]['id']

        # Point predicate participles to the verb.
        for word in self.words:
            if 'relation' in word and word['relation'] in ['v', 'vp'] and 'mood' in word and \
                    word['mood'] == 'participle':
                for matrix_verb in self.words:
                    if 'head_id' in matrix_verb and matrix_verb['head_id'] == word['id'] and \
                            matrix_verb['lemma'] == 'εἰμί':
                        if 'head_id' in word:
                            matrix_verb['head_id'] = word['head_id']
                        else:
                            del matrix_verb['head_id']
                        word['head_id'] = matrix_verb['id']

        # Attach second-position clitics to the immediately preceding word.  Attach whatever was attached to the clitic
        # to the thing the clitic was attached to.
        for i, word in enumerate(self.words):
            if word['lemma'] in SECOND_POSITION_CLITICS and i != 0:
                for j, w in enumerate(self.words):
                    if 'head_id' in w and w['head_id'] == word['id']:
                        w['head_id'] = word['id']
                word['head_id'] = self.words[i - 1]['id']

        # Hand-entered head edits.
        edits_df = pd.DataFrame(self.words)
        edits_df = edits_df.merge(HEAD_EDITS, left_on=['book', 'chapter', 'verse', 'position'],
                                  right_on=['book', 'chapter', 'verse', 'position'])
        all_words = [(word['book'], word['chapter'], word['verse'], word['position']) for word in self.words]
        edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
        if edits_df.shape[0] > 0:
            for word in self.words:
                if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                    edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'], word['position']))
                    if np.isnan(edits_df['new_head_verse'][edit_index]):
                        if 'head_id' in word:
                            del word['head_id']
                        else:
                            print('REDUNDANT HEAD EDIT: ' + word['book'] + ' ' + str(word['chapter']) + ':' +
                                  str(word['verse']) + ' ' + str(word['position']))
                    else:
                        new_head_index = all_words.index((word['book'], word['chapter'], edits_df['new_head_verse'][edit_index],
                                                          edits_df['new_head_position'][edit_index]))
                        if 'head_id' in word and word['head_id'] == self.words[new_head_index]['id']:
                            print('REDUNDANT HEAD EDIT: ' + word['book'] + ' ' + str(word['chapter']) + ':' +
                                  str(word['verse']) + ' ' + str(word['position']))
                        word['head_id'] = self.words[new_head_index]['id']

        # Hand-entered feature edits.
        edits_df = pd.DataFrame(self.words)
        edits_df = edits_df.merge(CASE_EDITS, left_on=['book', 'chapter', 'verse', 'position'],
                                  right_on=['book', 'chapter', 'verse', 'position'])
        edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
        if edits_df.shape[0] > 0:
            for word in self.words:
                if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                    edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'], word['position']))
                    word['case'] = edits_df['new_case'][edit_index]
        edits_df = pd.DataFrame(self.words)
        edits_df = edits_df.merge(GENDER_EDITS, left_on=['book', 'chapter', 'verse', 'position'],
                                  right_on=['book', 'chapter', 'verse', 'position'])
        edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
        if edits_df.shape[0] > 0:
            for word in self.words:
                if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                    edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'], word['position']))
                    word['gender'] = edits_df['new_gender'][edit_index]

        # Set the sentence ID.
        self.sentence_id = self.words[0]['book'] + ' ' + str(self.words[0]['chapter']) + ':' + \
                           str(self.words[0]['verse']) + '.' + str(self.words[0]['position']) + ' - ' + \
                           self.words[-1]['book'] + ' ' + str(self.words[-1]['chapter']) + ':' + \
                           str(self.words[-1]['verse']) + '.' + str(self.words[-1]['position'])

        # Get the position indices of the head and deps of each word.
        for i, word in enumerate(self.words):
            if 'head_id' in word:
                for j, possible_head in enumerate(self.words):
                    if possible_head['id'] == word['head_id']:
                        word['head'] = j
                        possible_head['deps'] += [i]
            else:
                root = i

        # Get all the roots of sentences within this sentence (the root of the whole tree, plus any additional hand-
        # specified roots).
        new_roots_df = pd.DataFrame(pd.DataFrame(self.words))
        new_roots_df = new_roots_df.merge(CUTS, left_on=['book', 'chapter', 'verse', 'position'],
                                          right_on=['book', 'chapter', 'verse', 'position'])
        cuts = list(zip(new_roots_df.book, new_roots_df.chapter, new_roots_df.verse, new_roots_df.position))
        self.roots = [root]
        for i, word in enumerate(self.words):
            if (word['book'], word['chapter'], word['verse'], word['position']) in cuts:
                self.roots += [i]

    # Return a list of sentences within the uncut sentence.
    def get_sentences(self):
        return [Sentence(self, root) for root in self.roots]


class Sentence:

    # Get a citation from a list of words.
    @staticmethod
    def get_citation(words):
        citations = [(BOOKS_OF_THE_BIBLE.index(word['book']), word['chapter'], word['verse']) for word in words]
        citations = list(set(citations))
        citations = sorted(citations)
        citation = PRETTY_BOOKS_OF_THE_BIBLE[citations[0][0]] + ' ' + str(citations[0][1]) + ':' +  str(citations[0][2])
        if len(citations) > 1:
            last_citation = citations[len(citations) - 1]
            if last_citation[0] != citations[0][0]:
                citation += ' - ' + PRETTY_BOOKS_OF_THE_BIBLE[last_citation[0]] + ' ' + str(
                    last_citation[1]) + ':' + str(
                    last_citation[2])
            else:
                citation += '-'
                if last_citation[1] != citations[0][1]:
                    citation += str(last_citation[1]) + ':' + str(last_citation[2])
                else:
                    citation += str(last_citation[2])
        return citation

    # Initialize the sentence from a specific root from an uncut sentence.
    def __init__(self, uncut_sentence, root):

        # Get the words that are actually in this sentence.  For each word, get the path from it to its root.
        self.words: List[Dict[str, Any]] = []
        paths = [[root]]
        while len(paths) > 0:
            current_path = paths.pop()
            current_word = uncut_sentence.words[current_path[-1]]
            if len(current_path) == 1:
                current_word['head'] = None
            current_word['path'] = current_path
            current_word['deps'] = [dep for dep in current_word['deps'] if dep not in uncut_sentence.roots]
            self.words += [current_word]
            paths += [current_path + [dep] for dep in current_word['deps']]

        # Sort the words.
        self.words = sorted(self.words, key=lambda d: (d['chapter'], d['verse'], d['position']))

        # Set the sentence ID.
        self.uncut_sentence_id = uncut_sentence.sentence_id
        self.sentence_id = self.words[0]['book'] + ' ' + str(self.words[0]['chapter']) + ':' + \
                           str(self.words[0]['verse']) + '.' + str(self.words[0]['position']) + ' - ' + \
                           self.words[-1]['book'] + ' ' + str(self.words[-1]['chapter']) + ':' + \
                           str(self.words[-1]['verse']) + '.' + str(self.words[-1]['position'])

        # Renumber indices.
        index_diff = root - [word['path'][1:] for word in self.words].index([])
        for word in self.words:
            if word['head'] is not None:
                word['head'] = word['head'] - index_diff
            word['path'] = [index - index_diff for index in word['path']]
            word['deps'] = [dep - index_diff for dep in word['deps']]

        # Set the text of this sentence.
        self.text = ' '.join(uncut_sentence.text.split(' ')[index_diff:(len(self.words) + index_diff)])

        # Set the citation of this sentence.
        self.citation = self.get_citation(self.words)

        # print()
        # for i, word in enumerate(self.words):
        #     print('(' + str(i) + ') ' + word['wordform'] + ' ' + str(word['head']) + ' ' + str(word['deps']))

        # Code some syntactic relations.
        for i, word in enumerate(self.words):

            # Get the features of the word (some of which might be encoded on its dependents).
            word_features = dict()
            for feature in ['case', 'gender', 'number', 'pos', 'mood']:
                word_features[feature] = None
                if 'lemma' in word and word['lemma'] in GENERAL_CONJUNCTIONS and \
                    not (word['pos'] == 'prep' and word['lemma'] == 'πλήν'):
                    temp_values = []
                    for dep_pos in word['deps']:
                        if feature in self.words[dep_pos] and self.words[dep_pos][feature] is not None:
                            temp_values += [self.words[dep_pos][feature]]
                    if len(temp_values) > 0:
                        word_features[feature] = Counter(temp_values).most_common(1)[0][0]
                    else:
                        word_features[feature] = None
                elif feature in word and word[feature] is not None:
                    word_features[feature] = word[feature]
                else:
                    for dep_pos in word['deps']:
                        if feature in self.words[dep_pos] and self.words[dep_pos]['pos'] in ['det'] and \
                                feature != 'pos':
                            word_features[feature] = self.words[dep_pos][feature]
                            break

            # Determine whether the word is the head of a relative clause.
            relative = False
            if (word_features['pos'] == 'verb' and
                word_features['mood'] in ['indicative', 'subjunctive', 'optative']) or \
                    word['lemma'] in SENTENTIAL_CONJUNCTIONS:
                dep_stack = word['deps'].copy()
                while len(dep_stack) > 0:
                    dep_word = self.words[dep_stack.pop()]
                    if dep_word['pos'].startswith('relative'):
                        relative = True
                        break
                    elif not (dep_word['pos'] == 'verb' and
                              dep_word['mood'] in ['indicative', 'subjunctive', 'optative'] and
                              not (word['lemma'] in GENERAL_CONJUNCTIONS + SENTENTIAL_CONJUNCTIONS and
                                   dep_word['head'] == i)):
                        dep_stack = dep_stack + dep_word['deps']

            # Get the features of the word's head (some of which might be encoded on its dependents).
            if word['head'] is not None:
                head = self.words[word['head']]
                word_head_features = dict()
                for feature in ['mood', 'pos', 'number', 'case', 'voice', 'degree', 'gender']:
                    word_head_features[feature] = None
                    if 'lemma' in head and head['lemma'] in GENERAL_CONJUNCTIONS and \
                            ('role' not in head or head['role'] != 'adv'):
                        temp_values = []
                        for dep_pos in [dp for dp in head['deps'] if self.words[dp]['id'] != word['id']]:
                            if feature in self.words[dep_pos] and self.words[dep_pos][feature] is not None:
                                temp_values += [self.words[dep_pos][feature]]
                        if len(temp_values) > 0:
                            word_head_features[feature] = Counter(temp_values).most_common(1)[0][0]
                        else:
                            word_head_features[feature] = None
                    elif feature in head and head[feature] is not None:
                        word_head_features[feature] = head[feature]
                    else:
                        for dep_pos in head['deps']:
                            if feature in self.words[dep_pos] and self.words[dep_pos]['pos'] in ['det'] and \
                                    feature != 'pos':
                                word_head_features[feature] = self.words[dep_pos][feature]
                                break
                conjunction = False
                if head['lemma'] in SENTENTIAL_CONJUNCTIONS:
                    conjunction = True
                elif head['lemma'] in GENERAL_CONJUNCTIONS and i != root:
                    walking_parent = uncut_sentence.nodes[uncut_sentence.nodes[word['id']]['n']]
                    conjunction = walking_parent['n'] == uncut_sentence.nodes[head['id']]['parent_n']
                    while 'parent_n' in walking_parent and not conjunction:
                        walking_parent = uncut_sentence.nodes[walking_parent['parent_n']]
                        conjunction = walking_parent['n'] == uncut_sentence.nodes[head['id']]['parent_n']

                # Guess at the syntactic relation between the word and its head.
                if word['lemma'] in SECOND_POSITION_CLITICS and word['id'] > head['id']:
                    word['relation'] = 'second-position clitic'
                elif (word_features['pos'] == 'num' or word['lemma'] in NUMBERS) and \
                        (head['pos'] == 'num' or head['lemma'] in NUMBERS):
                    word['relation'] = 'number'
                elif conjunction and (head['pos'] == 'conj' or
                                      (head['lemma'] in GENERAL_CONJUNCTIONS + SENTENTIAL_CONJUNCTIONS and
                                       (head['pos'] in ['conj', 'ptcl'] or
                                        head['lemma'] in ['κἄν', 'ἵνα', 'ὅτι']))) and \
                      not (head['lemma'] in ADVERB_CONJUNCTIONS and head['pos'] == 'adv'):
                    if head['lemma'] in COORDINATING_CONJUNCTIONS:
                        word['relation'] = 'conjunct'
                    elif head['lemma'] in SENTENTIAL_CONJUNCTIONS + ['ὡς', 'ὡσεί']:
                        if head['lemma'] == 'ὅτι' and \
                            ((head['head'] is not None and
                              self.words[head['head']]['lemma'] in SENTENTIAL_COMPLEMENT_HEADS) or
                             head['relation'] == 's'):
                            word['relation'] = 'conjunct, ὅτι'
                        else:
                            right_conjuncts = [index for index, w in enumerate(self.words)
                                               if 'head_id' in w and w['head_id'] == word['head_id'] and
                                                  w['lemma'] not in SECOND_POSITION_CLITICS and
                                                  (w['verse'] * 100) + w['position'] >
                                                  (head['verse'] * 100) + head['position']]
                            if len(right_conjuncts) > 0 and min(right_conjuncts) == i:
                                if head['lemma'] in ['ὡς', 'ὡσεί']:
                                    if word_features['pos'] == 'verb':
                                        word['relation'] = 'conjunct, ὡς, clause'
                                    else:
                                        word['relation'] = 'conjunct, ὡς, non-clause'
                                else:
                                    word['relation'] = 'conjunct, subordinate'
                            else:
                                word['relation'] = 'conjunct, main'
                    else:
                        word['relation'] = 'conjunct, other'
                elif word['relation'] == 's':
                    if head['lemma'] in SENTENTIAL_CONJUNCTIONS:
                        word['relation'] = 'conjunction'
                    elif word_head_features['pos'] != 'verb':
                        word['relation'] = 'subject of verbless predicate'
                    elif word_head_features['mood'] == 'infinitive':
                        word['relation'] = 'subject of infinitive'
                    elif word_head_features['mood'] == 'participle':
                        if word_features['case'] == 'accusative':
                            word['relation'] = 'subject of small clause'
                        else:
                            word['relation'] = 'subject of participle'
                    elif word['lemma'] != 'καί' and word_features['gender'] == 'neuter' and \
                            word_features['number'] == 'plural':
                        if word_head_features['number'] == 'singular':
                            word['relation'] = 'subject, neuter plural'
                        else:
                            word['relation'] = 'subject, neuter plural, regular agreement'
                    elif (word['lemma'] != 'καί' and word_features['number'] is not None and
                          word_head_features['number'] is not None and
                          word_features['number'] != word_head_features['number']) or \
                            (word['lemma'] == 'καί' and word_head_features['number'] == 'singular' and
                             word_features['mood'] != 'infinitive'):
                        word['relation'] = 'subject, irregular agreement'
                    else:
                        word['relation'] = 'subject'
                elif word['pos'] == 'ptcl' and word['lemma'] not in NEGATION:
                    word['relation'] = 'particle'
                elif word['pos'] == 'det':
                    if word_head_features['pos'] == 'verb' and word_head_features['mood'] == 'infinitive':
                        word['relation'] = 'determiner'
                    elif word_head_features['pos'] == 'verb' and \
                            word_head_features['mood'] in ['indicative', 'imperative', 'subjunctive', 'optative']:
                        word['relation'] = 'determiner'
                    elif (head['pos'] in GENERAL_CONJUNCTIONS and word_head_features['gender'] is None) or \
                            (head['pos'] not in GENERAL_CONJUNCTIONS and head['gender'] is None) or \
                            word_head_features['gender'] != word_features['gender'] or \
                            (head['pos'] in GENERAL_CONJUNCTIONS and word_head_features['number'] is None) or \
                            (head['pos'] not in GENERAL_CONJUNCTIONS and head['number'] is None) or \
                            word_head_features['number'] != word_features['number'] or \
                            (head['pos'] in GENERAL_CONJUNCTIONS and word_head_features['case'] is None) or \
                            (head['pos'] not in GENERAL_CONJUNCTIONS and head['case'] is None) or \
                            word_head_features['case'] != word_features['case']:
                        if word_features['gender'] == 'neuter' and word_features['number'] == 'plural':
                            word['relation'] = 'determiner, things of'
                        else:
                            word['relation'] = 'determiner'
                    else:
                        word['relation'] = 'determiner'
                elif word['lemma'] in NEGATION:
                    if word_head_features['pos'] in ['verb', 'ptcl'] and word_head_features['mood'] != 'participle':
                        word['relation'] = 'negation of verb'
                    elif head['lemma'] in NEGATION:
                        word['relation'] = 'negation, double'
                    elif head['head'] is not None and self.words[head['head']]['lemma'] in ['εἰ', 'ἐάν']:
                        if word_head_features['pos'] in ['noun', 'adj', 'personal pronoun'] or \
                                (word_head_features['pos'] == 'verb' and word_head_features['mood'] == 'participle'):
                            word['relation'] = 'negation, εἰ μὴ, nominal'
                        else:
                            word['relation'] = 'negation, εἰ μὴ'
                    else:
                        if (word_head_features['pos'] in ['noun', 'adj', 'personal pronoun',
                                                          'demonstrative pronoun', 'relative pronoun',
                                                          'reflexive pronoun'] or \
                                 (word_head_features['pos'] == 'verb' and
                                  word_head_features['mood'] == 'participle')) and \
                                head['lemma'] != 'ὡς':
                            word['relation'] = 'negation of nominal'
                        else:
                            word['relation'] = 'negation, other'
                elif word['relation'] == 'p':
                    if word_features['pos'] in ['noun', 'adj', 'num', 'personal pronoun', 'indefinite pronoun',
                                                'interrogative pronoun', 'demonstrative pronoun',
                                                'relative pronoun'] or \
                            (word_features['pos'] == 'verb' and word_features['mood'] == 'participle'):
                        word['relation'] = 'predicate, nominal'
                    else:
                        word['relation'] = 'predicate, non-nominal'
                elif head['lemma'] in SENTENTIAL_COMPLEMENT_HEADS and word['pos'] in ['verb', 'conj'] and \
                        (word['case'] is None or word_features['case'] != 'accusative') and \
                        (word['mood'] is None or word_features['mood'] not in ['participle', 'infinitive']) and \
                        (word_head_features['voice'] != 'passive' or head['lemma'] == 'ἀποκρίνομαι') and \
                        ('role' not in head or head['role'] != 'adv') and not relative:
                    word['relation'] = 'sentential complement'
                elif word_head_features['pos'] == 'prep' and not (word['lemma'] == 'καί' and word['pos'] == 'adv'):
                    if word['id'] < head['id'] and word_features['pos'] == 'adj':
                        word['relation'] = 'modifier of nominal, nominal'
                    else:
                        word['relation'] = 'object of preposition'
                elif word_features['pos'] == 'prep':
                    if word_head_features['pos'] in ['noun', 'interrogative pronoun', 'num', 'personal pronoun',
                                                     'indefinite pronoun']:
                        word['relation'] = 'modifier of nominal, PP'
                    elif word_head_features['degree'] == 'comparative':
                        word['relation'] = 'comparative'
                    elif word_head_features['pos'] == 'adj':
                        word['relation'] = 'modifier of adjective, PP'
                    elif word_head_features['pos'] in ['verb', 'conj']:
                        word['relation'] = 'modifier of verb, PP'
                    else:
                        word['relation'] = 'modifier of other, PP'
                elif word_features['mood'] == 'participle' and word['relation'] == 'adv' and \
                        word_head_features['pos'] == 'verb':
                    word['relation'] = 'modifier of verb, participle'
                elif (word_features['case'] is not None or word_head_features['case'] is not None) \
                        and (word_features['case'] == word_head_features['case']
                             or word_features['case'] is None or word_head_features['case'] is None) \
                        and (word_features['gender'] == word_head_features['gender']
                             or word_features['gender'] is None or word_head_features['gender'] is None or
                             head['gender'] is None) \
                        and (word_features['number'] == word_head_features['number']
                             or word_features['number'] is None or word_head_features['number'] is None) \
                        and (word_features['pos'] in ['adj', 'demonstrative pronoun', 'interrogative pronoun',
                                                      'indefinite pronoun', 'verb', 'num']
                             or (head['lemma'] in TITLES and bool(re.match(GREEK_CAPITALS, word['lemma'])))
                             or (word['lemma'] in TITLES and bool(re.match(GREEK_CAPITALS, head['lemma'])))) and \
                        word_head_features['mood'] not in ['indicative', 'imperative', 'subjunctive', 'optative',
                                                           'infinitive'] and \
                        word_features['mood'] not in ['infinitive'] and \
                        not relative:
                    if head['lemma'] in TITLES and bool(re.match(GREEK_CAPITALS, word['lemma'])):
                        word['relation'] = 'entitled'
                    elif word['lemma'] in TITLES and bool(re.match(GREEK_CAPITALS, head['lemma'])):
                        word['relation'] = 'title'
                    elif bool(re.match(GREEK_CAPITALS, word['lemma'])) and \
                            bool(re.match(GREEK_CAPITALS, head['lemma'])):
                        word['relation'] = 'name'
                    else:
                        word['relation'] = 'modifier of nominal, nominal'
                elif word_features['pos'] == 'verb' and word_features['mood'] == 'infinitive' and \
                        not (word_head_features == ['verb'] and word_features['case'] == 'genitive'):
                    if word_head_features['pos'] == 'verb':
                        if word_features['case'] == 'genitive':
                            word['relation'] = 'infinitive, purpose'
                        elif head['lemma'] in INFINITIVE_ARGUMENT_HEADS:
                            word['relation'] = 'infinitive argument of verb'
                        else:
                            word['relation'] = 'infinitive, purpose'
                    elif word_head_features['pos'] == 'adj':
                        word['relation'] = 'argument of adjective, infinitive'
                    elif word_head_features['pos'] == 'noun':
                        word['relation'] = 'infinitive argument of noun'
                elif word_features['pos'] in ['adj', 'num', 'noun'] and word_head_features['pos'] == 'verb' and \
                        (word_features['case'] is None or word_features['case'] == 'nominative') and \
                        word['relation'] == 'adv':
                    word['relation'] = 'modifier of verb, nominal'
                elif word_features['case'] == 'genitive':
                    if word['lemma'] in ['ὅς', 'ὅστις'] and i > 0 and \
                            self.words[i - 1]['lemma'] in ['ἕως', 'μέχρι(ς)', 'ἄχρι', 'ἄχρις']:
                        word['relation'] = 'genitive, time'
                    elif word_head_features['pos'] == 'verb':
                        if word_features['mood'] == 'participle':
                            word['relation'] = 'modifier of verb, participle'
                        else:
                            word['relation'] = 'direct object'
                    elif word_head_features['pos'] == 'adj' and word_head_features['degree'] == 'comparative':
                        word['relation'] = 'genitive, comparative'
                    elif head['lemma'] in PARTITIVE_HEADS:
                        word['relation'] = 'genitive, part-whole'
                    elif word_head_features['pos'] == 'adj':
                        word['relation'] = 'argument of adjective, nominal'
                    elif head['lemma'] in ['ἄγγελος', 'ἀδελφή', 'ἀδελφός', 'ἀνήρ', 'ἄρχων', 'βασιλεύς', 'γονεύς',
                                           'γυνή', 'δέσμιος', 'διδάσκαλος', 'δοῦλος', 'ἐχθρός', 'θεός', 'θυγάτηρ',
                                           'κύριος', 'λαός', 'μαθητής', 'μήτηρ', 'παῖς', 'πατήρ', 'πλησίον', 'σπέρμα',
                                           'συγγενής', 'συγγενίς', 'σύνδουλος', 'συνεργός', 'τέκνον', 'υἱός', 'φίλος',
                                           'Χριστός']:
                        word['relation'] = 'genitive, relation'
                    elif head['lemma'] in ['αἷμα', 'γλῶσσα', 'δάκτυλος', 'δεξιά', 'διάνοια', 'καρδία', 'κεφαλή',
                                           'κοιλία', 'μέλος', 'μέτωπον', 'ὀσφῦς', 'οὐρά', 'οὖς', 'ὀφθαλμός', 'πνεῦμα',
                                           'πούς', 'πρόσωπον', 'σάρξ', 'σπλάγχνον', 'στόμα', 'συνείδησις', 'σῶμα',
                                           'τράχηλος', 'χείρ', 'ψυχή']:
                        word['relation'] = 'genitive, body part'
                    elif head['lemma'] in ['ἀγαπητός', 'ἁμαρτία', 'ἀνάστασις', 'ἀναστροφή', 'ἀπόστολος', 'ἀσθένεια',
                                           'δέησις', 'διδαχή', 'ἔλεος', 'ἐνέργεια', 'ἐντολή', 'ἐπιθυμία', 'ἐπιφάνεια',
                                           'ἔργον', 'ζωή', 'θάνατος', 'θέλημα', 'καύχημα', 'μαρτυρία', 'ὀργή',
                                           'παράπτωμα', 'παρουσία', 'περισσεία', 'πίστις', 'πορνεία', 'προσευχή',
                                           'ῥῆμα', 'φωνή', 'χαρά']:
                        word['relation'] = 'genitive, subject'
                    elif head['lemma'] in ['ἀποκάλυψις', 'ἄφεσις', 'βρυγμός', 'γνῶσις', 'διάκονος', 'ἔνδειξις',
                                           'ἔπαινος', 'ἐπίγνωσις', 'ἐπίθεσις', 'θλῖψις', 'καθαρισμός', 'καταβολή',
                                           'μιμητής', 'οἰκοδομή', 'παράκλησις', 'ποιητής', 'σωτηρία', 'σωτήρ', 'φόβος',
                                           'χρεία']:
                        word['relation'] = 'genitive, object'
                    elif head['lemma'] in ['βασιλεία', 'θρόνος', 'ἱμάτιον', 'κράβαττος', 'μισθός', 'ναός', 'οἰκία',
                                           'οἶκος', 'ὄνομα', 'σταυρός', 'συναγωγή', 'τράπεζα', 'ὑπάρχω', 'φιάλη',
                                           'χώρα']:
                        word['relation'] = 'genitive, possession'
                    elif head['lemma'] in ['δικαιοσύνη', 'δόξα', 'δύναμις', 'ἰσχύς']:
                        word['relation'] = 'genitive, characterized by'
                    elif head['lemma'] in ['ἔσχατος', 'κλάδος', 'πέρας', 'πρεσβύτερος', 'συντέλεια', 'τεῖχος']:
                        word['relation'] = 'genitive, part-whole'
                    elif head['lemma'] in ['ζηλωτής']:
                        word['relation'] = 'genitive, about'
                    elif head['lemma'] in ['μέσος']:
                        word['relation'] = 'genitive, location'
                    elif head['lemma'] in ['ὄρος', 'φυλή']:
                        word['relation'] = 'genitive, specification'
                    elif head['lemma'] in ['πλῆθος']:
                        word['relation'] = 'genitive, material'
                    elif head['lemma'] in ['σοφία', 'χάρις']:
                        word['relation'] = 'genitive, source'
                    else:
                        word['relation'] = 'genitive, other'
                elif 'case' in word and word_features['case'] == 'dative':
                    if head['lemma'] in ['ἀκολουθέω', 'ἀνθίστημι', 'ἀντίκειμαι', 'ἀπειθέω', 'ἀποτάσσομαι', 'ἀρέσκω',
                                         'ἀτενίζω', 'βοηθέω', 'διακονέω', 'δοκέω', 'δουλεύω', 'ἐγγίζω', 'ἐμβλέπω',
                                         'ἐμπαίζω', 'ἐξακολουθέω', 'ἐξομολογέω', 'ἔοικα', 'ἐπακολουθέω', 'ἐπιμένω',
                                         'ἐπισκιάζω', 'ἐπιτιμάω', 'εὐχαριστέω', 'ἐφίστημι', 'λατρεύω', 'μέλει',
                                         'παρακολουθέω', 'πείθω', 'πιστεύω', 'πρέπω', 'προσέρχομαι', 'προσέχω',
                                         'προσκαρτερέω', 'προσκυνέω', 'προσμένω', 'προσπίπτω', 'συγκοινωνέω',
                                         'συγχαίρω', 'συμβαίνω', 'συμβάλλω', 'συμφέρω', 'συναντάω', 'συνέρχομαι',
                                         'ὑπακούω', 'ὑπαντάω']:
                        word['relation'] = 'direct object'
                    elif word_head_features['pos'] == 'verb':
                        word['relation'] = 'indirect object'
                    elif word_head_features['pos'] == 'adj':
                        word['relation'] = 'argument of adjective, nominal'
                    else:
                        word['relation'] = 'dative, other'
                elif 'case' in word and word_features['case'] == 'accusative':
                    if word['relation'] == 'adv' and word['gender'] == 'neuter':
                        if word['lemma'] == 'τίς':
                            word['relation'] = 'accusative, other'
                        else:
                            word['relation'] = 'accusative, manner'
                    elif word_head_features['pos'] == 'verb':
                        word['relation'] = 'direct object'
                    elif word['lemma'] in ['δεύτερος', 'ἔτος', 'ἡμέρα', 'πρότερος', 'πρῶτος', 'ταχύ', 'τρίτος',
                                           'ὕστερος', 'χρόνος', 'ὥρα']:
                        word['relation'] = 'accusative, time'
                    elif word['lemma'] in ['πολύς']:
                        word['relation'] = 'accusative, amount'
                    elif word['lemma'] in ['τρόπος']:
                        word['relation'] = 'accusative, manner'
                    else:
                        word['relation'] = 'accusative, other'
                elif 'case' in word and word_features['case'] == 'vocative':
                    word['relation'] = 'interjection, vocative'
                elif word_features['pos'] in ['noun'] and word_head_features['pos'] in ['noun'] and \
                        word_features['case'] is not None and word_head_features['case'] is not None and \
                        (word_features['case'] == word_head_features['case'] or
                         (word_features['case'] == 'nominative' and word_head_features['case'] == 'vocative')):
                    word['relation'] = 'appositive'
                elif word_features['pos'] in ['adv', 'adverb with kai', 'relative adverb', 'interrogative adverb',
                                              'indefinite adverb'] or \
                        word['pos'] in ['adv', 'adverb with kai', 'relative adverb', 'interrogative adverb',
                                        'indefinite adverb'] or \
                        (word['pos'] == 'conj' and word['relation'] == 'adv' and not relative):
                    if word_head_features['pos'] == 'verb':
                        word['relation'] = 'modifier of verb, adverb'
                    elif word_head_features['pos'] == 'adj':
                        word['relation'] = 'modifier of adjective, adverb'
                    elif word_head_features['pos'] in ['noun', 'personal pronoun', 'demonstrative pronoun', 'num',
                                                       'reflexive pronoun', 'interrogative pronoun',
                                                       'indefinite pronoun']:
                        word['relation'] = 'modifier of nominal, adverb'
                    else:
                        word['relation'] = 'modifier of other, adverb'
                elif relative:
                    if word_head_features['degree'] == 'comparative' and word_features['case'] == 'genitive':
                        word['relation'] = 'genitive, comparative'
                    elif word_head_features['pos'] in ['noun', 'adj', 'personal pronoun', 'indefinite pronoun',
                                                       'demonstrative pronoun', 'interrogative pronoun']:
                        word['relation'] = 'modifier of nominal, nominal'
                    elif word_head_features['pos'] == 'verb':
                        if word['relation'] == 'o':
                            word['relation'] = 'direct object'
                        elif word_head_features['mood'] == 'participle':
                            word['relation'] = 'modifier of nominal, nominal'
                        else:
                            word['relation'] = 'modifier of verb, nominal'
                elif word['relation'] == 'o':
                    word['relation'] = 'direct object'
                elif head['mood'] == 'indicative' and head['person'] == 'third' and head['number'] == 'singular' and \
                        ((head['lemma'] == 'γίνομαι' and head['voice'] == 'middle') or
                         (head['lemma'] == 'γράφω' and head['voice'] == 'passive') or
                         (head['lemma'] == 'μέλει' and head['voice'] == 'active')):
                    word['relation'] = 'subject'
                elif word_head_features['degree'] == 'comparative':
                    word['relation'] = 'comparative'
                elif word_features['mood'] == 'participle' and head['lemma'] == 'εἰμί':
                    word['relation'] = 'predicate, nominal'

            # Guess at the nominal type of the word.
            if relative:
                word['nominal_type'] = 'relative clause'
            elif word_features['pos'] == 'noun':
                word['nominal_type'] = 'noun'
            elif word_features['pos'] is not None and 'pronoun' in word_features['pos']:
                word['nominal_type'] = 'pronoun'
            elif word_features['pos'] in ['adj', 'num']:
                word['nominal_type'] = 'adjective'
            elif word_features['pos'] == 'det':
                word['nominal_type'] = 'determiner'
            elif word_features['pos'] == 'verb':
                if word_features['mood'] == 'participle':
                    word['nominal_type'] = 'participle'
                elif word_features['mood'] == 'infinitive':
                    word['nominal_type'] = 'infinitive'
                else:
                    word['nominal_type'] = 'clause'
            elif word_features['pos'] in ['prep', 'adv'] or \
                    (word_features['pos'] is not None and 'adverb' in word_features['pos']):
                word['nominal_type'] = 'headless'
            else:
                word['nominal_type'] = 'clause'

            # Get at the noun class type of the word
            if ('noun' in word['pos'] and word['pos'] not in ['personal pronoun', 'personal pronoun with kai']) or \
                    word['pos'] == 'adj':
                if word['lemma'] == 'Ἰησοῦς':
                    word['noun_class_type'] = 'Ihsous'
                elif word['lemma'] == 'ὅστις':
                    word['noun_class_type'] = 'first/second declension; third declension, consonant stem'
                elif word['lemma'] in FIRST_DECLENSION:
                    word['noun_class_type'] = 'first declension'
                elif word['lemma'] in FIRST_SECOND_DECLENSION:
                    word['noun_class_type'] = 'first/second declension'
                elif word['lemma'] in SECOND_DECLENSION:
                    word['noun_class_type'] = 'second declension'
                elif word['lemma'] in THIRD_DECLENSION_CONSONANT_STEM:
                    word['noun_class_type'] = 'third declension, consonant stem'
                elif word['lemma'] in THIRD_DECLENSION_VOWEL_STEM:
                    word['noun_class_type'] = 'third declension, vowel stem'
                elif word['lemma'] in UNDECLINED_NOUNS:
                    word['noun_class_type'] = 'undeclined'
                elif word['lemma'] in IRREGULAR_NOUNS:
                    word['noun_class_type'] = 'irregular'
                elif word['lemma'].endswith('μα'):
                    word['noun_class_type'] = 'third declension, consonant stem'
                elif word['lemma'].endswith('ος') and word['gender'] == 'neuter' and \
                        word['pos'] == 'noun' and word['lemma'] != 'ζῆλος':
                    word['noun_class_type'] = 'third declension, vowel stem'
                elif word['lemma'].endswith('ος') or word['lemma'].endswith('ός') \
                        or word['lemma'].endswith('ον') or word['lemma'].endswith('όν') or word['lemma'] == 'ὅς':
                    if word['pos'] == 'noun':
                        word['noun_class_type'] = 'second declension'
                    elif word['pos'] == 'adj' or 'pronoun' in word['pos']:
                        word['noun_class_type'] = 'first/second declension'
                elif word['lemma'].endswith('η') or word['lemma'].endswith('ή') or \
                        word['lemma'].endswith('α') or word['lemma'].endswith('ά') or \
                        word['lemma'].endswith('ῆ'):
                    if word['pos'] == 'noun':
                        word['noun_class_type'] = 'first declension'
                    elif word['pos'] == 'adj':
                        word['noun_class_type'] = 'first/second declension'
                elif word['pos'] == 'noun' and word['gender'] == 'masculine' and \
                        (word['lemma'].endswith('ης') or word['lemma'].endswith('ής') or
                         word['lemma'].endswith('ίας')) or word['lemma'].endswith('ας') or \
                        word['lemma'].endswith('ῆς') or word['lemma'].endswith('ᾶς'):
                    word['noun_class_type'] = 'first declension with hs'
                elif word['lemma'].endswith('ος') or word['lemma'].endswith('εύς') or \
                        word['lemma'].endswith('υς') or word['lemma'].endswith('ύς') or \
                        word['lemma'].endswith('ις'):
                    word['noun_class_type'] = 'third declension, vowel stem'
                elif word['lemma'].endswith('της') or word['lemma'].endswith('ών') or \
                        word['lemma'].endswith('ήρ') or word['lemma'].endswith('ψ') or \
                        word['lemma'].endswith('ίς') or word['lemma'].endswith('ωρ') or \
                        word['lemma'].endswith('ξ') or word['lemma'].endswith('ων'):
                    word['noun_class_type'] = 'third declension, consonant stem'
                else:
                    word['noun_class_type'] = 'undeclined'

            # Guess at the case type of the word.
            word['case_type'] = word_features['case']

            # Guess at the verb class type of the word.
            if word['pos'] == 'verb':
                if word['lemma'] in ['εἴσειμι', 'ἔξειμι']:
                    word['verb_class_type'] = 'mi'
                elif word['lemma'] in ['εἰμί', 'ἔξεστι(ν)'] or word['lemma'].endswith('ειμι'):
                    word['verb_class_type'] = 'eimi'
                elif word['lemma'] in ['οἶδα', 'σύνοιδα']:
                    word['verb_class_type'] = 'oida'
                elif word['lemma'].endswith('έω') or word['lemma'].endswith('έομαι') or word['lemma'] == 'δεῖ':
                    word['verb_class_type'] = 'contract, ew'
                elif word['lemma'].endswith('άω') or word['lemma'].endswith('άομαι'):
                    word['verb_class_type'] = 'contract, aw'
                elif word['lemma'].endswith('όω') or word['lemma'].endswith('όομαι'):
                    word['verb_class_type'] = 'contract, ow'
                elif word['lemma'].endswith('ω') or word['lemma'].endswith('ομαι') or \
                        word['lemma'] in ['μέλει', 'εἴωθα', 'ἀπεῖπον', 'ἔοικα', 'ἄγε']:
                    word['verb_class_type'] = 'omega'
                elif word['lemma'].endswith('μι') or word['lemma'].endswith('μί') or word['lemma'].endswith('μαι'):
                    word['verb_class_type'] = 'mi'
                else:
                    word['verb_class_type'] = 'other'

        # Hand-entered edits to syntactic relations.
        for relation_type, relation_edits_df in RELATION_EDITS.items():
            edits_df = pd.DataFrame(pd.DataFrame(self.words))
            edits_df = edits_df.merge(relation_edits_df, left_on=['book', 'chapter', 'verse', 'position'],
                                      right_on=['book', 'chapter', 'verse', 'position'])
            edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
            if edits_df.shape[0] > 0:
                for word in self.words:
                    if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                        edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'],
                                                         word['position']))
                        new_relation = edits_df['new_relation'][edit_index]
                        if relation_type == 'dative' and new_relation == 'direct object':
                            pass
                        elif relation_type != 'other':
                            new_relation = relation_type + ', ' + new_relation
                        if word['relation'] == new_relation:
                            print('REDUNDANT RELATION EDIT: ' + word['book'] + ' ' + str(word['chapter']) + ':' +
                                  str(word['verse']) + ' ' + str(word['position']) + ' ' + new_relation)
                        word['relation'] = new_relation

        # Hand-entered edits to types.
        edits_df = pd.DataFrame(pd.DataFrame(self.words))
        edits_df = edits_df.merge(TYPE_EDITS, left_on=['book', 'chapter', 'verse', 'position'],
                                  right_on=['book', 'chapter', 'verse', 'position'])
        edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
        if edits_df.shape[0] > 0:
            for word in self.words:
                if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                    edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'],
                                                     word['position']))
                    for type_name in ['nominal_type', 'case_type']:
                        new_type = edits_df['new_' + type_name][edit_index]
                        if not pd.isna(new_type):
                            if word[type_name] == new_type:
                                print('REDUNDANT TYPE EDIT: ' + word['book'] + ' ' + str(word['chapter']) + ':' +
                                      str(word['verse']) + ' ' + str(word['position']) + ' ' + new_type)
                            word[type_name] = new_type

    # Extract all licit strings from the sentence.
    def get_licit_strings(self):

        # Start with an empty list of mandatory pairs of words (where, if the first is present, the second must be
        # present as well or else the string is not licit).
        mandatory_pairs = []

        # Iterate over words, looking for words that require some other word to be present.
        for i, word in enumerate(self.words):

            # If the word is a negation, its head requires its presence (and it requires its head).
            if word['lemma'] in NEGATION + EXTENDED_NEGATION and word['head'] is not None:
                mandatory_pairs += [(word['head'], i), (i, word['head'])]

            # If the word is a determiner, its head must be present.
            if word['pos'] == 'det' and word['head'] is not None:
                mandatory_pairs += [(i, word['head'])]

            # If the word has a determiner, the determiner must be present (for certain parts of speech, and not for
            # names).
            if word['pos'] in KEEP_DETERMINER_POS and \
                    not bool(re.match(GREEK_CAPITALS, word['lemma'])) and \
                    word['lemma'] not in KEEP_DETERMINER_LEMMAS:
                mandatory_pairs += [(i, dep) for dep in word['deps']
                                    if self.words[dep]['relation'].startswith('determiner')]

            # If the word is the head of a "son of"-like relation, the relevant dependent must be present.
            if word['lemma'] in SON_OF_WORDS:
                mandatory_pairs += [(i, dep) for dep in word['deps'] if self.words[dep]['pos'] in SON_OF_POS]

            # If the word is a preposition, its argument must be present.
            if word['pos'] == 'prep':
                mandatory_pairs += [(i, dep) for dep in word['deps']]

            # If the word is copula-like and has a predicate, its predicate must be present.
            if word['lemma'] in COPULA:
                mandatory_pairs += [(i, dep) for dep in word['deps'] if 'predicate' in self.words[dep]['relation']]

            # If the word is a conjunction, its conjuncts must be present.
            if word['lemma'] in GENERAL_CONJUNCTIONS + SENTENTIAL_CONJUNCTIONS:
                mandatory_pairs += [(i, dep) for dep in word['deps']
                                    if self.words[dep]['relation'].startswith('conjunct')]

            # If the μὴ is part of εἰ μὴ, include the εἰ.
            if word['relation'].startswith('negation, εἰ μὴ'):
                mandatory_pairs += [(i, self.words[word['head']]['head'])]

            # If the word is the subject of a small clause or an infinitive, include the head of its head.
            if (word['relation'] == 'subject of small clause' or
                    word['relation'].startswith('subject of infinitive')) and \
                    self.words[word['head']]['head'] is not None:
                mandatory_pairs += [(i, self.words[word['head']]['head'])]

            # If the word is part of a gapping construction, include the head of its head.
            if word['relation'] == 'gap' and self.words[word['head']]['head'] is not None:
                mandatory_pairs += [(i, self.words[word['head']]['head'])]

            # If the word is sentential ὅτι, its head must be present.
            if word['lemma'] == 'ὅτι' and word['head'] is not None and \
                    len([dep for dep in word['deps'] if self.words[dep]['relation'] == 'conjunct, ὅτι']) > 0:
                mandatory_pairs += [(i, word['head'])]

            # If the word is the head of a relative clause, the relative must be present.
            if word['nominal_type'] == 'relative clause':
                dep_stack = word['deps'].copy()
                while len(dep_stack) > 0:
                    dep_index = dep_stack.pop()
                    dep_word = self.words[dep_index]
                    if dep_word['pos'].startswith('relative'):
                        mandatory_pairs += [(i, dep_index)]
                        break
                    elif not (dep_word['pos'] == 'verb' and
                              dep_word['mood'] in ['indicative', 'subjunctive', 'optative'] and
                              not (word['lemma'] in GENERAL_CONJUNCTIONS + SENTENTIAL_CONJUNCTIONS and
                                   dep_word['head'] == i)):
                        dep_stack = dep_stack + dep_word['deps']

            # If a second-position clitic is attached to the word, it must be present.
            mandatory_pairs += [(i, dep)
                                for dep in word['deps']
                                if self.words[dep]['relation'] == 'second-position clitic']

            # If the word is a semantically embedded sentential negation, include the verb.
            if word['relation'] == 'negation of verb, semantically embedded':
                current_word = word
                while 'head' in current_word and current_word['head'] is not None:
                    current_index = current_word['head']
                    current_word = self.words[current_index]
                    if current_word['pos'] == 'verb':
                        mandatory_pairs += [(i, current_index)]
                        break


        # Initialize the licit strings with all the individual words.
        licit_strings = [(i, i) for i in range(len(self.words))]

        # Iterate over all possible start positions.
        for first_word in range(len(self.words) - 1):

            # Iterate over all possible end positions.
            for last_word in range(first_word + 1, len(self.words)):

                # Assume this is a licit string until proven otherwise.
                licit_string = True

                # If the string starts with a second-position clitic, it's not licit.
                if self.words[first_word]['lemma'] in SECOND_POSITION_CLITICS and first_word > 0:
                    licit_string = False
                    # print('second-position clitic')

                # If the string ends with a second-position clitic, it's not licit, unless that's the last word in the
                # sentence.
                elif self.words[last_word]['lemma'] in SECOND_POSITION_CLITICS and last_word != len(self.words) - 1:
                    licit_string = False
                    # print('final second-position clitic')

                # If the string contains only part of a mandatory pair, it's not licit.
                else:
                    for w1, w2 in mandatory_pairs:
                        if first_word <= w1 <= last_word and (w2 < first_word or w2 > last_word):
                            licit_string = False
                            # print('partial mandatory pair')

                # Find the lowest node shared by the paths of all the nodes in the string.  Check all the paths from
                # non-trace nodes to the root: are there any paths with any non-trace nodes that are not in the string?
                # (I.e., is there any path between node and lowest common root with "gaps" outside the string?)  If so,
                # the string is not licit.
                if licit_string:
                    shared_nodes = set.intersection(*[set(w['path'])
                                                      for w in self.words[first_word:(last_word + 1)]
                                                      if 'lemma' in w and w['lemma']])
                    shared_nodes = [(node, len(self.words[node]['path'])) for node in shared_nodes]
                    lowest_node = [node for node, path_length in shared_nodes
                                   if path_length == max(pl for _, pl in shared_nodes)][0]
                    # print(lowest_node)
                    for word in range(first_word, last_word + 1):
                        if 'lemma' in self.words[word]:
                            lowest_node_index = self.words[word]['path'].index(lowest_node)
                            partial_path = self.words[word]['path'][lowest_node_index:]
                            gaps = [node for node in partial_path
                                    if 'lemma' in self.words[node]
                                    and (node < first_word or node > last_word)]
                            if len(gaps) > 0:
                                licit_string = False
                                # print('gap')
                                break

                # If this is a licit string, add it to the list.
                if licit_string:
                    licit_strings += [(first_word, last_word)]

        # Sort the list of licit strings.
        licit_strings = sorted(licit_strings)

        # Add the actual text of each licit string.
        licit_strings = [(ls[0], ls[1], ' '.join(self.text.split(' ')[ls[0]:(ls[1] + 1)])) for ls in licit_strings]

        # Return the list of licit strings.
        return licit_strings

    # Save the sentence to the database.
    def save_to_database(self, con):
        with con.cursor() as cur:

            # Adjust sentence IDs in saved checks, if necessary.
            if self.sentence_id != self.uncut_sentence_id:
                sql = """UPDATE checked_relation_tokens
                                JOIN words head_word
                                ON checked_relation_tokens.SentenceID = head_word.SentenceID
                                   AND checked_relation_tokens.HeadPos = head_word.SentencePosition
                                JOIN words dep_word
                                ON checked_relation_tokens.SentenceID = dep_word.SentenceID
                                   AND checked_relation_tokens.DependentPos = dep_word.SentencePosition
                         SET checked_relation_tokens.SentenceID = %s, checked_relation_tokens.HeadPos = %s,
                             checked_relation_tokens.DependentPos = %s
                         WHERE dep_word.Book = %s
                               AND dep_word.Chapter = %s
                               AND dep_word.Verse = %s
                               AND dep_word.VersePosition = %s
                               AND head_word.Verse = %s
                               AND head_word.VersePosition = %s"""
                cur.executemany(sql,
                                [(self.sentence_id, w['head'], j, w['book'], w['chapter'], w['verse'], w['position'],
                                  self.words[w['head']]['verse'], self.words[w['head']]['position'])
                                 for j, w in enumerate(self.words)
                                 if w['head'] is not None])
                sql = """UPDATE checked_types
                                JOIN words
                                ON checked_types.SentenceID = words.SentenceID
                                   AND checked_types.SentencePosition = words.SentencePosition
                         SET checked_types.SentenceID = %s, checked_types.SentencePosition = %s
                         WHERE words.Book = %s
                               AND words.Chapter = %s
                               AND words.Verse = %s
                               AND words.VersePosition = %s"""
                cur.executemany(sql,
                                [(self.sentence_id, j, w['book'], w['chapter'], w['verse'], w['position'])
                                 for j, w in enumerate(self.words)])

            # Delete and re-insert relations.
            sql = """DELETE FROM relations
                     WHERE (relations.SentenceID, relations.DependentPos) IN
                           (SELECT words.SentenceID, words.SentencePosition
                            FROM words
                            WHERE words.Book = %s
                                  AND words.Chapter = %s
                                  AND words.Verse = %s
                                  AND words.VersePosition = %s)"""
            cur.executemany(sql, [(w['book'], w['chapter'], w['verse'], w['position']) for w in self.words])
            sql = """INSERT INTO relations
                     (SentenceID, HeadPos, DependentPos, FirstPos, LastPos, Relation)
                     VALUES
                     (%s, %s, %s, %s, %s, %s)"""
            cur.executemany(sql,
                            [(self.sentence_id, word['head'], i, min(word['head'], i), max(word['head'], i),
                              word['relation'])
                             for i, word in enumerate(self.words)
                             if word['head'] is not None])

            # Delete and re-insert licit strings.
            sql = """WITH word_to_delete AS
                          (SELECT words.SentenceID, words.SentencePosition
                           FROM words
                           WHERE words.Book = %s
                                 AND words.Chapter = %s
                                 AND words.Verse = %s
                                 AND words.VersePosition = %s)
                     DELETE FROM strings
                     WHERE strings.SentenceID = (SELECT w1.SentenceID
                                                 FROM word_to_delete w1)
                           AND strings.Start <= (SELECT w2.SentencePosition
                                                 FROM word_to_delete w2)
                           AND strings.Stop >= (SELECT w3.SentencePosition
                                                FROM word_to_delete w3)"""
            cur.executemany(sql, [(w['book'], w['chapter'], w['verse'], w['position']) for w in self.words])
            strings = self.get_licit_strings()
            sql = """INSERT INTO strings
                     (SentenceID, Citation, Start, Stop, String)
                     VALUES
                     (%s, %s, %s, %s, %s)"""
            cur.executemany(sql,
                            [(self.sentence_id, self.get_citation(self.words[s[0]:(s[1] + 1)]), s[0], s[1], s[2])
                             for s in strings])

            # Delete and re-insert words.
            sql = """DELETE FROM words
                     WHERE Book = %s
                           AND Chapter = %s
                           AND Verse = %s
                           AND VersePosition = %s"""
            cur.executemany(sql, [(w['book'], w['chapter'], w['verse'], w['position']) for w in self.words])
            sql = """INSERT INTO words
                     (Book, Chapter, Verse, VersePosition, SentenceID, SentencePosition, Lemma, Wordform, POS, Gender,
                      Number, NCase, Person, Tense, Voice, Mood, Degree, NominalType, NounClassType, CaseType,
                      VerbClassType)
                     VALUES
                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.executemany(sql,
                            [(w['book'], w['chapter'], w['verse'], w['position'], self.sentence_id, j, w['lemma'],
                              w['wordform'], w['pos'], w['gender'], w['number'], w['case'], w['person'], w['tense'],
                              w['voice'], w['mood'], w['degree'], w['nominal_type'], w['noun_class_type'],
                              w['case_type'], w['verb_class_type'])
                             for j, w in enumerate(self.words)])

            # Commit changes.
            con.commit()


def get_pretty_string(sentence, limits):
    sentence_text = sentence[1].text
    return ' '.join(sentence_text.split(' ')[limits[0]:(limits[1] + 1)])


if __name__ == '__main__':

    # Connect to the database.
    connection = pymysql.connect(host='localhost', user='root', password=os.environ['MYSQL_PASSWORD'], database='gnt')

    # Initialize a dictionary to hold sentences.
    sentences = dict()

    # Iterate over books.
    for sbl_file in SBL_FILES:

        # Get all the sentences from the book.
        sentence_counter = 0
        sentences[sbl_file] = []
        sbl_sentences = [sbl_sentence
                         for sbl_sentence in ElementTree.parse(SBL_DIR + '/' + sbl_file).findall('.//sentence')]

        # Iterate over SBL sentences.
        for sbl_sentence in sbl_sentences:

            # Process the sentence.
            cut_sentences = UncutSentence(sbl_sentence).get_sentences()

            # Iterate over sentences.
            for sentence in cut_sentences:
                print('(' + str(sentence_counter) + ') ' + sentence.citation + ' ' + sentence.text)
                sentences[sbl_file] += [sentence]
                sentence.save_to_database(connection)
                sentence_counter += 1

    # Close the database connection.
    connection.close()
