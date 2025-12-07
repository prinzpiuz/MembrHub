from src.accounts.models import Account


DEFAULT_ADDRESS_FORMAT = (
    "{name}\n"
    "{address_line_1}\n"
    "{address_line_2}\n"
    "{city}, {state} {postal_code}\n"
    "{country}"
)

COUNTRY_ADDRESS_FORMATS = {
    "US": "{name}\n{address_line_1}\n{address_line_2}\n{city}, {state} {postal_code}",
    "USA": "{name}\n{address_line_1}\n{address_line_2}\n{city}, {state} {postal_code}",
    "UK": "{name}\n{address_line_1}\n{address_line_2}\n{city}\n{postal_code}",
    "GB": "{name}\n{address_line_1}\n{address_line_2}\n{city}\n{postal_code}",
    "IN": "{name}\n{address_line_1}\n{address_line_2}\n{city} - {postal_code}\n{state}",
    "INDIA": "{name}\n{address_line_1}\n{address_line_2}\n{city} - {postal_code}\n{state}",
    "DE": "{name}\n{address_line_1}\n{address_line_2}\n{postal_code} {city}",
    "GERMANY": "{name}\n{address_line_1}\n{address_line_2}\n{postal_code} {city}",
    "FR": "{name}\n{address_line_1}\n{address_line_2}\n{postal_code} {city}",
    "FRANCE": "{name}\n{address_line_1}\n{address_line_2}\n{postal_code} {city}",
    "AU": "{name}\n{address_line_1}\n{address_line_2}\n{city} {state} {postal_code}",
    "AUSTRALIA": "{name}\n{address_line_1}\n{address_line_2}\n{city} {state} {postal_code}",
    "CA": "{name}\n{address_line_1}\n{address_line_2}\n{city} {state} {postal_code}",
    "CANADA": "{name}\n{address_line_1}\n{address_line_2}\n{city} {state} {postal_code}",
}


def format_address(
    account: Account,
    format_template: str | None = None,
) -> str:
    if not account.has_address:
        return ""

    if format_template is None:
        country = (account.country or "").upper()
        format_template = COUNTRY_ADDRESS_FORMATS.get(country, DEFAULT_ADDRESS_FORMAT)

    name = account.full_name

    formatted = format_template.format(
        name=name,
        address_line_1=account.address_line_1 or "",
        address_line_2=account.address_line_2 or "",
        city=account.city or "",
        state=account.state or "",
        postal_code=account.postal_code or "",
        country=account.country or "",
    )

    lines = [line.strip() for line in formatted.split("\n") if line.strip()]
    cleaned_lines = []
    for line in lines:
        line = line.strip(" ,.-")
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def format_address_single_line(
    account: Account,
    separator: str = ", ",
) -> str:
    parts = []

    if account.full_name:
        parts.append(account.full_name)
    if account.address_line_1:
        parts.append(account.address_line_1)
    if account.address_line_2:
        parts.append(account.address_line_2)
    if account.city:
        parts.append(account.city)
    if account.state:
        parts.append(account.state)
    if account.postal_code:
        parts.append(account.postal_code)
    if account.country:
        parts.append(account.country)

    return separator.join(parts)
