"""Generate Riverside Dental patient FAQ PDF for demos / website download."""

from pathlib import Path

CONTENT = """Riverside Dental Group — Patient FAQ

Office hours
Monday to Friday 8:00 AM to 5:00 PM.
Saturday 9:00 AM to 1:00 PM.
Closed Sunday.

Insurance
We accept Delta Dental PPO, Cigna, MetLife, and most major PPO plans.
Bring your insurance card to your first visit.

Appointments
Call our phone number (555) 010-2200 or book online.
New patients should arrive 15 minutes early.
Same-day emergency slots are held each morning.

Location and address
Our address is 220 Maple Street, Suite 100, Riverside.

Parking
Free parking is available behind the clinic on Maple Street.

Services
We offer in-office professional teeth whitening.
We welcome families and see children age 3 and older.
We offer nitrous oxide (laughing gas) for anxious patients.
"""


def write_minimal_pdf(path: Path, text: str) -> None:
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    lines = safe.splitlines()
    parts = ["BT", "/F1 11 Tf", "50 750 Td", "14 TL"]
    for i, line in enumerate(lines):
        if i == 0:
            parts.append(f"({line}) Tj")
        else:
            parts.append("T*")
            parts.append(f"({line}) Tj")
    parts.append("ET")
    stream = "\n".join(parts).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        (
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
        ),
        f"4 0 obj<< /Length {len(stream)} >>stream\n".encode() + stream + b"\nendstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(out))
        out.extend(obj)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(
        f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(out))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    targets = [
        root / "fixtures" / "riverside" / "riverside-patient-faq.pdf",
        root / "fixtures" / "riverside" / "insurance-faq.pdf",
        root / "demo" / "riverside-patient-faq.pdf",
    ]
    for target in targets:
        write_minimal_pdf(target, CONTENT)
        print(f"Wrote {target}")
