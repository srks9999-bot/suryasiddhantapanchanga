"""
Name dictionaries for Panchanga elements in multiple languages.

This module contains localized names for:
- Planets
- Weekdays
- Lunar months (Masa)
- Solar months (Saura Masa)
- Karanas
- Yogas
- Nakshatras
- Tithis
- Pakshas
- Jovian years
"""

from typing import Dict

# Planet names
PLANET_NAMES: Dict[str, str] = {
    'star': 'Star        ',
    'sun': 'Sun         ',
    'moon': 'Moon        ',
    'mercury': 'Mercury     ',
    'venus': 'Venus       ',
    'mars': 'Mars        ',
    'jupiter': 'Jupiter     ',
    'saturn': 'Saturn      ',
    'Candrocca': 'Candrocca   ',
    'Rahu': 'Rahu        ',
}

# Weekday names in different languages
WEEKDAY_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'సోమవారం',
        1: 'మంగళవారం',
        2: 'బుధవారం',
        3: 'గురువారం',
        4: 'శుక్రవారం',
        5: 'శనివారం',
        6: 'ఆదివారం'
    },
    'english': {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
}

# Masa (lunar month) names in different languages
MASA_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'చైత్రము',
        1: 'వైశాఖము',
        2: 'జ్యేష్ఠము',
        3: 'ఆషాఢము',
        4: 'శ్రావణము',
        5: 'భాద్రపదము',
        6: 'ఆశ్వయుజము',
        7: 'కార్తీకము',
        8: 'మార్గశిరము',
        9: 'పుష్యము',
        10: 'మాఘము',
        11: 'ఫాల్గుణము'
    },
    'english': {
        0: 'Caitra',
        1: 'Vaisakha',
        2: 'Jyaistha',
        3: 'Asadha',
        4: 'Sravana',
        5: 'Bhadrapada',
        6: 'Asvina',
        7: 'Karttika',
        8: 'Margasirsa',
        9: 'Pausa',
        10: 'Magha',
        11: 'Phalguna'
    }
}

# Saura masa (solar month) names in different languages
SAURA_MASA_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'మేష',
        1: 'వృషభ',
        2: 'మిథున',
        3: 'కర్కాటక',
        4: 'సింహ',
        5: 'కన్య',
        6: 'తుల',
        7: 'వృశ్చిక',
        8: 'ధనుస్సు',
        9: 'మకర',
        10: 'కుంభ',
        11: 'మీన'
    },
    'english': {
        0: 'Mesa',
        1: 'Vrsa',
        2: 'Mithuna',
        3: 'Karkata',
        4: 'Simha',
        5: 'Kanya',
        6: 'Tula',
        7: 'Vrscika',
        8: 'Dhanus',
        9: 'Makara',
        10: 'Kumbha',
        11: 'Mina'
    }
}

# Karana names in different languages
KARANA_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'కింస్తుఘ్న',
        1: 'బవ',
        2: 'బాలవ',
        3: 'కౌలవ',
        4: 'తైతిల',
        5: 'గర',
        6: 'వణిజ',
        7: 'విష్టి',
        8: 'శకుని',
        9: 'చతుష్పద',
        10: 'నాగ'
    },
    'english': {
        0: 'Kimstughna',
        1: 'Bava',
        2: 'Balava',
        3: 'Kaulava',
        4: 'Taitila',
        5: 'Gara',
        6: 'Vanij',
        7: 'Visti',
        8: 'Sakuni',
        9: 'Catuspada',
        10: 'Naga'
    }
}

