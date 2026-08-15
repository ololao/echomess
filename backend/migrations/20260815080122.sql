-- Create enum type "userstatus"
CREATE TYPE "userstatus" AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING');
-- Create "rooms" table
CREATE TABLE "rooms" (
  "id" character varying(36) NOT NULL,
  "name" character varying(30) NOT NULL,
  "tsv" tsvector NOT NULL GENERATED ALWAYS AS (setweight(to_tsvector('english'::regconfig, (COALESCE(name, ''::character varying))::text), 'A'::"char") || setweight(to_tsvector('russian'::regconfig, (COALESCE(name, ''::character varying))::text), 'A'::"char")) STORED,
  PRIMARY KEY ("id"),
  CONSTRAINT "rooms_name_key" UNIQUE ("name")
);
-- Create "users" table
CREATE TABLE "users" (
  "id" character varying(36) NOT NULL,
  "name" character varying(10) NOT NULL,
  "email" character varying(100) NOT NULL,
  "password" character varying(255) NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "status" "userstatus" NOT NULL,
  PRIMARY KEY ("id"),
  CONSTRAINT "users_email_key" UNIQUE ("email")
);
-- Create "messages" table
CREATE TABLE "messages" (
  "id" character varying NOT NULL,
  "data" bytea NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "user_id" character varying(36) NOT NULL,
  "room_id" character varying(36) NOT NULL,
  PRIMARY KEY ("id"),
  CONSTRAINT "messages_room_id_fkey" FOREIGN KEY ("room_id") REFERENCES "rooms" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "messages_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);
