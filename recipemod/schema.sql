DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username text NOT NULL,
    password text NOT NULL
);

CREATE UNIQUE INDEX users_pkey ON users(id int4_ops);

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    description text,
    user_id integer REFERENCES users(id),
    created timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated timestamp without time zone,
    image_url text,
    url text,
    yield text,
    authors jsonb,
    ingredients jsonb,
    instructions jsonb,
    times jsonb,
    category jsonb,
    cuisine jsonb,
    keywords jsonb,
    ratings jsonb,
    video jsonb,
    reviews jsonb
);

CREATE UNIQUE INDEX recipes_pkey ON recipes(id int4_ops);

CREATE TABLE modifications (
    id SERIAL PRIMARY KEY,
    recipe_id integer REFERENCES recipes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    changed_fields jsonb,
    meta jsonb,
    created timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX modifications_pkey ON modifications(id int4_ops);
CREATE INDEX modifications_recipe_id_idx ON modifications(recipe_id int4_ops);