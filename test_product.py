import frappe
from mysite.www.controllers.sofa_details import get_sofa_unit_details, get_sofa_collection_details

model_name = 'باکس اورامان بیضی طول ۸۰ عرض ۴۰ خودرنگ'

# Test get_sofa_unit_details
result = get_sofa_unit_details(model_name, "فروش")
if result:
    print(f"get_sofa_unit_details: FOUND, type={result.get('type')}, name={result.get('name','')[:60]}")
else:
    print("get_sofa_unit_details: NOT FOUND")

# Test get_sofa_collection_details  
result2 = get_sofa_collection_details(model_name, "فروش")
if result2:
    print(f"get_sofa_collection_details: FOUND, type={result2.get('type')}, name={result2.get('name','')[:60]}")
else:
    print("get_sofa_collection_details: NOT FOUND")
