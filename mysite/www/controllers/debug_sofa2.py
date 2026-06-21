from mysite.www.controllers.sofa_details import _normalize_name, get_sofa_unit_details

url = 'باكس اورامان بيضي طول ۸۰ عرض ۴۰ خودرنگ'
url_clean = _normalize_name(url)
output = []
output.append('url_clean: ' + repr(url_clean))

result = get_sofa_unit_details(url, 'فروش')
if result is None:
    output.append('Result: None')
else:
    output.append('type: ' + str(result.get('type')))
    output.append('name: ' + str(result.get('name')))
    output.append('module: ' + str(result.get('module')))
    output.append('variants: ' + str(len(result.get('variants', []))))

print('\n'.join(output))
