data "external_schema" "sqlalchemy" {
    program = [
        "uv",
        "run",
        "model-loader.py"
    ]
}

env "sqlalchemy" {
    src = data.external_schema.sqlalchemy.url
    dev = "docker://postgres/16/dev?search_path=public"
    migration {
        dir = "file://migrations"
    }
    format {
        migrate {
           diff = "{{ sql . \"  \" }}"
        }
    }
}