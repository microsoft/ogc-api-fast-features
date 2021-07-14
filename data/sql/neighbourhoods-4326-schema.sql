CREATE TABLE IF NOT EXISTS neighbourhoods (
    ID SERIAL PRIMARY KEY
 ,  name VARCHAR(100) NOT NULL UNIQUE
 ,  boundary GEOMETRY(MULTIPOLYGON) NOT NULL
)
;