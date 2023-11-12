

# category_main_cb
# 'projects' don't have a number
property_codes = {'apartment': 1, 'house': 2,
                  'parcel': 3,  'commercial': 4,  'other': 5}
property_codes_names = {1: 'apartment', 2: 'house',
                        3: 'parcel',  4: 'commercial',  5: 'other'}

# category_type_cb
deal_codes = {'sell': 1, 'rent': 2,  'auction': 3, 'shares': 4}
deal_codes_names = {1: 'sell', 2: 'rent',  3: 'auction', 4: 'shares'}


category_type_cb_detail = {0: 'vse', 1: 'prodej', 2: 'pronajem',  3: 'drazby'}
category_main_cb_detail = {0: 'vse', 1: 'byt', 2: 'dum',
                           3: 'pozemek',  4: 'komercni',  5: 'ostatni'}
category_sub_cb_detail = {
    2: "1+kk",
    3: "1+1",
    4: "2+kk",
    5: "2+1",
    6: "3+kk",
    7: "3+1",
    8: "4+kk",
    9: "4+1",
    10: "5+kk",
    11: "5+1",
    12: "6-a-vice",
    16: "atypicky",
    47: "pokoj",
    37: "rodinny",
    39: "vila",
    43: "chalupa",
    33: "chata",
    35: "pamatka",
    40: "na-klic",
    44: "zemedelska-usedlost",
    19: "bydleni",
    18: "komercni",
    20: "pole",
    22: "louka",
    21: "les",
    46: "rybnik",
    48: "sady-vinice",
    23: "zahrada",
    24: "ostatni-pozemky",
    25: "kancelare",
    26: "sklad",
    27: "vyrobni-prostor",
    28: "obchodni-prostor",
    29: "ubytovani",
    30: "restaurace",
    31: "zemedelsky",
    38: "cinzovni-dum",
    49: "virtualni-kancelar",
    32: "ostatni-komercni-prostory",
    34: "garaz",
    52: "garazove-stani",
    50: "vinny-sklep",
    51: "pudni-prostor",
    53: "mobilni-domek",
    36: "jine-nemovitosti"
}

default = 'undefined'


def get_detail_url_from_seo_object(seo_object, id):
    res = 'www.sreality.cz/detail/'

    if seo_object['category_type_cb']:
        res += category_type_cb_detail.get(
            int(seo_object['category_type_cb']), default) + '/'
    if seo_object['category_main_cb']:
        res += category_main_cb_detail.get(
            int(seo_object['category_type_cb']), default) + '/'
    if seo_object['category_sub_cb']:
        res += category_sub_cb_detail.get(
            int(seo_object['category_sub_cb']), default) + '/'
    if seo_object['locality']:
        res += seo_object['locality'] + '/'
    return res + id


def get_catalog_uris(deal, property_type, count, per_page=100):
    return [f'https://www.sreality.cz/api/cs/v2/estates?category_main_cb={property_codes[property_type]}&category_type_cb={deal_codes[deal]}&per_page={per_page}&page={x}' for x in range(count//per_page + 1)]


locality_region_id =   {1: "jihocesky-kraj",
                        2: "plzensky-kraj",
                        3: "karlovarsky-kraj",
                        4: "ustecky-kraj",
                        5: "liberecky-kraj",
                        6: "kralovehradecky-kraj",
                        7: "pardubicky-kraj",
                        8: "olomoucky-kraj",
                        9: "zlinsky-kraj",
                        10: "praha",
                        11: "stredocesky-kraj",
                        12: "moravskoslezsky-kraj",
                        13: "vysocina-kraj",
                        14: "jihomoravsky-kraj"}

locality_district_id = {1: "ceske-budejovice",
                        2: "cesky-krumlov",
                        3: "jindrichuv-hradec",
                        4: "pisek",
                        5: "prachatice",
                        6: "strakonice",
                        7: "tabor",
                        71: "blansko",
                        74: "breclav",
                        72: "brno",
                        73: "brno-venkov",
                        75: "hodonin",
                        76: "vyskov",
                        77: "znojmo",
                        9: "cheb",
                        10: "karlovy-vary",
                        16: "sokolov",
                        28: "hradec-kralove",
                        30: "jicin",
                        31: "nachod",
                        33: "rychnov-nad-kneznou",
                        36: "trutnov",
                        18: "ceska-lipa",
                        21: "jablonec-nad-nisou",
                        22: "liberec",
                        34: "semily",
                        60: "bruntal",
                        61: "frydek-mistek",
                        62: "karvina",
                        63: "novy-jicin",
                        64: "opava",
                        65: "ostrava",
                        46: "jesenik",
                        42: "olomouc",
                        43: "prerov",
                        40: "prostejov",
                        44: "sumperk",
                        29: "chrudim",
                        32: "pardubice",
                        35: "svitavy",
                        37: "usti-nad-orlici",
                        8: "domazlice",
                        11: "klatovy",
                        13: "plzen-jih",
                        12: "plzen",
                        14: "plzen-sever",
                        15: "rokycany",
                        17: "tachov",
                        5010: "praha-10",
                        5001: "praha-1",
                        5002: "praha-2",
                        5003: "praha-3",
                        5004: "praha-4",
                        5005: "praha-5",
                        5006: "praha-6",
                        5007: "praha-7",
                        5008: "praha-8",
                        5009: "praha-9",
                        48: "benesov",
                        49: "beroun",
                        50: "kladno",
                        51: "kolin",
                        52: "kutna-hora",
                        54: "melnik",
                        53: "mlada-boleslav",
                        55: "nymburk",
                        56: "praha-vychod",
                        57: "praha-zapad",
                        58: "pribram",
                        59: "rakovnik",
                        20: "chomutov",
                        19: "decin",
                        23: "litomerice",
                        24: "louny",
                        25: "most",
                        26: "teplice",
                        27: "usti-nad-labem",
                        66: "havlickuv-brod",
                        67: "jihlava",
                        68: "pelhrimov",
                        69: "trebic",
                        70: "zdar-nad-sazavou",
                        39: "kromeriz",
                        41: "uherske-hradiste",
                        45: "vsetin",
                        38: "zlin"}