# Yoga names in different languages
YOGA_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'విష్కంభ',
        1: 'ప్రీతి',
        2: 'ఆయుష్మాన్',
        3: 'సౌభాగ్య',
        4: 'శోభన',
        5: 'అతిగండ',
        6: 'సుకర్మ',
        7: 'ధృతి',
        8: 'శూల',
        9: 'గండ',
        10: 'వృద్ధి',
        11: 'ధృవ',
        12: 'వ్యాఘాత',
        13: 'హర్షణ',
        14: 'వజ్ర',
        15: 'సిద్ధి',
        16: 'వ్యతిపాత',
        17: 'వరీయస్',
        18: 'పరిఘ',
        19: 'శివ',
        20: 'సిద్ధ',
        21: 'సాధ్య',
        22: 'శుభ',
        23: 'శుక్ల',
        24: 'బ్రహ్మ',
        25: 'ఐంద్ర',
        26: 'వైదృతి',
        27: 'విష్కంభ'
    },
    'english': {
        0: 'Viskambha',
        1: 'Priti',
        2: 'Ayusmat',
        3: 'Saubhagya',
        4: 'Sobhana',
        5: 'Atiganda',
        6: 'Sukarman',
        7: 'Dhrti',
        8: 'Sula',
        9: 'Ganda',
        10: 'Vrddhi',
        11: 'Dhruva',
        12: 'Vyaghata',
        13: 'Harsana',
        14: 'Vajra',
        15: 'Siddhi',
        16: 'Vyatipata',
        17: 'Variyas',
        18: 'Parigha',
        19: 'Siva',
        20: 'Siddha',
        21: 'Sadhya',
        22: 'Subha',
        23: 'Sukla',
        24: 'Brahman',
        25: 'Aindra',
        26: 'Vaidhrti',
        27: 'Viskambha'
    }
}

# Nakshatra names in different languages
NAKSHATRA_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'అశ్విని',
        1: 'భరణి',
        2: 'కృత్తిక',
        3: 'రోహిణి',
        4: 'మృగశిర',
        5: 'ఆర్ద్ర',
        6: 'పునర్వసు',
        7: 'పుష్య',
        8: 'ఆశ్లేష',
        9: 'మఘ',
        10: 'పూర్వ ఫల్గుణి',
        11: 'ఉత్తర ఫల్గుణి',
        12: 'హస్త',
        13: 'చిత్ర',
        14: 'స్వాతి',
        15: 'విశాఖ',
        16: 'అనురాధ',
        17: 'జ్యేష్ఠ',
        18: 'మూల',
        19: 'పూర్వాషాఢ',
        20: 'ఉత్తరాషాఢ',
        21: 'శ్రావణ',
        22: 'ధనిష్ఠ',
        23: 'శతభిష',
        24: 'పూర్వ భాద్రపద',
        25: 'ఉత్తర భాద్రపద',
        26: 'రేవతి',
        27: 'అశ్విని'
    },
    'english': {
        0: 'Asvini',
        1: 'Bharani',
        2: 'Krttika',
        3: 'Rohini',
        4: 'Mrgasira',
        5: 'Ardra',
        6: 'Punarvasu',
        7: 'Pusya',
        8: 'Aslesa',
        9: 'Magha',
        10: 'P-phalguni',
        11: 'U-phalguni',
        12: 'Hasta',
        13: 'Citra',
        14: 'Svati',
        15: 'Visakha',
        16: 'Anuradha',
        17: 'Jyestha',
        18: 'Mula',
        19: 'P-asadha',
        20: 'U-asadha',
        21: 'Sravana',
        22: 'Dhanistha',
        23: 'Satabhisaj',
        24: 'P-bhadrapada',
        25: 'U-bhadrapada',
        26: 'Revati',
        27: 'Asvini'
    }
}

# Tithi names in different languages (for tithi 1-14, same in both pakshas)
TITHI_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        1: 'పాడ్యమి',
        2: 'విదియ',
        3: 'తదియ',
        4: 'చవితి',
        5: 'పంచమి',
        6: 'షష్ఠి',
        7: 'సప్తమి',
        8: 'అష్టమి',
        9: 'నవమి',
        10: 'దశమి',
        11: 'ఏకాదశి',
        12: 'ద్వాదశి',
        13: 'త్రయోదశి',
        14: 'చతుర్దశి',
        # Note: Tithi 15 is handled separately:
        # - Sukla Paksha 15 = పౌర్ణమి (Purnima)
        # - Krsna Paksha 15 = అమావాస్య (Amavasya)
    },
    'english': {
        1: 'Pratipada',
        2: 'Dvitiya',
        3: 'Tritiya',
        4: 'Chaturthi',
        5: 'Panchami',
        6: 'Shashti',
        7: 'Saptami',
        8: 'Ashtami',
        9: 'Navami',
        10: 'Dashami',
        11: 'Ekadashi',
        12: 'Dvadashi',
        13: 'Trayodashi',
        14: 'Chaturdashi',
        # Note: Tithi 15 is handled separately:
        # - Sukla Paksha 15 = Purnima
        # - Krsna Paksha 15 = Amavasya
    }
}

