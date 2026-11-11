import os
import re

backup_dir = "render_backup_extracted/2026-11-10T20_25Z/csfms"
toc_path = os.path.join(backup_dir, "toc.dat")

with open(toc_path, "rb") as f:
    raw = f.read()

pattern = re.compile(rb'COPY\s+("[^"]+"\."([^"]+)"\s+\(([^)]+)\)\s+FROM stdin;)[^\n]*\n.*?(\d{4}\.dat)', re.DOTALL)
matches = pattern.findall(raw)

tables_info = {}
for copy_stmt, table_name, cols_str, dat_file in matches:
    t_name = table_name.decode()
    cols = [c.strip().strip('"') for c in cols_str.decode().split(",")]
    tables_info[t_name] = {
        "dat_file": dat_file.decode(),
        "cols": cols
    }

ordered_tables = [
    "roles",
    "departments",
    "programs",
    "academic_years",
    "sections",
    "subjects",
    "faculty",
    "users",
    "students",
    "enrollments",
    "faculty_assignments",
    "attendance_sessions",
    "attendance_records",
    "institution_settings",
    "audit_logs"
]

output_sql_path = "supabase_import.sql"

total_records = 0
summary = {}

with open(output_sql_path, "w", encoding="utf-8") as out:
    out.write("-- ============================================================\n")
    out.write("-- CSFMS Data Migration to Supabase\n")
    out.write("-- Source: Render PostgreSQL Backup (2026-11-10T20:25Z)\n")
    out.write("-- ============================================================\n\n")
    out.write("BEGIN;\n\n")
    out.write("-- Disable triggers & foreign keys temporarily during data restore\n")
    out.write("SET session_replication_role = 'replica';\n\n")

    # Truncate all tables first so initial seed data doesn't clash with backup data
    table_list_str = ", ".join([f'"public"."{t}"' for t in ordered_tables])
    out.write(f"-- Clear existing seed data\n")
    out.write(f"TRUNCATE TABLE {table_list_str} CASCADE;\n\n")

    for t_name in ordered_tables:
        if t_name not in tables_info:
            continue
        info = tables_info[t_name]
        dat_path = os.path.join(backup_dir, info["dat_file"])
        cols = info["cols"]
        
        with open(dat_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            
        rows = []
        for line in lines:
            line = line.rstrip("\r\n")
            if not line or line == r"\.":
                continue
            parts = line.split("\t")
            rows.append(parts)
            
        summary[t_name] = len(rows)
        total_records += len(rows)
        
        out.write(f"-- ------------------------------------------------------------\n")
        out.write(f"-- Table: {t_name} ({len(rows)} records)\n")
        out.write(f"-- ------------------------------------------------------------\n")
        
        if rows:
            col_list_str = ", ".join([f'"{c}"' for c in cols])
            for r in rows:
                val_strs = []
                for idx, v in enumerate(r):
                    col_name = cols[idx] if idx < len(cols) else ""
                    if v == r"\N":
                        val_strs.append("NULL")
                    elif v == "t":
                        val_strs.append("TRUE")
                    elif v == "f":
                        val_strs.append("FALSE")
                    elif col_name in ("id", "department_id", "program_id", "academic_year_id", "section_id", "subject_id", "faculty_id", "role_id", "student_id", "actor_user_id", "entity_id", "session_id", "marked_by", "duration_years", "semester", "credits", "attendance_edit_window_hours") and v.isdigit():
                        val_strs.append(v)
                    else:
                        escaped = v.replace("'", "''")
                        val_strs.append(f"'{escaped}'")
                out.write(f'INSERT INTO "public"."{t_name}" ({col_list_str}) VALUES ({", ".join(val_strs)});\n')
            
            # Reset sequence safely
            out.write(f"SELECT setval(pg_get_serial_sequence('\"public\".\"{t_name}\"', 'id'), COALESCE((SELECT MAX(id) FROM \"public\".\"{t_name}\"), 1), true);\n")
        out.write("\n")

    out.write("SET session_replication_role = 'origin';\n\n")
    out.write("COMMIT;\n")

print(f"Generated {output_sql_path} with {total_records} total records across {len(summary)} tables!")
