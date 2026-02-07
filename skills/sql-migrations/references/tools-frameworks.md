# Migration Tools & Frameworks

## Liquibase

Version control for databases.

```xml
<!-- liquibase/changelog/db.changelog-master.xml -->
<databaseChangeLog>
  <changeSet id="1" author="john">
    <createTable tableName="users">
      <column name="id" type="SERIAL" autoIncrement="true">
        <constraints primaryKey="true"/>
      </column>
      <column name="name" type="VARCHAR(255)"/>
    </createTable>
  </changeSet>

  <changeSet id="2" author="jane">
    <renameColumn tableName="users" oldColumnName="name" newColumnName="full_name"/>
  </changeSet>
</databaseChangeLog>
```

## Flyway

Simple, powerful migrations.

```bash
# Install
brew install flyway

# Create migration
touch migrations/V1__Create_users_table.sql

# Run migrations
flyway migrate

# Validate
flyway validate
```

## Django Migrations (Python)

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show status
python manage.py showmigrations

# Revert
python manage.py migrate app_name 0001
```

## Alembic (Python)

```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply
alembic upgrade head

# Downgrade
alembic downgrade -1
```
