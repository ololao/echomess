-- Modify "users" table
ALTER TABLE "users" ALTER COLUMN "name" TYPE character varying(50), ALTER COLUMN "password" DROP NOT NULL, ADD COLUMN "google_id" character varying(255) NULL, ADD CONSTRAINT "users_google_id_key" UNIQUE ("google_id");
