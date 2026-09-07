from database_functions import (
    get_all_villages,
    get_all_relocation_sites,
    get_all_relocation_assignments
)


print("Testing database functions...")

print("Villages:", get_all_villages())
print("Relocation Sites:", get_all_relocation_sites())
print("Relocation Assignments:", get_all_relocation_assignments())

print("Database integration test completed successfully!")