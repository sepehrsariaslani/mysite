from mysite.www.controllers.sofa_details import _normalize_name
from mysite.www.sofas import get_nested_sofa_products

url_clean = _normalize_name('اورamان')
output = []
output.append('url_clean: ' + repr(url_clean))

sofa_hints = ('مبل', 'کاناپه', 'ال', 'اکسنت')
has_sofa_hint = any(h in url_clean for h in sofa_hints)
output.append('has_sofa_hint: ' + str(has_sofa_hint))
output.append('len split: ' + str(len(url_clean.split())))

all_models = get_nested_sofa_products('فروش')
found = False
for model in all_models:
    if 'اورامان' in model.get('sofa_model_name', ''):
        output.append('Found model: ' + model['sofa_model_name'])
        for mod in model.get('sofa_modules', []):
            mod_clean = _normalize_name(mod.get('sofa_module_name', ''))
            for item in mod.get('sofa_module_items', []):
                item_clean = _normalize_name(item.get('item_name', ''))
                is_exact = item_clean == url_clean or mod_clean == url_clean
                output.append('  item=' + repr(item_clean) + ' mod=' + repr(mod_clean) + ' exact=' + str(is_exact))
                if is_exact:
                    found = True
        break

output.append('Found exact match: ' + str(found))
print('\n'.join(output))
