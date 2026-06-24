"""
Database Seeder — creates roles, menus, permissions, and default users.
Run with: python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from application.providers.database import SessionLocal, engine, Base
from application.repositories.user_repository import UserRepository
from application.repositories.role_repository import RoleRepository
from application.repositories.menu_repository import MenuRepository
from application.repositories.permission_repository import PermissionRepository
from application.src.models.user_model import UserRole
from application.dto.role_dto import RoleCreateDTO
from application.dto.menu_dto import MenuCreateDTO
from application.dto.permission_dto import MenuPermissionEntryDTO


MENU_DEFINITIONS = [
    {"menu_name": "Dashboard",     "menu_code": "dashboard",     "parent_menu_id": None, "route_path": "/",           "icon": "dashboard",    "display_order": 1},
    {"menu_name": "Master Data",   "menu_code": "master_data",   "parent_menu_id": None, "route_path": None,           "icon": "database",     "display_order": 2},
    {"menu_name": "Transactions",  "menu_code": "transactions",  "parent_menu_id": None, "route_path": None,           "icon": "exchange-alt", "display_order": 3},
    {"menu_name": "Reports",       "menu_code": "reports",       "parent_menu_id": None, "route_path": None,           "icon": "chart-bar",    "display_order": 4},
    {"menu_name": "Settings",      "menu_code": "settings",      "parent_menu_id": None, "route_path": None,           "icon": "cog",          "display_order": 5},
]

CHILD_MENU_DEFINITIONS = [
    {"menu_name": "Airlines",           "menu_code": "airlines",           "parent_code": "master_data", "route_path": "/airlines",      "icon": "plane",      "display_order": 1},
    {"menu_name": "Vendors",            "menu_code": "vendors",            "parent_code": "master_data", "route_path": "/vendors",       "icon": "truck",      "display_order": 2},
    {"menu_name": "Fuel Prices",        "menu_code": "fuel_prices",        "parent_code": "master_data", "route_path": "/fuel-prices",   "icon": "gas-pump",   "display_order": 3},
    {"menu_name": "Transaction Report", "menu_code": "transaction_report", "parent_code": "reports",      "route_path": "/transactions",  "icon": "chart-pie",  "display_order": 2},
    {"menu_name": "Users",              "menu_code": "users",              "parent_code": "settings",     "route_path": "/users",         "icon": "users",      "display_order": 2},
    {"menu_name": "Roles",              "menu_code": "roles",              "parent_code": "settings",     "route_path": "/roles",         "icon": "shield-alt", "display_order": 3},
    {"menu_name": "Menus",              "menu_code": "menus",              "parent_code": "settings",     "route_path": "/menus",         "icon": "bars",       "display_order": 4},
    {"menu_name": "Permissions",        "menu_code": "permissions",        "parent_code": "settings",     "route_path": "/permissions",   "icon": "lock",       "display_order": 5},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        role_repo = RoleRepository(db)
        menu_repo = MenuRepository(db)
        perm_repo = PermissionRepository(db)
        user_repo = UserRepository(db)

        # ── 1. Seed Menus ───────────────────────────────────────────────────────
        menu_code_to_id = {}
        for m in MENU_DEFINITIONS:
            existing = menu_repo.get_by_code(m["menu_code"])
            if existing:
                print(f"ℹ️   Menu '{m['menu_code']}' already exists, skipping.")
                menu_code_to_id[m["menu_code"]] = existing.id
            else:
                dto = MenuCreateDTO(**m)
                created = menu_repo.create(dto)
                menu_code_to_id[m["menu_code"]] = created.id
                print(f"✅  Menu created  →  {m['menu_code']} (id={created.id})")

        for cm in CHILD_MENU_DEFINITIONS:
            existing = menu_repo.get_by_code(cm["menu_code"])
            if existing:
                print(f"ℹ️   Menu '{cm['menu_code']}' already exists, skipping.")
                menu_code_to_id[cm["menu_code"]] = existing.id
            else:
                parent_id = menu_code_to_id[cm["parent_code"]]
                dto = MenuCreateDTO(
                    menu_name=cm["menu_name"],
                    menu_code=cm["menu_code"],
                    parent_menu_id=parent_id,
                    route_path=cm["route_path"],
                    icon=cm["icon"],
                    display_order=cm["display_order"],
                )
                created = menu_repo.create(dto)
                menu_code_to_id[cm["menu_code"]] = created.id
                print(f"✅  Menu created  →  {cm['menu_code']} (id={created.id}, parent={cm['parent_code']})")

        # ── 2. Seed Admin Role ──────────────────────────────────────────────────
        admin_role = role_repo.get_by_name("admin")
        if not admin_role:
            dto = RoleCreateDTO(role_name="admin", description="Super administrator with full system access")
            admin_role = role_repo.create(dto)
            print(f"✅  Role created  →  admin (id={admin_role.id})")
        else:
            print(f"ℹ️   Role 'admin' already exists (id={admin_role.id}), skipping.")

        # ── 3. Assign all permissions to Admin Role ─────────────────────────────
        all_menu_ids = list(menu_code_to_id.values())
        existing_perms = perm_repo.get_all_for_role(admin_role.id)
        existing_menu_ids = {p.menu_id for p in existing_perms}
        missing_menu_ids = [mid for mid in all_menu_ids if mid not in existing_menu_ids]

        if missing_menu_ids:
            entries = [
                MenuPermissionEntryDTO(
                    menu_id=mid,
                    can_view=True, can_create=True, can_edit=True, can_delete=True,
                    can_download=True, can_approve=True, can_export=True, can_print=True,
                )
                for mid in missing_menu_ids
            ]
            perm_repo.bulk_upsert(admin_role.id, entries)
            print(f"✅  Granted all permissions to admin role for {len(entries)} menu(s).")
        else:
            print(f"ℹ️   Admin role already has all menu permissions.")

        # ── 4. Seed Users & attach to admin role ────────────────────────────────
        admin_user = user_repo.get_by_username("admin")
        if not admin_user:
            admin_user = user_repo.create_user(username="admin", plain_password="admin123", role=UserRole.admin)
            print("✅  Admin user created  →  username: admin  |  password: admin123")
        else:
            print("ℹ️   Admin user already exists, skipping.")

        if admin_user.role_id is None:
            admin_user.role_id = admin_role.id
            db.commit()
            print(f"✅  Linked admin user to admin role (role_id={admin_role.id})")
        else:
            print(f"ℹ️   Admin user already linked to role_id={admin_user.role_id}")

        operator_user = user_repo.get_by_username("operator")
        if not operator_user:
            operator_user = user_repo.create_user(username="operator", plain_password="operator123", role=UserRole.operator)
            print("✅  Operator user created  →  username: operator  |  password: operator123")
        else:
            print("ℹ️   Operator user already exists, skipping.")

    finally:
        db.close()

    print("\n🚀  Seeding complete. You can now log in at POST /auth/login")


if __name__ == "__main__":
    seed()
