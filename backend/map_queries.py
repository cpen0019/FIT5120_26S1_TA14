from backend.db import get_connection


STATE_CODE_MAP = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "SA": "South Australia",
    "WA": "Western Australia",
    "TAS": "Tasmania",
    "NT": "Northern Territory",
    "ACT": "Australian Capital Territory",
}


def normalize_state_name(state_value: str) -> str:
    if not state_value:
        return state_value

    cleaned = state_value.strip()
    upper_value = cleaned.upper()

    if upper_value in STATE_CODE_MAP:
        return STATE_CODE_MAP[upper_value]

    return cleaned


def get_state_stats():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    state,
                    ROUND(AVG(age_standardised_rate)::numeric, 2) AS avg_incidence_rate,
                    SUM(cases) AS total_cases
                FROM melanoma_state_incidence
                WHERE state <> 'Australia'
                GROUP BY state
                ORDER BY state;
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_state_details(state_code: str):
    state_name = normalize_state_name(state_code)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    state,
                    year,
                    SUM(cases) AS cases,
                    ROUND(AVG(age_standardised_rate)::numeric, 2) AS age_standardised_rate
                FROM melanoma_state_incidence
                WHERE state = %s
                GROUP BY state, year
                ORDER BY year;
                """,
                (state_name,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_state_comparison():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH latest_year AS (
                    SELECT MAX(year) AS year
                    FROM melanoma_state_incidence
                    WHERE state <> 'Australia'
                )
                SELECT
                    m.state,
                    m.year,
                    SUM(m.cases) AS cases,
                    ROUND(AVG(m.age_standardised_rate)::numeric, 2) AS age_standardised_rate
                FROM melanoma_state_incidence m
                JOIN latest_year y
                  ON m.year = y.year
                WHERE m.state <> 'Australia'
                GROUP BY m.state, m.year
                ORDER BY age_standardised_rate DESC, m.state;
                """
            )
            return cur.fetchall()
    finally:
        conn.close()