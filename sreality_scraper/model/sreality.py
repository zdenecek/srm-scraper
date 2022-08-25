

# category_main_cb
# 'projects' don't have a number
property_codes = { 'apartment':1  , 'house':2, 'parcel':3,  'comercial':4,  'other':5  }
property_codes_names = { 1:'apartment'  , 2:'house', 3:'parcel',  4:'comercial',  5:'other'  }

# category_type_cb
deal_codes = { 'sell':1  , 'rent':2,  'auction':3  } 
deal_codes_names = { 1:'sell'  , 2:'rent',  3:'auction'  } 


def get_catalog_uris(deal, property_type, count, per_page = 100):
        return [f'https://www.sreality.cz/api/cs/v2/estates?category_main_cb={property_type}&category_type_cb={deal}&locality_country_id=10001&per_page={per_page}&page={x}' for x in range(count//per_page + 1)]