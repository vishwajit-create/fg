import sys
import os
import psycopg2
from app import create_app
from app.extensions import db

def setup_and_migrate(supabase_uri):
    # Ensure URI starts with postgresql://
    if supabase_uri.startswith("postgres://"):
        supabase_uri = supabase_uri.replace("postgres://", "postgresql://", 1)
        
    print("=" * 60)
    print("CSFMS -> Supabase Migration Tool")
    print("=" * 60)
    
    print("\n1. Initializing tables on Supabase...")
    os.environ["DATABASE_URL"] = supabase_uri
    app = create_app("production")
    
    with app.app_context():
        db.create_all()
        print("   -> Tables created successfully in Supabase!")

    print("\n2. Importing backup data from 'supabase_import.sql'...")
    sql_file = "supabase_import.sql"
    if not os.path.exists(sql_file):
        print(f"Error: {sql_file} not found!")
        return

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    conn = psycopg2.connect(supabase_uri)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(sql_commands)
        print("   -> All data imported successfully!")
    except Exception as e:
        print(f"   -> Import error: {e}")
    finally:
        cur.close()
        conn.close()

    print("\n3. Verifying record counts in Supabase:")
    conn = psycopg2.connect(supabase_uri)
    cur = conn.cursor()
    tables = [
        "roles", "departments", "programs", "academic_years", "sections",
        "subjects", "faculty", "users", "students", "enrollments",
        "faculty_assignments", "attendance_sessions", "attendance_records",
        "institution_settings", "audit_logs"
    ]
    for t in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "public"."{t}";')
            cnt = cur.fetchone()[0]
            print(f"   * {t:22}: {cnt} rows")
        except Exception:
            pass
    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("Now update DATABASE_URL in your Render dashboard environment variables.")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_to_supabase.py <SUPABASE_DATABASE_URL>")
        print("Example:")
        print("  python import_to_supabase.py \"postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres\"")
        sys.exit(1)
    setup_and_migrate(sys.argv[1])