# Special tithi names for the 15th tithi
TITHI_15_NAMES: Dict[str, Dict[str, str]] = {
    'telugu': {
        'Suklapaksa': 'పౌర్ణమి',
        'Krsnapaksa': 'అమావాస్య'
    },
    'english': {
        'Suklapaksa': 'Purnima',
        'Krsnapaksa': 'Amavasya'
    }
}

# Paksha names in different languages
PAKSHA_NAMES: Dict[str, Dict[str, str]] = {
    'telugu': {
        'Suklapaksa': 'శుక్ల పక్షం',
        'Krsnapaksa': 'కృష్ణ పక్షం'
    },
    'english': {
        'Suklapaksa': 'Sukla Paksha',
        'Krsnapaksa': 'Krsna Paksha'
    }
}

# Adhimasa prefix in different languages
ADHIMASA_PREFIX: Dict[str, str] = {
    'telugu': 'అధిక-',
    'english': 'Adhika-'
}

# Jovian year names (60-year cycle) in different languages
JOVIAN_YEAR_NAMES: Dict[str, Dict[int, str]] = {
    'telugu': {
        0: 'క్షయ(60)',
        1: 'ప్రభవ(1)',
        2: 'విభవ(2)',
        3: 'శుక్ల(3)',
        4: 'ప్రమోద(4)',
        5: 'ప్రజాపతి(5)',
        6: 'అంగిరస(6)',
        7: 'శ్రీముఖ(7)',
        8: 'భవ(8)',
        9: 'యువన(9)',
        10: 'ధాతృ(10)',
        11: 'ఈశ్వర(11)',
        12: 'బహుధాన్య(12)',
        13: 'ప్రమాథి(13)',
        14: 'విక్రమ(14)',
        15: 'వృష(15)',
        16: 'చిత్రభాను(16)',
        17: 'సుభాను(17)',
        18: 'తారణ(18)',
        19: 'పార్థివ(19)',
        20: 'వ్యయ(20)',
        21: 'సర్వజిత్(21)',
        22: 'సర్వధారి(22)',
        23: 'విరోధి(23)',
        24: 'వికృత(24)',
        25: 'ఖర(25)',
        26: 'నందన(26)',
        27: 'విజయ(27)',
        28: 'జయ(28)',
        29: 'మన్మథ(29)',
        30: 'దుర్ముఖ(30)',
        31: 'హేమలంబ(31)',
        32: 'విలంబి(32)',
        33: 'వికారి(33)',
        34: 'శార్వరి(34)',
        35: 'ప్లవ(35)',
        36: 'శుభకృత్(36)',
        37: 'శోభన(37)',
        38: 'క్రోధి(38)',
        39: 'విశ్వావసు(39)',
        40: 'పరాభవ(40)',
        41: 'ప్లవంగ(41)',
        42: 'కీలక(42)',
        43: 'సౌమ్య(43)',
        44: 'సాధారణ(44)',
        45: 'విరోధకృత్(45)',
        46: 'పరిధావి(46)',
        47: 'ప్రమాది(47)',
        48: 'ఆనంద(48)',
        49: 'రాక్షస(49)',
        50: 'అనల(50)',
        51: 'పింగళ(51)',
        52: 'కాలయుక్త(52)',
        53: 'సిద్ధార్థి(53)',
        54: 'రౌద్ర(54)',
        55: 'దుర్మతి(55)',
        56: 'దుందుభి(56)',
        57: 'రుధిరోద్గారి(57)',
        58: 'రక్తాక్ష(58)',
        59: 'క్రోధన(59)'
    },
    'english': {
        0: 'Ksaya(60)',
        1: 'Prabhava(1)',
        2: 'Vibhava(2)',
        3: 'Sukla(3)',
        4: 'Pramoda(4)',
        5: 'Prajapati(5)',
        6: 'Angiras(6)',
        7: 'Srimukha(7)',
        8: 'Bhava(8)',
        9: 'Yuvan(9)',
        10: 'Dhatr(10)',
        11: 'Isvara(11)',
        12: 'Bahudhanya(12)',
        13: 'Pramathin(13)',
        14: 'Vikrama(14)',
        15: 'Vrsa(15)',
        16: 'Citrabhanu(16)',
        17: 'Subhanu(17)',
        18: 'Tarana(18)',
        19: 'Parthiva(19)',
        20: 'Vyaya(20)',
        21: 'Sarvajit(21)',
        22: 'Sarvadharin(22)',
        23: 'Virodhin(23)',
        24: 'Vikrta(24)',
        25: 'Khara(25)',
        26: 'Nandana(26)',
        27: 'Vijaya(27)',
        28: 'Jaya(28)',
        29: 'Manmatha(29)',
        30: 'Durmukha(30)',
        31: 'Hemalamba(31)',
        32: 'Vilambin(32)',
        33: 'Vikarin(33)',
        34: 'Sarvari(34)',
        35: 'Plava(35)',
        36: 'Subhakrt(36)',
        37: 'Sobhana(37)',
        38: 'Krodhin(38)',
        39: 'Visvavasu(39)',
        40: 'Parabhava(40)',
        41: 'Plavanga(41)',
        42: 'Kilaka(42)',
        43: 'Saumya(43)',
        44: 'Sadharana(44)',
        45: 'Virodhakrt(45)',
        46: 'Paridhavin(46)',
        47: 'Pramadin(47)',
        48: 'Ananda(48)',
        49: 'Raksasa(49)',
        50: 'Anala(50)',
        51: 'Pingala(51)',
        52: 'Kalayukta(52)',
        53: 'Siddharthin(53)',
        54: 'Raudra(54)',
        55: 'Durmati(55)',
        56: 'Dundubhi(56)',
        57: 'Rudhirodgarin(57)',
        58: 'Raktaksa(58)',
        59: 'Krodhana(59)'
    }
}


