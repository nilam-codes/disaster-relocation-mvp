import sqlite3


def get_connection():
    connection = sqlite3.connect("database/disaster.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def add_village(
    village_id,
    village_name,
    district,
    block,
    subdistrict,
    latitude,
    longitude,
    population,
    households,
    children_0_6,
    male_population,
    female_population,
    illiterate_population,
    sc_population,
    st_population
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO villages (
            village_id,
            village_name,
            district,
            block,
            subdistrict,
            latitude,
            longitude,
            population,
            households,
            children_0_6,
            male_population,
            female_population,
            illiterate_population,
            sc_population,
            st_population
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        village_id,
        village_name,
        district,
        block,
        subdistrict,
        latitude,
        longitude,
        population,
        households,
        children_0_6,
        male_population,
        female_population,
        illiterate_population,
        sc_population,
        st_population
    ))

    connection.commit()
    connection.close()

    print("Village added successfully!")


def get_all_villages():
    connection = get_connection()

    villages = connection.execute("""
        SELECT *
        FROM villages
    """).fetchall()

    connection.close()

    return villages


def get_village_by_id(village_id):
    connection = get_connection()

    village = connection.execute("""
        SELECT *
        FROM villages
        WHERE village_id = ?
    """, (village_id,)).fetchone()

    connection.close()

    return village


def add_hazard(
    hazard_id,
    village_id,
    landslide_count,
    rainfall_exposure,
    river_flood_exposure,
    slope,
    hazard_score
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO hazards (
            hazard_id,
            village_id,
            landslide_count,
            rainfall_exposure,
            river_flood_exposure,
            slope,
            hazard_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        hazard_id,
        village_id,
        landslide_count,
        rainfall_exposure,
        river_flood_exposure,
        slope,
        hazard_score
    ))

    connection.commit()
    connection.close()

    print("Hazard added successfully!")


def get_hazards_by_village(village_id):
    connection = get_connection()

    hazards = connection.execute("""
        SELECT *
        FROM hazards
        WHERE village_id = ?
    """, (village_id,)).fetchall()

    connection.close()

    return hazards


def add_risk_assessment(
    risk_id,
    village_id,
    risk_score,
    risk_level,
    relocation_priority,
    assessment_date
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO risk_assessment (
            risk_id,
            village_id,
            risk_score,
            risk_level,
            relocation_priority,
            assessment_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        risk_id,
        village_id,
        risk_score,
        risk_level,
        relocation_priority,
        assessment_date
    ))

    connection.commit()
    connection.close()

    print("Risk assessment added successfully!")


def get_risk_assessment_by_village(village_id):
    connection = get_connection()

    risk_assessment = connection.execute("""
        SELECT *
        FROM risk_assessment
        WHERE village_id = ?
    """, (village_id,)).fetchall()

    connection.close()

    return risk_assessment


def add_relocation_site(
    site_id,
    site_name,
    latitude,
    longitude,
    available_area,
    capacity,
    accessibility_score,
    site_risk_score,
    suitability_score
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO relocation_sites (
            site_id,
            site_name,
            latitude,
            longitude,
            available_area,
            capacity,
            accessibility_score,
            site_risk_score,
            suitability_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        site_id,
        site_name,
        latitude,
        longitude,
        available_area,
        capacity,
        accessibility_score,
        site_risk_score,
        suitability_score
    ))

    connection.commit()
    connection.close()

    print("Relocation site added successfully!")


def get_all_relocation_sites():
    connection = get_connection()

    sites = connection.execute("""
        SELECT *
        FROM relocation_sites
    """).fetchall()

    connection.close()

    return sites


def add_relocation_assignment(
    assignment_id,
    village_id,
    site_id,
    people_to_relocate,
    distance,
    allocation_status
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO relocation_assignments (
            assignment_id,
            village_id,
            site_id,
            people_to_relocate,
            distance,
            allocation_status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        assignment_id,
        village_id,
        site_id,
        people_to_relocate,
        distance,
        allocation_status
    ))

    connection.commit()
    connection.close()

    print("Relocation assignment added successfully!")


def get_all_relocation_assignments():
    connection = get_connection()

    assignments = connection.execute("""
        SELECT *
        FROM relocation_assignments
    """).fetchall()

    connection.close()

    return assignments


def get_village_risk_report():
    connection = get_connection()

    report = connection.execute("""
        SELECT
            v.village_id,
            v.village_name,
            v.district,
            h.hazard_score,
            r.risk_score,
            r.risk_level,
            r.relocation_priority
        FROM villages v
        LEFT JOIN hazards h
            ON v.village_id = h.village_id
        LEFT JOIN risk_assessment r
            ON v.village_id = r.village_id
        ORDER BY r.risk_score DESC
    """).fetchall()

    connection.close()

    return report


def get_relocation_report():
    connection = get_connection()

    report = connection.execute("""
        SELECT
            v.village_id,
            v.village_name,
            r.risk_score,
            r.risk_level,
            s.site_name,
            a.people_to_relocate,
            a.distance,
            a.allocation_status
        FROM relocation_assignments a
        JOIN villages v
            ON a.village_id = v.village_id
        JOIN relocation_sites s
            ON a.site_id = s.site_id
        LEFT JOIN risk_assessment r
            ON v.village_id = r.village_id
        ORDER BY r.risk_score DESC
    """).fetchall()

    connection.close()

    return report


if __name__ == "__main__":
    print("Database functions file is working!")