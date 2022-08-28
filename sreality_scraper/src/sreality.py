

# category_main_cb
# 'projects' don't have a number
property_codes = {'apartment': 1, 'house': 2,
                  'parcel': 3,  'comercial': 4,  'other': 5}
property_codes_names = {1: 'apartment', 2: 'house',
                        3: 'parcel',  4: 'comercial',  5: 'other'}

# category_type_cb
deal_codes = {'sell': 1, 'rent': 2,  'auction': 3}
deal_codes_names = {1: 'sell', 2: 'rent',  3: 'auction'}


category_type_cb_detail = {0: 'vse',1: 'prodej', 2: 'pronajem',  3: 'drazby'}
category_main_cb_detail= {0: 'vse', 1: 'byt', 2: 'dum',
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
        res += category_type_cb_detail.get(int(seo_object['category_type_cb']), default) + '/'
    if seo_object['category_main_cb']:
        res += category_main_cb_detail.get(int(seo_object['category_type_cb']), default) + '/'
    if seo_object['category_sub_cb']:
        res += category_sub_cb_detail.get(int(seo_object['category_sub_cb']), default) + '/'
    if seo_object['locality']:
        res += seo_object['locality'] + '/'
    return res + id


def get_catalog_uris(deal, property_type, count, per_page=100):
    return [f'https://www.sreality.cz/api/cs/v2/estates?category_main_cb={property_codes[property_type]}&category_type_cb={deal_codes[deal]}&locality_country_id=10001&per_page={per_page}&page={x}' for x in range(count//per_page + 1)]
