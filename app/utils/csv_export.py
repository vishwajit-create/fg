import csv
import io


def generate_csv(headers, rows):
    """
    Generate a CSV byte stream safe against formula injection.

    headers: list of column header strings
    rows:    iterable of dicts or lists
    returns: BytesIO ready for Flask send_file
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for row in rows:
        if isinstance(row, dict):
            safe_row = [_escape_cell(row.get(h, '')) for h in headers]
        else:
            safe_row = [_escape_cell(v) for v in row]
        writer.writerow(safe_row)

    output.seek(0)
    byte_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    byte_output.seek(0)
    return byte_output


def _escape_cell(value):
    """Prefix formula-injection trigger characters with a single quote."""
    v = str(value) if value is not None else ''
    if v and v[0] in ('=', '+', '-', '@', '\t', '\r'):
        v = "'" + v
    return v
