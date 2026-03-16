DROP TABLE IF EXISTS melanoma_incidence;
DROP TABLE IF EXISTS melanoma_mortality;
DROP TABLE IF EXISTS melanoma_state_incidence;

CREATE TABLE melanoma_incidence (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    sex TEXT NOT NULL,
    age_group TEXT NOT NULL,
    age_specific_rate NUMERIC
);

CREATE TABLE melanoma_mortality (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    sex TEXT NOT NULL,
    age_group TEXT NOT NULL,
    age_specific_rate NUMERIC
);

CREATE TABLE melanoma_state_incidence (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    state TEXT NOT NULL,
    cases INTEGER,
    age_standardised_rate NUMERIC
);