# Helper functions to get names
def get_weekday_name(weekday_index: int, language: str = 'telugu') -> str:
    """Get weekday name by index and language."""
    lang_names = WEEKDAY_NAMES.get(language, WEEKDAY_NAMES['english'])
    return lang_names.get(weekday_index, '')


def get_masa_name(masa_num: int, language: str = 'telugu') -> str:
    """Get lunar month name by number and language."""
    lang_names = MASA_NAMES.get(language, MASA_NAMES['english'])
    return lang_names.get(masa_num, '')


def get_saura_masa_name(masa_num: int, language: str = 'telugu') -> str:
    """Get solar month name by number and language."""
    lang_names = SAURA_MASA_NAMES.get(language, SAURA_MASA_NAMES['english'])
    return lang_names.get(masa_num, '')


def get_tithi_name(tithi_day: int, paksa: str, language: str = 'telugu') -> str:
    """Get tithi name by day, paksha, and language."""
    # Handle special case for tithi 15
    if tithi_day == 15:
        tithi_15_lang = TITHI_15_NAMES.get(language, TITHI_15_NAMES['english'])
        return tithi_15_lang.get(paksa, '')
    
    # For tithi 1-14
    lang_names = TITHI_NAMES.get(language, TITHI_NAMES['english'])
    return lang_names.get(tithi_day, '')


def get_paksha_name(paksa: str, language: str = 'telugu') -> str:
    """Get paksha name by key and language."""
    lang_names = PAKSHA_NAMES.get(language, PAKSHA_NAMES['english'])
    return lang_names.get(paksa, paksa)

