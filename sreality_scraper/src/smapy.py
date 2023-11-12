import re

def get_reverse_geocode_url(lon, lat):
    return f'https://api.mapy.cz/rgeocode?lon={lon}&lat={lat}&count=0'


# Response body format:
# <?xml version="1.0" encoding="utf-8"?>
# <rgeocode label="Těšínská, Praha, Hlavní město Praha" status="200" message="Ok">
#     <item id="124797" name="Těšínská" source="stre" type="stre" x="14.418971886642606" y="50.12904336155153" />
#     <item id="115" name="Praha 8" source="quar" type="quar" x="14.45457" y="50.1243991667" />
#     <item id="14965" name="Troja" source="ward" type="ward" x="14.423425" y="50.1221472222" />
#     <item id="3468" name="Praha" source="muni" type="muni" x="14.4341412988" y="50.0835493857" />
#     <item id="47" name="Okres Hlavní město Praha" source="dist" type="dist" x="14.466000012775831" y="50.066789200167186" />
#     <item id="10" name="Hlavní město Praha" source="regi" type="regi" x="14.466" y="50.066789" />
#     <item id="112" name="Česko" source="coun" type="coun" x="15.338411" y="49.742858" />
# </rgeocode>

def parse_reverse_geocode_xml(xml):
    match = re.search(r'id="(.*)" name="(.*)" source="muni"', xml)
    if match:
        return { 
            "id": int(match.group(1)),
            "name":  match.group(2)
        }
    return None