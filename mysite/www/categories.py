import frappe

no_cache = 1

def get_context(context):
    context.boot = get_boot_data()
    context.safe_render = 0
    return context

def get_boot_data():
    # Hardcoded categories for now, matching the requested layout
    # In a real scenario, these could be fetched from Item Group
    categories = [
        {
            "id": "furniture",
            "name": "مبلمان راحتی",
            "count": "۱۲۴ محصول",
            "tag": "پرفروش‌ترین",
            "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "featured": True,
            "route": "sofas"
        },
        {
            "id": "open-chairs",
            "name": "صندلی‌های اپن",
            "count": "۴۵ محصول",
            "tag": "جدید",
            "image": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=600",
            "route": "barstools"
        },
        {
            "id": "dining-chairs",
            "name": "صندلی‌های ناهارخوری",
            "count": "۴۴ محصول",
            "image": "https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600",
            "route": "dining-chairs"
        },
        {
            "id": "tables",
            "name": "میز ناهارخوری",
            "count": "۵۶ محصول",
            "image": "https://images.unsplash.com/photo-1611269154421-4e27233ac5c7?w=500",
            "route": "tables"
        },
        {
            "id": "coffee-tables",
            "name": "میز جلومبلی و عسلی",
            "count": "۳۴ محصول",
            "image": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500",
            "route": "coffee-tables"
        },
        {
            "id": "office",
            "name": "صندلی اداری",
            "count": "۶۷ محصول",
            "tag": "اداری",
            "image": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=500",
            "route": "office"
        },
        {
            "id": "benches",
            "name": "نیمکت‌ها",
            "count": "۱۲ محصول",
            "image": "https://images.unsplash.com/photo-1595514535311-665d95368307?w=500",
            "route": "benches"
        },
        {
            "id": "beds",
            "name": "سرویس خواب",
            "count": "۱۸ محصول",
            "image": "https://images.unsplash.com/photo-1505691938895-1758d7eaa511?w=500",
            "route": "beds"
        },
        {
            "id": "accessories",
            "name": "کوسن و تشکچه",
            "count": "۳۸ محصول",
            "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500",
            "route": "cushions"
        },
        {
            "id": "fabrics",
            "name": "پارچه‌ها",
            "count": "۴۶۰+ رنگ",
            "tag": "کالیته",
            "image": "https://images.unsplash.com/photo-1616047006789-b7af0fba0323?w=700",
            "route": "fabrics",
            "type": "accessories"
        }
    ]
    
    return {
        "Categories": categories
    }
