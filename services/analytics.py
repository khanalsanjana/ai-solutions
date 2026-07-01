from models import Inquiry


def inquiry_summary():
    total = Inquiry.query.count()
    recent = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(5).all()
    source_countries = [inquiry.country or "Unknown" for inquiry in Inquiry.query.all()]
    country_counts = {}
    for country in source_countries:
        country_counts[country] = country_counts.get(country, 0) + 1

    return {
        "total": total,
        "recent": recent,
        "country_counts": country_counts,
    }