def _get_karana_name_math(tithi_value: float, is_second_half: bool, language: str = 'telugu') -> str:
    """
    Mathematically derive Karana name from Tithi index without heavy recalculation.

    Logic:
    - There are 60 half-tithis (Karanas) in a lunar month (30 Tithis * 2).
    - Karana Index = floor(Tithi * 2) -> returns 0 to 59.

    Mapping:
    - 0       : Kimstughna (Fixed)
    - 1 to 56 : Cycle of 7 Movable Karanas (Bava...Vishti) repeating 8 times.
    - 57      : Shakuni (Fixed)
    - 58      : Chatushpada (Fixed)
    - 59      : Naga (Fixed)
    """
    # Calculate absolute Karana index (0-59)
    # If we are in the 2nd half, we add 0.5 to the tithi integer part effectively
    tithi_int = int(tithi_value)
    karana_idx = (tithi_int * 2) + (1 if is_second_half else 0)

    # Normalize just in case of slight overflow (though rare 30.0)
    karana_idx = karana_idx % 60

    # Get names dictionary
    karana_names = KARANA_NAMES.get(language, KARANA_NAMES['english'])

    # Determine specific Karana ID based on Surya Siddhanta logic
    if karana_idx == 0:
        kid = 0  # Kimstughna
    elif 1 <= karana_idx <= 56:
        # The movable cycle is 1-7.
        # (karana_idx - 1) % 7 gives 0-6. Add 1 to map to your specific IDs if needed.
        # Assuming your KARANA_NAMES dict keys are:
        # 0: Kimstughna, 1: Bava, 2: Balava ... 7: Vishti, 8: Shakuni...

        # Map 1..56 to 1..7
        rem = (karana_idx - 1) % 7
        kid = rem + 1  # 1=Bava ... 7=Vishti
    elif karana_idx == 57:
        kid = 8  # Shakuni
    elif karana_idx == 58:
        kid = 9  # Chatushpada
    elif karana_idx == 59:
        kid = 10  # Naga
    else:
        return ""

    return karana_names.get(kid, '')

def get_karana_name(tithi: float, language: str = 'telugu') -> str:
    """
    Get karana name from tithi value.

    This function now uses _get_karana_name_math internally for better consistency.
    The fractional part of the tithi determines which half we're in.
    """
    # Determine which half of the tithi we're in
    fractional_part = tithi % 1.0
    is_second_half = fractional_part >= 0.5

    # Use the math-based function
    return _get_karana_name_math(tithi, is_second_half, language)


def get_yoga_name(tslong: float, tllong: float, language: str = 'telugu') -> str:
    """Get yoga name from sun and moon longitudes."""
    from panchanga.core.math_utils import MathUtils
    
    yoga1 = MathUtils.zero360(tslong + tllong)
    yoga = MathUtils.trunc(yoga1 * 27 / 360)
    yoga_names = YOGA_NAMES.get(language, YOGA_NAMES['english'])
    return yoga_names.get(yoga, '')


def get_nakshatra_name(tllong: float, language: str = 'telugu') -> str:
    """Get nakshatra name from moon longitude."""
    from panchanga.core.math_utils import MathUtils
    
    nakshatra_index = MathUtils.trunc(tllong * 27 / 360)
    nakshatra_names = NAKSHATRA_NAMES.get(language, NAKSHATRA_NAMES['english'])
    return nakshatra_names.get(nakshatra_index, '')


def get_jovian_year_name(year_kali: int, language: str = 'telugu') -> str:
    """Get Jovian year name (North Indian) from Kali year."""
    from panchanga.core.math_utils import MathUtils
    
    jovian_year = (MathUtils.trunc((year_kali * 211 - 108) / 18000) + year_kali + 27) % 60
    lang_names = JOVIAN_YEAR_NAMES.get(language, JOVIAN_YEAR_NAMES['english'])
    return lang_names.get(jovian_year, '')


def get_jovian_year_name_south(year_kali: int, language: str = 'telugu') -> str:
    """Get Jovian year name (South Indian) from Kali year."""
    if year_kali < 4009:
        jovian_year = year_kali
    else:
        jovian_year = (year_kali - 14) % 60
    return get_jovian_year_name(jovian_year, language)


def get_adhimasa_prefix(language: str = 'telugu') -> str:
    """Get adhimasa prefix for the given language."""
    return ADHIMASA_PREFIX.get(language, ADHIMASA_PREFIX['english'])
