from backend.db import get_connection


def get_cancer_trends():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    years.year AS year,
                    i.incidence_rate,
                    m.mortality_rate
                FROM
                    (
                        SELECT DISTINCT year FROM melanoma_incidence
                        UNION
                        SELECT DISTINCT year FROM melanoma_mortality
                    ) AS years
                LEFT JOIN
                    (
                        SELECT
                            year,
                            AVG(age_specific_rate) AS incidence_rate
                        FROM melanoma_incidence
                        GROUP BY year
                    ) AS i
                    ON years.year = i.year
                LEFT JOIN
                    (
                        SELECT
                            year,
                            AVG(age_specific_rate) AS mortality_rate
                        FROM melanoma_mortality
                        GROUP BY year
                    ) AS m
                    ON years.year = m.year
                ORDER BY years.year;
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_cancer_age_groups():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    age_group,
                    AVG(age_specific_rate) AS incidence_rate
                FROM melanoma_incidence
                WHERE age_group IS NOT NULL
                GROUP BY age_group
                ORDER BY age_group;
                """
            )
            return cur.fetchall()
    finally:
        conn.close()